## Business Understanding

### Objective
Produce a **map of the Earth's surface of East Java using satellite imagery**: for every
pixel of a Sentinel-2 image, decide which of five land-cover classes it belongs to, and present
the result as an interactive map on top of the satellite picture.

The five classes are:

| Class | Meaning |
|---|---|
| Built-up | Buildings, settlements, roads and other built surfaces |
| Farmland | Agricultural land, mainly rice fields |
| Water body | Sea, lakes, reservoirs, rivers and ponds |
| Forest | Non-mangrove forest |
| Mangrove forest | Coastal mangrove forest |

### Why this is useful
- Land-cover maps show how land is used across a province and are a starting point for
  planning, for example where farmland borders growing built-up areas.
- Mangrove forest grows only along the coast and is easy to confuse with ordinary forest.
  Separating the two lets the map show where coastal mangrove is.
- Classifying from satellite imagery covers the whole province consistently, instead of
  surveying it area by area on the ground.

### Questions the project answers
1. Where is each land-cover class located in East Java?
2. How much area does each class cover?
3. How reliable is the classification (accuracy per class, tested on polygons the model did not see)?

### Approach in one line
Digitize sample polygons for each class, read their Sentinel-2 values (bands 8A, 11 and 4),
train a Random Forest classifier, classify the province, and publish each class as a GeoJSON
layer in a Streamlit web map where a class can be switched on or off with a checkbox.

### Success criteria
- Overall accuracy and Cohen's kappa are reported on test polygons that were kept out of training.
- Every class is checked for confusion with the others (especially mangrove vs. forest and
  farmland vs. built-up). When a class is weak, more sample polygons are added and the model is
  trained again until the result is acceptable.

### Scope and limits
- One image composite (median of all cloud-free observations in 2025) at 20 m resolution.
- Only the five classes above; land change over time is not analysed.
- Results depend on the quality and spread of the digitized sample polygons.
- The GeoJSON layers are generalized (coarser grid, small patches removed) so the web map stays
  fast; exact areas are therefore taken from the classified raster, not from the GeoJSON.
