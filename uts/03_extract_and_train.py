"""Step 3 - read pixel values under your polygons, train the classifier, evaluate it.

Model: Random Forest on B04, B8A, B11 (+ NDVI and NDMI computed from them).
The train/test split is made by POLYGON, so pixels of one polygon never appear in both sets.
"""
import json
import sys

import geopandas as gpd
import joblib
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask as rio_mask
from shapely.geometry import box, mapping
from sklearn.ensemble import RandomForestClassifier

import config as C
from lulc_utils import evaluate, make_features, split_polygons, valid_pixels


def extract_pixels():
    tiles = sorted(C.TILES_DIR.glob("*.tif"))
    if not tiles:
        sys.exit(f"No tiles in {C.TILES_DIR}. Run step 2 first.")
    polys = gpd.read_file(C.SAMPLES_CLEAN).to_crs(C.CRS)
    rng = np.random.default_rng(C.SEED)
    rows = []
    for tif in tiles:
        with rasterio.open(tif) as src:
            if src.count < 3:
                sys.exit(f"{tif.name} has {src.count} bands, expected 3 (B04, B8A, B11).")
            hit = polys[polys.intersects(box(*src.bounds))]
            for _, p in hit.iterrows():
                try:
                    arr, _ = rio_mask(src, [mapping(p.geometry)], crop=True, filled=False)
                except ValueError:      # polygon does not overlap this raster
                    continue
                bands = arr[:3].reshape(3, -1)
                inside = ~np.ma.getmaskarray(bands).any(axis=0)
                vals = np.ma.getdata(bands).astype("float32")
                if src.nodata is not None and not np.isnan(src.nodata):
                    inside &= ~np.any(vals == src.nodata, axis=0)
                ok = inside & valid_pixels(vals)
                idx = np.flatnonzero(ok)
                if len(idx) == 0:
                    continue
                if len(idx) > C.MAX_PIXELS_PER_POLYGON:
                    idx = rng.choice(idx, C.MAX_PIXELS_PER_POLYGON, replace=False)
                df = make_features(vals[0, idx], vals[1, idx], vals[2, idx])
                df.insert(0, "kelas", p["kelas"])
                df.insert(0, "poly_id", p["poly_id"])
                rows.append(df)
    if not rows:
        sys.exit("No pixels extracted: polygons do not overlap the downloaded tiles.")
    return pd.concat(rows, ignore_index=True)


def main():
    pix = extract_pixels()
    pix.to_csv(C.PIXELS_CSV, index=False)
    used = pix.groupby("kelas")["poly_id"].nunique().reindex(C.CLASSES).fillna(0).astype(int)
    print("Polygons with usable pixels per class:\n", used.to_string())
    print("Pixels per class:\n", pix["kelas"].value_counts().reindex(C.CLASSES).fillna(0).astype(int).to_string())

    poly_df = pix[["poly_id", "kelas"]].drop_duplicates()
    train_ids, test_ids = split_polygons(poly_df, C.TEST_SIZE, C.SEED)
    tr = pix[pix["poly_id"].isin(train_ids)]
    te = pix[pix["poly_id"].isin(test_ids)]
    print(f"\nTrain: {len(train_ids)} polygons / {len(tr)} pixels   Test: {len(test_ids)} polygons / {len(te)} pixels")

    model = RandomForestClassifier(**C.RF_PARAMS)
    model.fit(tr[C.FEATURES], tr["kelas"])
    pred = model.predict(te[C.FEATURES])

    present = [c for c in C.CLASSES if c in set(te["kelas"]) | set(pred)]
    res = evaluate(te["kelas"], pred, present)
    res["n_polygons_train"] = len(train_ids)
    res["n_polygons_test"] = len(test_ids)
    res["n_pixels_train"] = int(len(tr))
    res["n_pixels_test"] = int(len(te))
    res["polygons_per_class"] = {k: int(v) for k, v in used.items()}
    res["pixels_per_class"] = {k: int(v) for k, v in pix["kelas"].value_counts().items()}
    res["feature_importance"] = dict(zip(C.FEATURES, map(float, model.feature_importances_)))
    res["period"] = f"{C.DATE_START} to {C.DATE_END}"

    print(f"\nOverall accuracy: {res['accuracy']:.4f}   Cohen's kappa: {res['kappa']:.4f}")
    print("\nPer-class F1 (lowest first - these classes need more / better polygons):")
    f1 = {c: res["per_class"][c]["f1-score"] for c in present}
    for c, v in sorted(f1.items(), key=lambda kv: kv[1]):
        print(f"  {c:10s} {v:.3f}")
    print("\nConfusion matrix (rows = true, columns = predicted):")
    print(pd.DataFrame(res["confusion_matrix"], index=present, columns=present).to_string())

    sig = pix.groupby("kelas")[["B04", "B8A", "B11"]].mean().reindex(C.CLASSES).dropna()
    sig.to_csv(C.SIGNATURE_CSV)
    joblib.dump({"model": model, "features": C.FEATURES}, C.MODEL_PATH)
    with open(C.METRICS_JSON, "w") as f:
        json.dump(res, f, indent=2)
    print(f"\nSaved {C.MODEL_PATH.name}, {C.METRICS_JSON.name}, {C.SIGNATURE_CSV.name}, {C.PIXELS_CSV.name} in data/")


if __name__ == "__main__":
    main()
