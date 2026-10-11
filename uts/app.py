"""Streamlit app: land cover of East Java (Sentinel-2 + Random Forest), Leaflet map with class filter."""
import json

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

import config as C

ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
ESRI_ATTR = "Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community"

st.set_page_config(page_title="East Java Land Cover", layout="wide")


@st.cache_data
def load_json(path):
    p = C.ROOT / path
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def load_layer(k):
    return load_json(f"data/geojson/{k}.geojson")


st.title("Land cover map of East Java from Sentinel-2 imagery")
tab_bu, tab_flow, tab_map, tab_info = st.tabs(
    ["Business Understanding", "Workflow", "Map", "Information"])

# ------------------------------------------------------------------ Business understanding
with tab_bu:
    bu = C.ROOT / "business_understanding.md"
    st.markdown(bu.read_text(encoding="utf-8") if bu.exists() else "business_understanding.md not found")

# ------------------------------------------------------------------ Workflow
with tab_flow:
    metrics = load_json("data/metrics.json")
    period = metrics["period"] if metrics else f"{C.DATE_START} to {C.DATE_END}"
    st.markdown(f"""
**Take input &rarr; Process &rarr; Classify &rarr; Get information**

1. **Input**
   - Sentinel-2 L2A satellite imagery from Copernicus Data Space (openEO), period {period}.
   - Sample polygons digitized by hand in geojson.io for five classes: built-up, farmland, water body, forest, mangrove forest.
2. **Process**
   - Clouds, cloud shadow, cirrus and snow are masked with the SCL band, then a median composite is made.
   - Bands **8A, 11 and 4** (NIR, SWIR, red) are used; NDVI and NDMI are computed from the same bands.
   - Pixel values under each sample polygon become the training data.
3. **Classify**
   - A Random Forest is trained on 70 % of the polygons and tested on the other 30 %.
   - The trained model classifies every pixel of East Java, and the result is converted to one GeoJSON layer per class.
4. **Get information**
   - *Map* tab: class layers on top of the satellite basemap, with a checkbox per class.
   - *Information* tab: area of each class and the model's accuracy.
""")

# ------------------------------------------------------------------ Map
with tab_map:
    left, right = st.columns([1, 4])
    with left:
        st.subheader("Classes")

        def set_all(value):
            for k in C.CLASSES:
                st.session_state[f"show_{k}"] = value

        b1, b2 = st.columns(2)
        b1.button("Show all", on_click=set_all, args=(True,), use_container_width=True)
        b2.button("Hide all", on_click=set_all, args=(False,), use_container_width=True)
        selected = []
        for k in C.CLASSES:
            if st.checkbox(C.CLASS_NAME_EN[k], value=True, key=f"show_{k}"):
                selected.append(k)
            st.markdown(
                f"<div style='height:6px;width:100%;background:{C.CLASS_COLOR[k]};"
                f"margin:-10px 0 8px 0;border-radius:3px'></div>", unsafe_allow_html=True)
        opacity = st.slider("Layer opacity", 0.1, 1.0, 0.6, 0.05)
        st.caption("Only the ticked classes are drawn on the map.")

    with right:
        m = folium.Map(location=[-7.75, 112.6], zoom_start=8, tiles=None, control_scale=True)
        folium.TileLayer(tiles=ESRI, attr=ESRI_ATTR, name="Satellite (Esri World Imagery)").add_to(m)
        missing = []
        for k in selected:
            data = load_layer(k)
            if data is None:
                missing.append(k)
                continue
            color = C.CLASS_COLOR[k]
            folium.GeoJson(
                data,
                name=C.CLASS_NAME_EN[k],
                style_function=lambda _f, col=color, op=opacity: {
                    "fillColor": col, "color": col, "weight": 0.3, "fillOpacity": op},
            ).add_to(m)
        if missing:
            st.warning(f"No GeoJSON yet for: {', '.join(missing)}. Run 04_predict_and_vectorize.py first.")
        st_folium(m, height=680, use_container_width=True, returned_objects=[])

# ------------------------------------------------------------------ Information
with tab_info:
    stats = load_json("data/class_stats.json")
    metrics = load_json("data/metrics.json")
    if stats is None or metrics is None:
        st.info("Run steps 3 and 4 to fill this page.")
    else:
        st.subheader("Area per class")
        df = pd.DataFrame(stats["classes"]).T
        df.index = [C.CLASS_NAME_EN[k] for k in df.index]
        st.dataframe(df[["area_km2", "percent"]].rename(
            columns={"area_km2": "Area (km2)", "percent": "Share (%)"}), use_container_width=True)
        st.bar_chart(df["area_km2"])
        st.caption(f"Counted from the classified raster at {stats['resolution_m']} m resolution, "
                   "inside the East Java boundary used for the download.")

        st.subheader("Model accuracy (test polygons not used for training)")
        c1, c2, c3 = st.columns(3)
        c1.metric("Overall accuracy", f"{metrics['accuracy'] * 100:.1f} %")
        c2.metric("Cohen's kappa", f"{metrics['kappa']:.3f}")
        c3.metric("Test pixels", f"{metrics['n_pixels_test']:,}")
        labels = metrics["labels"]
        per = pd.DataFrame({k: metrics["per_class"][k] for k in labels}).T[
            ["precision", "recall", "f1-score", "support"]].round(3)
        st.dataframe(per, use_container_width=True)
        st.markdown("**Confusion matrix** (rows = true class, columns = predicted class)")
        st.dataframe(pd.DataFrame(metrics["confusion_matrix"], index=labels, columns=labels),
                     use_container_width=True)
        st.markdown(f"Training data: {metrics['polygons_per_class']} polygons per class; "
                    f"{metrics['n_pixels_train']:,} training pixels.")

        sig_path = C.ROOT / "data" / "class_signature.csv"
        if sig_path.exists():
            st.subheader("Mean reflectance of the training pixels (bands 8A, 11, 4)")
            sig = pd.read_csv(sig_path, index_col=0)[["B8A", "B11", "B04"]]
            st.line_chart(sig.T)
            st.caption("Each line is one class. Bands are in the order 8A, 11, 4 as in the assignment.")
