# -*- coding: utf-8 -*-
"""
Add accessibility indices from graph with amenities, made with "./scripts/add_amenities_to_graph.py".
"""

import os
import geopandas as gpd
import networkx as nx
import osmnx as ox
import shapely
import json
import numpy as np


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
    with open("tags_amenities.json", "r") as f:
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
        # Add average distance and travel time for fast and slow walkers to edges
        nx.set_node_attributes(
            G, nx.closeness_centrality(G, distance="length"), "closeness"
        )
        for u, v, k in G.edges:
            G.edges[u, v, k]["avg_dist"] = (
                np.average(
                    list(nx.shortest_path_length(G, source=u, weight="length").values())
                )
                + np.average(
                    list(nx.shortest_path_length(G, source=v, weight="length").values())
                )
            ) / 2
        nx.set_edge_attributes(
            G,
            {
                key: round(val / (SLOW_SPEED * 1000 / 60))
                for key, val in nx.get_edge_attributes(G, "avg_dist").items()
            },
            "avg_time_slow",
        )
        nx.set_edge_attributes(
            G,
            {
                key: round(val / (FAST_SPEED * 1000 / 60))
                for key, val in nx.get_edge_attributes(G, "avg_dist").items()
            },
            "avg_time_fast",
        )
        # Add population to edges in the graph
