"""Helpers that need geopandas / shapely."""
import geopandas as gpd
from shapely.ops import unary_union

import config as C


def load_boundary_utm():
    """East Java boundary in EPSG:32749 as one shapely geometry (far islands removed if configured)."""
    gdf = gpd.read_file(C.BOUNDARY)
    geom = unary_union(list(gdf.to_crs(C.CRS).geometry))
    parts = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    if C.EXCLUDE_FAR_ISLANDS:
        kept = []
        for p in parts:
            c = gpd.GeoSeries([p], crs=C.CRS).to_crs(4326).iloc[0].centroid
            if c.x > C.MAX_LON or c.y > C.MAX_LAT:
                continue
            kept.append(p)
        parts = kept
    geom = unary_union(parts)
    if C.BOUNDARY_BUFFER_M:
        geom = geom.buffer(C.BOUNDARY_BUFFER_M)
    return geom
