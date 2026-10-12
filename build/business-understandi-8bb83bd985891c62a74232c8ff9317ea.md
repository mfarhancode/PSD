# Business Understanding

## Objective

Produce a **map of the Earth's surface of East Java using satellite imagery**: for every pixel of a
Sentinel-2 image, decide which of five land-cover classes it belongs to, and present the result as an
interactive map on top of the satellite picture.

| Class | Meaning |
|---|---|
| Built-up | Buildings, settlements, roads and other built surfaces |
| Farmland | Agricultural land, mainly rice fields |
| Water body | Sea, lakes, reservoirs, rivers and ponds |
| Forest | Non-mangrove forest |
| Mangrove forest | Coastal mangrove forest |

## Why this is useful

- A land-cover map shows how land is used across a province and is a starting point for planning,
  for example where farmland borders growing built-up areas.
- Mangrove forest grows only along the coast and is easy to confuse with ordinary forest. Separating
  the two shows where coastal mangrove is.
- Classifying from satellite imagery covers the whole province consistently, instead of surveying it
  area by area on the ground.

## Questions the project answers

1. Where is each land-cover class located in East Java?
2. How much area does each class cover?
3. How reliable is the classification (accuracy per class, tested on polygons the model did not see)?

## Success criteria

- Overall accuracy and Cohen's kappa are reported on test polygons kept out of training.
- Every class is checked for confusion with the others, especially mangrove vs. forest and
  farmland vs. built-up. When a class is weak, more sample polygons are added and the model is
  trained again until the result is acceptable.

## Scope and limits

- The classified area is the part of East Java covered by the 12 downloaded Sentinel-2 tiles.
- One image composite (median of cloud-free observations in 2025) at 20 m resolution.
- Only the five classes above; change over time is not analysed.
- Results depend on the quality and spread of the digitized polygons.
- The GeoJSON layers are generalized so the web map stays fast; exact areas come from the classified
  raster, not from the GeoJSON.
