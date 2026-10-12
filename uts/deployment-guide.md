# Deployment

The web map is deployed on **Streamlit Community Cloud**:
[https://uts-psd-farhan.streamlit.app/](https://uts-psd-farhan.streamlit.app/)

## What the app shows

- **Business Understanding** and **Workflow** tabs.
- **Map** tab: the satellite basemap (Esri World Imagery) with one GeoJSON layer per class on top.
  Each class has a checkbox; only the ticked classes are drawn.
- **Information** tab: area per class, overall accuracy, kappa, confusion matrix.

![Map with only the forest class ticked](images/uts_map.png)

## Run locally

```
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

1. Push the repository to GitHub. Do not push `data/tiles/`, `data/class_tiles/`,
   `data/training_pixels.csv` or `data/model_rf.joblib`.
2. On share.streamlit.io choose **Create app**, select the repository and branch.
3. Set **Main file path** to `uts/app.py`.
4. Deploy. Dependencies are read from `requirements.txt` (streamlit, folium, streamlit-folium, pandas).

The app reads `data/geojson/*.geojson`, `data/class_stats.json`, `data/metrics.json` and
`data/class_signature.csv`.
