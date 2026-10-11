"""Step 4 - classify every tile, then digitize the result into one GeoJSON layer per class.

For each Sentinel-2 tile: predict a class map (GeoTIFF, 1-5, 0 = no data / outside East Java),
count the area per class, and convert each class to polygons (GeoJSON, EPSG:4326) for the web map.
Polygons are generalized (coarser grid, small blobs removed, simplified) so the files stay small
enough for Leaflet - see VECTOR_FACTOR, SIEVE_MIN_PIXELS, MIN_AREA_HA and SIMPLIFY_M in config.py.
"""
import json
import sys

import geopandas as gpd
import joblib
import numpy as np
import rasterio
from rasterio.features import geometry_mask, shapes, sieve
from shapely.geometry import box, shape

import config as C
from geo_utils import load_boundary_utm
from lulc_utils import make_features, valid_pixels


def predict_tile(model, features, src, boundary):
    data = src.read([1, 2, 3]).astype("float32")             # (3, h, w)
    h, w = data.shape[1:]
    flat = data.reshape(3, -1)
    ok = valid_pixels(flat)
    inside = geometry_mask([boundary], out_shape=(h, w), transform=src.transform, invert=True).ravel()
    ok &= inside
    out = np.zeros(h * w, dtype="uint8")
    idx = np.flatnonzero(ok)
    for start in range(0, len(idx), 500_000):                # predict in chunks to save memory
        sl = idx[start:start + 500_000]
        X = make_features(flat[0, sl], flat[1, sl], flat[2, sl])[features]
        out[sl] = [C.CLASS_ID[k] for k in model.predict(X)]
    return out.reshape(h, w)


def class_polygons(class_map, transform, class_id):
    """Binary class layer -> list of shapely polygons in the raster CRS (metres)."""
    f = C.VECTOR_FACTOR
    h, w = class_map.shape
    hh, ww = h // f * f, w // f * f
    binary = (class_map[:hh, :ww] == class_id).astype("uint8")
    if f > 1:                                                # majority vote per f x f block
        blocks = binary.reshape(hh // f, f, ww // f, f).sum(axis=(1, 3), dtype="uint8")
        binary = (blocks * 2 >= f * f).astype("uint8")
    t = transform * transform.scale(f, f)
    if not binary.any():
        return []
    binary = sieve(binary, size=C.SIEVE_MIN_PIXELS, connectivity=4)
    polys = []
    min_area = C.MIN_AREA_HA * 10_000
    for geom, val in shapes(binary, mask=binary.astype(bool), transform=t, connectivity=4):
        g = shape(geom)
        if g.area < min_area:
            continue
        polys.append(g.simplify(C.SIMPLIFY_M, preserve_topology=True))
    return polys


def round_coords(obj, nd=5):
    if isinstance(obj, (list, tuple)):
        if obj and isinstance(obj[0], (int, float)):
            return [round(v, nd) for v in obj]
        return [round_coords(o, nd) for o in obj]
    return obj


def main():
    tiles = sorted(C.TILES_DIR.glob("*.tif"))
    if not tiles:
        sys.exit(f"No tiles in {C.TILES_DIR}. Run step 2 first.")
    bundle = joblib.load(C.MODEL_PATH)
    model, features = bundle["model"], bundle["features"]
    boundary = load_boundary_utm()

    C.CLASS_TILES_DIR.mkdir(parents=True, exist_ok=True)
    C.GEOJSON_DIR.mkdir(parents=True, exist_ok=True)
    pixel_counts = {k: 0 for k in C.CLASSES}
    layer_polys = {k: [] for k in C.CLASSES}
    res = C.RESOLUTION

    for i, tif in enumerate(tiles, 1):
        print(f"[{i}/{len(tiles)}] {tif.name}")
        with rasterio.open(tif) as src:
            if not box(*src.bounds).intersects(boundary):
                continue
            cmap = predict_tile(model, features, src, boundary)
            profile = src.profile.copy()
            profile.update(count=1, dtype="uint8", nodata=0, compress="lzw")
            with rasterio.open(C.CLASS_TILES_DIR / f"{tif.stem}_class.tif", "w", **profile) as dst:
                dst.write(cmap, 1)
            for k in C.CLASSES:
                cid = C.CLASS_ID[k]
                pixel_counts[k] += int((cmap == cid).sum())
                layer_polys[k] += class_polygons(cmap, src.transform, cid)

    total = sum(pixel_counts.values())
    stats = {k: {"pixels": v,
                 "area_km2": round(v * res * res / 1e6, 2),
                 "percent": round(100 * v / total, 2) if total else 0.0}
             for k, v in pixel_counts.items()}
    with open(C.STATS_JSON, "w") as f:
        json.dump({"resolution_m": res, "classes": stats}, f, indent=2)

    for k in C.CLASSES:
        gdf = gpd.GeoDataFrame({"kelas": k, "area_ha": [round(g.area / 1e4, 2) for g in layer_polys[k]]},
                               geometry=layer_polys[k], crs=C.CRS).to_crs(4326)
        gj = json.loads(gdf.to_json(drop_id=True))
        for feat in gj["features"]:
            feat["geometry"]["coordinates"] = round_coords(feat["geometry"]["coordinates"])
        path = C.GEOJSON_DIR / f"{k}.geojson"
        with open(path, "w") as f:
            json.dump(gj, f, separators=(",", ":"))
        print(f"  {k:9s} {len(gdf):7d} polygons  {path.stat().st_size / 1e6:7.1f} MB")
    print("\nArea per class:")
    for k, v in stats.items():
        print(f"  {k:9s} {v['area_km2']:10.1f} km2  {v['percent']:5.1f} %")
    print(f"\nSaved class tiles in {C.CLASS_TILES_DIR} and GeoJSON layers in {C.GEOJSON_DIR}")


if __name__ == "__main__":
    main()
