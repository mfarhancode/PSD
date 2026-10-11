# East Java land cover (LULC) - Sentinel-2, Random Forest, Streamlit

Classes: `built_up`, `farmland`, `water`, `forest`, `mangrove` (label column: `kelas`).
Bands 8A-11-4, Sentinel-2 L2A, year 2025, 20 m.

## Setup (VS Code, Windows PowerShell)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-pipeline.txt
```
Put your polygon file at `data/samples.geojson` (the boundary is already in `data/east_java_boundary.geojson`).

## Run in this order
| Step | Command | What it does |
|---|---|---|
| 1 | `python 01_prepare_samples.py` | Checks polygons, maps labels to `kelas`, writes `data/samples_clean.geojson` |
| 2a | `python 02_download_sentinel2.py --test` | Small 10x10 km test download (login to Copernicus in the browser). Open `data/test/test_area.tif` and check it has 3 bands |
| 2b | `python 02_download_sentinel2.py --dry-run` | Shows how many tiles the full download needs |
| 2c | `python 02_download_sentinel2.py` | Downloads all tiles to `data/tiles/` (rerun to retry failed ones) |
| 3 | `python 03_extract_and_train.py` | Pixels under polygons -> Random Forest -> accuracy, kappa, confusion matrix |
| 4 | `python 04_predict_and_vectorize.py` | Classifies all tiles, writes class GeoTIFF tiles + one GeoJSON per class + area table |
| 5 | `pip install -r requirements.txt` then `streamlit run app.py` | Web map with class checkboxes |

**Improve the model:** after step 3 look at the lowest per-class F1 and the confusion matrix.
Add more polygons for the weak classes in geojson.io, then rerun steps 1 and 3 (step 2 does not need rerunning
unless the polygons are in areas not yet downloaded).

## Deploy on Streamlit Community Cloud
Push to GitHub: `app.py`, `config.py`, `business_understanding.md`, `requirements.txt`, and the `data/` files
the app reads (`data/geojson/*.geojson`, `data/class_stats.json`, `data/metrics.json`, `data/class_signature.csv`).
Do not push `data/tiles/`. Each file must be below 100 MB; if a GeoJSON is larger, raise `VECTOR_FACTOR`,
`MIN_AREA_HA` or `SIMPLIFY_M` in `config.py` and rerun step 4.

## Choices made (all in `config.py`)
- Period: 2025-01-01 to 2025-12-31, median composite, cloud/shadow/cirrus/snow masked with SCL.
- Features: B04, B8A, B11 plus NDVI and NDMI computed from them.
- Train/test split by polygon (70/30), at most 300 random pixels per polygon.
- Far offshore islands (Kangean, Masalembu, Bawean) are left out of the download to save quota
  (`EXCLUDE_FAR_ISLANDS`). The boundary is land only, so open sea is not classified (`BOUNDARY_BUFFER_M` adds a coastal strip).
- GeoJSON layers are generalized for the web map; class areas are counted from the raster, not the GeoJSON.
