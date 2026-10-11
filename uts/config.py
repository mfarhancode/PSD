"""Central settings for the East Java LULC project. Edit values here only."""
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"

# ---- input files (put them in the data/ folder) ----------------------------
SAMPLES_RAW = DATA / "samples.geojson"            # your digitized polygons (from geojson.io)
BOUNDARY = DATA / "east_java_boundary.geojson"    # province boundary (from geoBoundaries)

# ---- generated files --------------------------------------------------------
SAMPLES_CLEAN = DATA / "samples_clean.geojson"    # step 1 output
TEST_DIR = DATA / "test"                          # step 2 --test output
TILES_DIR = DATA / "tiles"                        # step 2 output (Sentinel-2 composite tiles)
PIXELS_CSV = DATA / "training_pixels.csv"         # step 3 output
MODEL_PATH = DATA / "model_rf.joblib"             # step 3 output
METRICS_JSON = DATA / "metrics.json"              # step 3 output
SIGNATURE_CSV = DATA / "class_signature.csv"      # step 3 output (mean B04/B8A/B11 per class)
CLASS_TILES_DIR = DATA / "class_tiles"            # step 4 output (classified GeoTIFF tiles)
GEOJSON_DIR = DATA / "geojson"                    # step 4 output (one GeoJSON per class)
STATS_JSON = DATA / "class_stats.json"            # step 4 output (area per class)

# ---- classes ----------------------------------------------------------------
CLASSES = ["built_up", "farmland", "water", "forest", "mangrove"]
CLASS_ID = {name: i + 1 for i, name in enumerate(CLASSES)}       # 0 = no data
CLASS_NAME_EN = {
    "built_up": "Built-up (Bangunan)",
    "farmland": "Farmland (Lahan pertanian)",
    "water": "Water body (Lautan, danau, perairan)",
    "forest": "Forest (Hutan)",
    "mangrove": "Mangrove forest (Hutan mangrove)",
}
CLASS_COLOR = {
    "built_up": "#e31a1c",
    "farmland": "#ffd92f",
    "water": "#1f78b4",
    "forest": "#1b7837",
    "mangrove": "#7b3294",
}
# Accepted spellings in your geojson -> official class value.
# Step 1 reads column "kelas" if it exists, otherwise column "Type".
LABEL_MAP = {
    "built_up": "built_up", "built-up": "built_up", "bangunan": "built_up", "pemukiman": "built_up",
    "farmland": "farmland", "sawah": "farmland", "pertanian": "farmland",
    "water": "water", "air": "water",
    "forest": "forest", "hutan": "forest", "hutan non mangrove": "forest",
    "mangrove": "mangrove", "hutan mangrove": "mangrove",
}

# ---- Sentinel-2 download (openEO / Copernicus Data Space) -------------------
DATE_START = "2025-01-01"
DATE_END = "2026-01-01"        # end date is exclusive -> all of 2025
MAX_CLOUD = 60                 # % scene cloud cover accepted before pixel-level masking
BANDS = ["B04", "B8A", "B11"]  # lecturer's note: bands 8A-11-4 (order in the GeoTIFF)
EPSG = 32749                   # UTM 49S, used for every tile so that tiles line up
CRS = f"EPSG:{EPSG}"
RESOLUTION = 20                # metres (B8A and B11 are natively 20 m)
TILE_SIZE_M = 50_000           # 50 km x 50 km tiles = 2500 x 2500 pixels

# Far offshore islands (Kangean, Masalembu, Bawean ...) would add many tiles that are
# mostly sea. Set to False if you want them included.
EXCLUDE_FAR_ISLANDS = True
MAX_LON = 114.7
MAX_LAT = -6.4
BOUNDARY_BUFFER_M = 0          # >0 adds a coastal sea strip around the province

# ---- sampling and model -----------------------------------------------------
MIN_POLYGON_AREA_M2 = 500    # polygons smaller than this are dropped (step 1)
WARN_POLYGON_AREA_M2 = 5_000_000   # polygons larger than this are flagged (mixed land cover risk)
MAX_PIXELS_PER_POLYGON = 300   # random cap so very large polygons do not dominate
TEST_SIZE = 0.30               # share of POLYGONS (not pixels) kept for testing
SEED = 42
FEATURES = ["B04", "B8A", "B11", "NDVI", "NDMI"]
RF_PARAMS = dict(n_estimators=300, class_weight="balanced", n_jobs=-1, random_state=SEED)

# ---- GeoJSON layers for the web map ------------------------------------------
VECTOR_FACTOR = 3              # 3 -> vectorize at 60 m (smaller files). 1 = full 20 m
SIEVE_MIN_PIXELS = 10          # remove blobs smaller than this many (coarse) pixels
MIN_AREA_HA = 3                # drop polygons smaller than this
SIMPLIFY_M = 40                # geometry simplification tolerance in metres
