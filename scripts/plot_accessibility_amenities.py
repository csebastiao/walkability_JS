# -*- coding: utf-8 -*-
"""
Create plot for all cities of accessibility metrics from graph with amenities made with "./scripts/add_amenities_to_graph.py" and indices made with "./scripts/add_indices_to_graph.py".
"""

import os
import osmnx as ox
from matplotlib import pyplot as plt
import matplotlib as mpl
import tqdm


if __name__ == "__main__":
    folder_poly = "./data/raw/"
    folder_graph = "./data/processed/graphs/"
    folder_plot = "./plots/accessibility/"
    # Get all polygon files
    for file_poly in tqdm.tqdm(
        [filename for filename in os.listdir(folder_poly) if filename.endswith(".gpkg")]
    ):
        city_name = file_poly.split(".")[0]
        print(city_name)
        if city_name in ["Milan_Metropolitan"]:
            pass
        else:
            G = ox.load_graphml(folder_graph + f"{city_name}_simplified_wind.graphml")
            gdf_nodes, gdf_edges = ox.graph_to_gdfs(G, nodes=True, edges=True)
            cmap = mpl.colors.ListedColormap(["orange", "blue", "gray"])
            speed_list = [2, 5]
            for speed in speed_list:
                fig, ax = plt.subplots(figsize=(32, 20))
                gdf_edges.plot(
                    ax=ax,
                    linewidth=0.5,
                    column=f"speed_{speed}",
                    cmap=cmap,
                    legend=True,
                )
                ax.set_title(f"{city_name}, accessibility walking at {speed} km/h")
                ax.axis("off")
                plt.tight_layout()
                fig.savefig(folder_plot + f"{city_name}_speed_{speed}.png", dpi=400)
