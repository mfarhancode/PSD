# Modeling and Evaluation

## Model

**Random Forest** (scikit-learn): 300 trees, balanced class weights, random seed 42.
Input features: B04, B8A, B11, NDVI, NDMI. Code: `03_extract_and_train.py`.

## Results on the test polygons

The test set holds 70 polygons (8,159 pixels) that were not used for training.

| Metric | Value |
|---|---|
| Overall accuracy | 96.47 % |
| Cohen's kappa | 0.942 |

### Per-class results

| Class | Precision | Recall | F1 | Test pixels |
|---|---|---|---|---|
| built_up | 0.968 | 0.912 | 0.939 | 431 |
| farmland | 0.162 | 0.372 | 0.225 | 43 |
| water | 0.979 | 0.927 | 0.953 | 2,189 |
| forest | 0.987 | 0.993 | 0.990 | 4,465 |
| mangrove | 0.916 | 0.970 | 0.942 | 1,031 |

### Confusion matrix (rows = true class, columns = predicted)

| | built_up | farmland | water | forest | mangrove |
|---|---|---|---|---|---|
| **built_up** | 393 | 1 | 0 | 37 | 0 |
| **farmland** | 0 | 16 | 27 | 0 | 0 |
| **water** | 0 | 74 | 2,030 | 2 | 83 |
| **forest** | 13 | 4 | 7 | 4,432 | 9 |
| **mangrove** | 0 | 4 | 9 | 18 | 1,000 |

### Feature importance

| Feature | Importance |
|---|---|
| NDMI | 0.251 |
| NDVI | 0.233 |
| B11 | 0.231 |
| B8A | 0.180 |
| B04 | 0.106 |

### Mangrove vs. forest in bands 8A, 11 and 4

Mean reflectance of the training pixels:

| Class | B8A | B11 | B04 |
|---|---|---|---|
| built_up | 2,368 | 2,637 | 1,248 |
| farmland | 1,353 | 764 | 657 |
| water | 462 | 265 | 505 |
| forest | 3,337 | 1,692 | 341 |
| mangrove | 3,754 | 1,242 | 356 |

Mangrove and forest have almost the same red reflectance (B04), but mangrove has higher B8A and lower
B11 than forest. This difference lets the model separate them: only 18 of 1,031 mangrove test pixels
were predicted as forest, and 9 of 4,465 forest test pixels as mangrove.

## Improving the model

- The first run kept only polygons of at least 2,000 m², which left 15 farmland polygons. Lowering the
  minimum to 500 m² kept 41 farmland polygons (237 polygons in total).

## Limitations

- **Farmland is the weakest class** (F1 0.225). Its polygons are small, so it has only 438 training
  and test pixels against 14,965 for forest, and only 43 farmland pixels in the test set. Most farmland
  test pixels (27 of 43) were predicted as water, and 74 water pixels were predicted as farmland; flooded
  rice fields, which look like water, are a likely cause. The overall accuracy is
  dominated by the large classes and says little about farmland.
- Because of this, the class areas in the app, especially farmland, built-up and forest, should be read
  as estimates rather than exact figures.
- The map covers the 12 downloaded tiles, not the whole province.
- The next step to improve the result would be more and larger farmland polygons.

## Class areas

The area of each class is shown in the **Information** tab of the app (see [](deployment-guide.md)).
