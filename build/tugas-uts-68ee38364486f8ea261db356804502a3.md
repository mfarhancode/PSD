# UTS Replacement Assignment: Land Cover Classification of East Java

## Assignment

Re-digitize and classify land cover for **East Java** from Sentinel-2 satellite imagery, using a
classification model of my choice, and publish the result as an interactive web map.

| Class | Meaning |
|---|---|
| `built_up` | Built-up area (buildings) |
| `farmland` | Farmland |
| `water` | Water bodies (sea, lakes, waters) |
| `forest` | Forest |
| `mangrove` | Mangrove forest |

Requirements from the brief:

- Use many sample polygons and keep adding them until the model performs well.
- Use bands **8A, 11 and 4** to separate mangrove forest from regular forest.
- Show the classification as GeoJSON layers on top of a satellite map, with Leaflet.
- A checkbox per class: when a class is ticked, only that class is shown.
- Include a Business Understanding section.
- Deploy on Streamlit.

## Coverage

Sentinel-2 data was downloaded for the 12 tiles (50 km x 50 km each) that contain the sample
polygons, so the classified map covers that part of East Java, mainly the central part of the province
around Surabaya, Mojokerto, Jombang, Kediri and Malang.

## Workflow

**Take input, process, classify, get information.**

1. **Input:** Sentinel-2 L2A imagery (Copernicus openEO, year 2025) and hand-digitized sample polygons.
2. **Process:** cloud masking, median composite, bands 8A-11-4, pixel values under each polygon.
3. **Classify:** Random Forest, tested on polygons kept out of training; every pixel of East Java is classified.
4. **Get information:** class layers on a map, area per class, and model accuracy.

## Pages

- [](business-understanding-uts.md)
- [](data-understanding-uts.md)
- [](data-preparation-uts.md)
- [](modeling-evaluation-uts.md)
- [](code-uts.md)
- [](deployment-guide.md)
