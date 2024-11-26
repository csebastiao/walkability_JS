# -*- coding: utf-8 -*-
"""
Create plot for all cities of node density, meaning intersection density which is correlated with high walkability (see Ewing & Cervero 2010). Made with the fully simplified graph from "./scripts/create_graphs.py".
"""

import os
import osmnx as ox
import seaborn as sns
from matplotlib import pyplot as plt


if __name__ == "__main__":
    folder_poly = "./data/raw/"
    folder_graph = "./data/processed/graphs/"
    folder_plot = "./plots/intersection_density/"
    # Get all polygon files
    for file_poly in [
        filename for filename in os.listdir(folder_poly) if filename.endswith(".gpkg")
    ]:
        city_name = file_poly.split(".")[0]
        G = ox.load_graphml(folder_graph + f"{city_name}_fully_simplified.graphml")
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(G, nodes=True, edges=True)
        fig, ax = plt.subplots(figsize=(16, 16))
        gdf_edges.plot(color="black", ax=ax, linewidth=1)
        sns.kdeplot(
            gdf_nodes,
            x="x",
            y="y",
            fill=True,
            cmap="crest",
            thresh=0.4,
            alpha=0.8,
            ax=ax,
            cbar=True,
        )
        ax.set_title(f"{city_name}, Intersection Density")
        ax.axis("off")
        plt.tight_layout()
        fig.savefig(folder_plot + f"{city_name}.png", dpi=400)
