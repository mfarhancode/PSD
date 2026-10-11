"""Step 2 - download a Sentinel-2 L2A composite (bands B04, B8A, B11) from Copernicus openEO.

  python 02_download_sentinel2.py --test      small 10x10 km test around your first farmland polygon
  python 02_download_sentinel2.py --dry-run   list the tiles that would be downloaded, then stop
  python 02_download_sentinel2.py --samples-only   only tiles that contain your polygons (enough for training)
  python 02_download_sentinel2.py             download all tiles (resumes: existing files are skipped)

For every tile the server: filters Sentinel-2 L2A for 2025, masks cloud / cloud shadow / cirrus /
snow with the SCL band, takes the per-pixel median over time, and returns a 3-band GeoTIFF
(B04, B8A, B11) at 20 m in EPSG:32749.
A browser window opens the first time so you can log in to your Copernicus account.
"""
import argparse
import sys
import time

import geopandas as gpd
import openeo
from shapely.geometry import box

import config as C
from geo_utils import load_boundary_utm
from lulc_utils import tile_grid


def build_cube(conn, west, south, east, north):
    cube = conn.load_collection(
        "SENTINEL2_L2A",
        spatial_extent={"west": west, "south": south, "east": east, "north": north, "crs": C.CRS},
        temporal_extent=[C.DATE_START, C.DATE_END],
        bands=C.BANDS + ["SCL"],
        max_cloud_cover=C.MAX_CLOUD,
    )
    scl = cube.band("SCL")
    # SCL classes: 3 cloud shadow, 8 cloud medium, 9 cloud high, 10 thin cirrus, 11 snow/ice
    bad = (scl == 3) | (scl == 8) | (scl == 9) | (scl == 10) | (scl == 11)
    cube = cube.filter_bands(C.BANDS).mask(bad)
    cube = cube.reduce_dimension(dimension="t", reducer="median")
    cube = cube.resample_spatial(resolution=C.RESOLUTION, projection=C.EPSG)
    return cube


def run_job(conn, extent, out_path, title):
    west, south, east, north = extent
    cube = build_cube(conn, west, south, east, north)
    job = cube.create_job(title=title, out_format="GTiff")
    job.start_and_wait()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    job.get_results().download_file(out_path)


def test_extent():
    gdf = gpd.read_file(C.SAMPLES_CLEAN).to_crs(C.CRS)
    farm = gdf[gdf["kelas"] == "farmland"]
    if farm.empty:
        sys.exit("No farmland polygon found in samples_clean.geojson (run step 1 first).")
    c = farm.iloc[0].geometry.centroid
    half = 5000
    snap = lambda v: round(v / C.RESOLUTION) * C.RESOLUTION
    return snap(c.x - half), snap(c.y - half), snap(c.x + half), snap(c.y + half)


def all_tiles(samples_only=False):
    boundary = load_boundary_utm()
    minx, miny, maxx, maxy = boundary.bounds
    polys = gpd.read_file(C.SAMPLES_CLEAN).to_crs(C.CRS) if samples_only else None
    tiles = []
    for name, x0, y0, x1, y1 in tile_grid(minx, miny, maxx, maxy, C.TILE_SIZE_M):
        b = box(x0, y0, x1, y1)
        if not b.intersects(boundary):
            continue
        if samples_only and not polys.intersects(b).any():
            continue
        tiles.append((name, (x0, y0, x1, y1)))
    return tiles


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--samples-only", action="store_true",
                    help="only tiles that contain sample polygons")
    args = ap.parse_args()

    if args.test:
        extent = test_extent()
        print("Test extent (UTM 49S, metres):", extent)
        conn = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()
        out = C.TEST_DIR / "test_area.tif"
        t0 = time.time()
        run_job(conn, extent, out, "uts-test-area")
        print(f"Saved {out} in {time.time() - t0:.0f} s. Now open it and check it has 3 bands.")
        print("Check your credit usage in the Copernicus dashboard before running the full download.")
        return

    tiles = all_tiles(args.samples_only)
    print(f"{len(tiles)} tiles of {C.TILE_SIZE_M // 1000} km x {C.TILE_SIZE_M // 1000} km")
    if args.dry_run:
        for name, ext in tiles:
            print(" ", name, ext)
        return

    conn = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()
    failed = []
    for i, (name, (x0, y0, x1, y1)) in enumerate(tiles, 1):
        out = C.TILES_DIR / f"{name}.tif"
        if out.exists():
            print(f"[{i}/{len(tiles)}] {name}: already downloaded, skipping")
            continue
        print(f"[{i}/{len(tiles)}] {name}: requesting ...")
        try:
            t0 = time.time()
            run_job(conn, (x0, y0, x1, y1), out, f"uts-{name}")
            print(f"    done in {time.time() - t0:.0f} s")
        except Exception as e:  # keep going; rerun the script to retry failed tiles
            print(f"    FAILED: {e}")
            failed.append(name)
    if failed:
        print("\nFailed tiles (rerun this script to retry):", failed)
    else:
        print("\nAll tiles downloaded.")


if __name__ == "__main__":
    main()