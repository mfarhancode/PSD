"""Step 1 - check and clean your digitized polygons.

Reads data/samples.geojson, converts the label column to `kelas` with the five official
values (built_up, farmland, water, forest, mangrove), drops polygons that are too small
to contain pixels, and writes data/samples_clean.geojson.
"""
import sys

import geopandas as gpd

import config as C


def main():
    if not C.SAMPLES_RAW.exists():
        sys.exit(f"Put your polygon file at {C.SAMPLES_RAW}")

    gdf = gpd.read_file(C.SAMPLES_RAW)
    print(f"Read {len(gdf)} features, geometry types: {sorted(gdf.geom_type.unique())}")
    gdf = gdf[gdf.geom_type.isin(["Polygon", "MultiPolygon"])].copy()

    label_col = "kelas" if "kelas" in gdf.columns else "Type" if "Type" in gdf.columns else None
    if label_col is None:
        sys.exit(f"No 'kelas' or 'Type' column found. Columns: {list(gdf.columns)}")
    print(f"Label column used: {label_col}")

    raw = gdf[label_col].astype(str).str.strip().str.lower()
    unknown = sorted(set(raw) - set(C.LABEL_MAP))
    if unknown:
        sys.exit(f"Unknown label values {unknown}. Add them to LABEL_MAP in config.py or fix the file.")
    gdf["kelas"] = raw.map(C.LABEL_MAP)

    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()
    invalid = ~gdf.geometry.is_valid
    if invalid.any():
        print(f"Fixing {int(invalid.sum())} invalid geometries")
        gdf.loc[invalid, "geometry"] = gdf.loc[invalid, "geometry"].buffer(0)

    gdf["area_m2"] = gdf.to_crs(C.CRS).geometry.area.round(0)
    too_small = gdf["area_m2"] < C.MIN_POLYGON_AREA_M2
    too_large = gdf["area_m2"] > C.WARN_POLYGON_AREA_M2
    print(f"Dropping {int(too_small.sum())} polygons smaller than {C.MIN_POLYGON_AREA_M2} m2")
    print(f"WARNING: {int(too_large.sum())} polygons larger than {C.WARN_POLYGON_AREA_M2 / 1e6:.0f} km2 "
          f"(kept, but they may cover mixed land cover - consider redrawing)")
    gdf = gdf[~too_small].copy()

    gdf["class_id"] = gdf["kelas"].map(C.CLASS_ID)
    gdf = gdf.sort_values("kelas").reset_index(drop=True)
    gdf["poly_id"] = gdf.groupby("kelas").cumcount().add(1).map("{:03d}".format)
    gdf["poly_id"] = gdf["kelas"] + "_" + gdf["poly_id"]

    out = gdf[["poly_id", "kelas", "class_id", "area_m2", "geometry"]].to_crs(4326)
    C.DATA.mkdir(exist_ok=True)
    out.to_file(C.SAMPLES_CLEAN, driver="GeoJSON")

    print("\nPolygons per class:")
    print(out.groupby("kelas").agg(polygons=("poly_id", "count"),
                                   median_area_m2=("area_m2", "median"),
                                   max_area_m2=("area_m2", "max")).reindex(C.CLASSES))
    print(f"\nSaved {len(out)} polygons -> {C.SAMPLES_CLEAN}")


if __name__ == "__main__":
    main()
