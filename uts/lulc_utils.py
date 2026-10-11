"""Helpers that need only numpy / pandas / scikit-learn (no GIS libraries)."""
import math

import numpy as np
import pandas as pd

import config as C


def make_features(b04, b8a, b11):
    """Build the model feature table from three 1-D arrays of reflectance values."""
    b04 = np.asarray(b04, dtype="float32")
    b8a = np.asarray(b8a, dtype="float32")
    b11 = np.asarray(b11, dtype="float32")
    eps = 1e-6
    df = pd.DataFrame({
        "B04": b04,
        "B8A": b8a,
        "B11": b11,
        "NDVI": (b8a - b04) / (b8a + b04 + eps),   # vegetation
        "NDMI": (b8a - b11) / (b8a + b11 + eps),   # moisture (NIR vs SWIR)
    })
    return df[C.FEATURES]


def valid_pixels(bands):
    """bands: array (3, n). True where the pixel holds usable values."""
    ok = np.all(np.isfinite(bands), axis=0)
    ok &= np.any(bands != 0, axis=0)
    return ok


def split_polygons(poly_df, test_size, seed):
    """Stratified split by polygon. poly_df needs columns poly_id and kelas."""
    rng = np.random.default_rng(seed)
    train, test = [], []
    for _, g in poly_df.groupby("kelas"):
        ids = g["poly_id"].to_numpy().copy()
        rng.shuffle(ids)
        n_test = max(1, int(round(len(ids) * test_size))) if len(ids) > 1 else 0
        test += list(ids[:n_test])
        train += list(ids[n_test:])
    return set(train), set(test)


def tile_grid(minx, miny, maxx, maxy, size):
    """Yield (name, x0, y0, x1, y1) for a grid aligned to multiples of `size`."""
    x_start = math.floor(minx / size) * size
    y_start = math.floor(miny / size) * size
    x = x_start
    while x < maxx:
        y = y_start
        while y < maxy:
            yield f"tile_{int(x // 1000)}_{int(y // 1000)}", x, y, x + size, y + size
            y += size
        x += size


def evaluate(y_true, y_pred, labels):
    from sklearn.metrics import (accuracy_score, classification_report,
                                 cohen_kappa_score, confusion_matrix)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "kappa": float(cohen_kappa_score(y_true, y_pred)),
        "labels": list(labels),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
        "per_class": classification_report(y_true, y_pred, labels=labels,
                                           output_dict=True, zero_division=0),
    }
