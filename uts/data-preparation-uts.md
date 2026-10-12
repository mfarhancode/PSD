# Data Preparation

Code: `02_download_sentinel2.py` (download) and `03_extract_and_train.py` (extraction). See [](code-uts.md).

## 1. Download from Copernicus openEO

For each 50 km x 50 km tile the server:

1. Selects Sentinel-2 L2A scenes of 2025 with scene cloud cover of at most 60 %.
2. Masks cloud shadow, medium and high cloud, thin cirrus and snow/ice using the scene
   classification layer (SCL classes 3, 8, 9, 10, 11).
3. Takes the per-pixel **median** over time, so each pixel is a cloud-free typical value.
4. Resamples to 20 m in EPSG:32749 and returns a 3-band GeoTIFF (B04, B8A, B11).

Only the 12 tiles that contain sample polygons were downloaded (`--samples-only`).

## 2. Pixel values under the polygons

For every sample polygon, the pixels whose centre lies inside the polygon are read from the tiles.
Invalid pixels (no data) are removed, and at most 300 random pixels per polygon are kept.

| Class | Polygons | Pixels |
|---|---|---|
| built_up | 48 | 2,171 |
| farmland | 41 | 438 |
| water | 48 | 7,044 |
| forest | 50 | 14,965 |
| mangrove | 50 | 3,658 |

## 3. Features

| Feature | Formula |
|---|---|
| B04, B8A, B11 | reflectance values |
| NDVI | (B8A − B04) / (B8A + B04) |
| NDMI | (B8A − B11) / (B8A + B11) |

NDVI and NDMI are computed only from the three bands in the brief.

## 4. Train / test split

The split is made **by polygon**, 70 % of the polygons of each class for training and 30 % for
testing (random seed 42). Pixels of one polygon never appear in both sets, which avoids an
over-optimistic accuracy caused by neighbouring, similar pixels.

| Set | Polygons | Pixels |
|---|---|---|
| Train | 167 | 20,117 |
| Test | 70 | 8,159 |
