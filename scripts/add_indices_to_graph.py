# -*- coding: utf-8 -*-
"""
Add accessibility indices from graph with amenities, made with "./scripts/add_amenities_to_graph.py".
"""

import os
import networkx as nx
import osmnx as ox
import json
import numpy as np
import tqdm


def proximity(x, speed, time_list=[5, 15]):
    for t in time_list:
        if x[f"time_{t}_speed_{speed}"]:
            return str(t)
    return "Longer"


if __name__ == "__main__":
    SLOW_SPEED = 2
    FAST_SPEED = 5
    with open("./scripts/tags_amenities.json", "r") as f:
        tags = json.load(f)
    folder_poly = "./data/raw/"
    folder_graph = "./data/processed/graphs/"
    folder_geom = "./data/processed/geoms/"
    folder_plot = "./plots/city_graphs/"
    with open("./scripts/urban_functions.json", "r") as f:
        urb_func = json.load(f)
    # Get all polygon files
    for file_poly in tqdm.tqdm(
        [filename for filename in os.listdir(folder_poly) if filename.endswith(".gpkg")]
    ):
        city_name = file_poly.split(".")[0]
        print(city_name)
        if city_name in ["Milan_Metropolitan"]:
            pass
        else:
            G = ox.load_graphml(folder_graph + city_name + "_simplified_wame.graphml")
            ## Add average distance and travel time for fast and slow walkers to edges
            # nx.set_node_attributes(
            #     G, nx.closeness_centrality(G, distance="length"), "closeness"
            # )
            # for u, v, k in G.edges:
            #     G.edges[u, v, k]["avg_dist"] = (
            #         np.average(
            #             list(nx.shortest_path_length(G, source=u, weight="length").values())
            #         )
            #         + np.average(
            #             list(nx.shortest_path_length(G, source=v, weight="length").values())
            #         )
            #     ) / 2
            # nx.set_edge_attributes(
            #     G,
            #     {
            #         key: round(val / (SLOW_SPEED * 1000 / 60))
            #         for key, val in nx.get_edge_attributes(G, "avg_dist").items()
            #     },
            #     "avg_time_slow",
            # )
            # nx.set_edge_attributes(
            #     G,
            #     {
            #         key: round(val / (FAST_SPEED * 1000 / 60))
            #         for key, val in nx.get_edge_attributes(G, "avg_dist").items()
            #     },
            #     "avg_time_fast",
            # )
            dict_ame = {}
            for key in urb_func.keys():
                dict_ame[key] = {}
            for n in G.nodes:
                for key in urb_func.keys():
                    dict_ame[key][n] = 0
                if "amenity" in G.nodes[n]:
                    for ame in G.nodes[n]["amenity"]:
                        for key in urb_func.keys():
                            if ame in urb_func[key]:
                                dict_ame[key][n] += 1
            for dic in dict_ame.keys():
                nx.set_node_attributes(G, dict_ame[dic], name=dic)
            TIME = [5, 15]  # in minutes, could add 30 but a bit long to run
            SPEED = [2, 5]  # in km/h
            THRESH = 1  # num of amenities necessary
            dist = {}
            for t in TIME:
                for s in SPEED:
                    dist[f"time_{t}_speed_{s}"] = round(1000 * s * t / 60)  # in meters
            access_node = {}
            for d in tqdm.tqdm(dist):
                access_node[d] = {}
                for n in G.nodes:
                    eg = nx.ego_graph(G, n, radius=dist[d], distance="length")
                    if len(eg) > 1:
                        gdfn, gdfe = ox.graph_to_gdfs(eg)
                        cond = [False] * len(urb_func.keys())
                        for idx, key in enumerate(urb_func.keys()):
                            if np.sum(gdfn[key].values) >= THRESH:
                                cond[idx] = True
                        access_node[d][n] = all(cond)
                    else:
                        access_node[d][n] = False
            access_edge = {}
            for d in dist:
                access_edge[d] = {}
                for e in G.edges:
                    access_edge[d][e] = access_node[d][e[0]] or access_node[d][e[1]]
            for key in access_node:
                nx.set_node_attributes(G, access_node[key], key)
                nx.set_edge_attributes(G, access_edge[key], key)
            nodes, edges = ox.graph_to_gdfs(G)
            for s in SPEED:
                edges[f"speed_{s}"] = edges.apply(lambda x: proximity(x, s), axis=1)
                nx.set_edge_attributes(G, edges[f"speed_{s}"], f"speed_{s}")
            ox.save_graphml(G, folder_graph + city_name + "_simplified_wind.graphml")
