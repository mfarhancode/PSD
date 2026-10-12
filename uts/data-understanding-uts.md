# Data Understanding

## Study area

East Java province, Indonesia. Boundary: geoBoundaries (ADM1, simplified), clipped to the province.
Far offshore islands (Kangean, Masalembu, Bawean) are left out to save download quota. Sentinel-2
data was downloaded for the 12 tiles (50 km x 50 km) that contain the sample polygons.

## Satellite data

- **Sentinel-2 L2A** (Copernicus Data Space, via openEO), 1 January to 31 December 2025.
- Bands used, as asked in the brief (8A-11-4):

| Band | Name | Native resolution |
|---|---|---|
| B8A | Near infrared (narrow) | 20 m |
| B11 | Short-wave infrared | 20 m |
| B04 | Red | 10 m |

- The data is processed at 20 m in UTM zone 49S (EPSG:32749).

## Sample polygons

Polygons were digitized by hand in geojson.io, each with a property holding its class.

![Sample polygons digitized in geojson.io (Surabaya region)](images/uts_polygons.png)

The original labels were mapped to the five class names:

| Original label | Class (`kelas`) |
|---|---|
| Pemukiman | `built_up` |
| Sawah | `farmland` |
| Air | `water` |
| Hutan non mangrove | `forest` |
| Hutan mangrove | `mangrove` |

248 polygons were digitized. `01_prepare_samples.py` drops polygons that are too small to contain
pixels. With a minimum area of 2,000 m² only 204 polygons remained, and farmland kept just 15 polygons.
Because rice fields are small, the minimum was lowered to **500 m²**, which dropped 11 polygons and kept
**237**, including 41 farmland polygons.

| Class | Polygons | Median area (m²) | Max area (m²) |
|---|---|---|---|
| built_up | 48 | 12,137 | 97,782 |
| farmland | 41 | 1,306 | 76,446 |
| water | 48 | 30,391 | 289,593,506 |
| forest | 50 | 2,382,332 | 95,597,754 |
| mangrove | 50 | 16,461 | 321,881 |

## Known limitations of the samples

- Some polygons are large (16 are larger than 5 km², for example sea and forest) and may contain mixed
  land cover. At most 300 random pixels are used per polygon so large polygons do not dominate.
- Farmland polygons are small (median 1,306 m²), so they contribute few pixels.
- Fishponds next to mangrove and flooded rice fields can look like water.
