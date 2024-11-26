# -*- coding: utf-8 -*-
"""
Add amenities from OSM to the unsimplified street network extracted in "/scripts/create_graphs.py". List of amenities from the "./scripts/tags_amenities.json" file, see "OSM_tags.md" for for information.
"""

import os
import geopandas as gpd
import osmnx as ox
import shapely
import json


def find_centroid(geom):
    """Find the centroid of a geometry."""
    if type(geom) == shapely.Point:
        return [geom.xy[0][0], geom.xy[1][0]]
    return find_centroid(geom.centroid)


def return_true(dic):
    """Return the key where the value is True."""
    for key, val in dic.items():
        if val:
            return key


if __name__ == "__main__":
    SLOW_SPEED = 2
    FAST_SPEED = 5
    with open("./scripts/tags_amenities.json", "r") as f:
        tags = json.load(f)
    folder_poly = "./data/raw/"
    folder_graph = "./data/processed/graphs/"
    folder_geom = "./data/processed/geoms/"
    folder_plot = "./plots/city_graphs/"
    # Get all polygon files
    for file_poly in [
        filename for filename in os.listdir(folder_poly) if filename.endswith(".gpkg")
    ]:
        city_name = file_poly.split(".")[0]
        poly = gpd.read_file(folder_poly + file_poly).geometry[0]
        G = ox.load_graphml(folder_graph + city_name + "_unsimplified.graphml")
        # Add amenities to node
        features = ox.features.features_from_polygon(poly, tags)
        features["pos"] = features.geometry.apply(find_centroid)
        features["feature_type"] = features.apply(
            lambda x: return_true(
                {
                    key: (True if isinstance(x[key], str) else False)
                    for key in tags
                    if key in x.keys()
                }
            ),
            axis=1,
        )
        features["nearest_node"] = features["pos"].apply(
            lambda x: ox.nearest_nodes(G, X=x[0], Y=x[1])
        )
        for val in features["nearest_node"].values:
            amenity = features[features["nearest_node"] == val]["feature_type"]
            if "amenity" in G.nodes[val].keys():
                G.nodes[val]["amenity"].append(amenity)
            else:
                G.nodes[val]["amenity"] = [amenity]
        # Simplify keeping the closest nodes to amenities even if they are not intersections for higher granularity
        G = ox.simplify_graph(G, node_attrs_include=["amenity"])
        ox.save_graphml(G, folder_graph + city_name + "_simplified_wame.graphml")
