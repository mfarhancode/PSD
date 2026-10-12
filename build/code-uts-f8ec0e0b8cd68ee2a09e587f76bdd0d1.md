# Code

All code lives in this folder and is shown below directly from the files. Run order: 1 to 4, then the app.

## Settings: `config.py`

All paths, class names, colours, dates, bands and model settings.

```{literalinclude} config.py
```

## Step 1: prepare samples (`01_prepare_samples.py`)

Maps labels to the five class names, fixes invalid geometries, drops polygons that are too small.

```{literalinclude} 01_prepare_samples.py
```

## Step 2: download Sentinel-2 (`02_download_sentinel2.py`)

Cloud-masked median composite of bands B04, B8A, B11 for 2025, downloaded tile by tile from Copernicus openEO.

```{literalinclude} 02_download_sentinel2.py
```

## Step 3: extract pixels, train, evaluate (`03_extract_and_train.py`)

Reads pixel values under the polygons, trains the Random Forest, evaluates on test polygons.

```{literalinclude} 03_extract_and_train.py
```

## Step 4: predict and create GeoJSON layers (`04_predict_and_vectorize.py`)

Classifies every tile and converts each class into a GeoJSON layer.

```{literalinclude} 04_predict_and_vectorize.py
```

## Helper modules

```{literalinclude} lulc_utils.py
```

```{literalinclude} geo_utils.py
```

## Streamlit app: `app.py`

Business Understanding, workflow, Leaflet map with one checkbox per class, and information about areas and accuracy.

```{literalinclude} app.py
```
