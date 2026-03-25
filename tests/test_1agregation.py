import sys
sys.path.append('..')

import matplotlib.pyplot as plt
import networkx as nx
from topology import generate_topology_fig8a_single_agg_layer

"""
Test for generating and visualizing the Fig8a topology with a single aggregation layer.

This test creates a hierarchical network topology with three layers:
Backbone -> Aggregation -> Edge. The topology is generated using the 
`generate_topology_fig8a_single_agg_layer` function and visualized with `matplotlib`.

Topology structure:
    - A single backbone node connects to the aggregation node.
    - The aggregation node connects to multiple edge nodes.
    - Edge nodes are redundantly connected to the aggregation node.

Node placement:
    - Backbone nodes are placed at the top.
    - Aggregation nodes are placed in the middle.
    - Edge nodes are placed at the bottom.

Parameters:
    n_edge (int): Number of edge nodes.
    n_agg (int): Number of aggregation nodes (set to 1 for Fig8a).
    n_backbone (int): Number of backbone nodes (set to 1 for Fig8a).

Expected Output:
    A visual representation of the Fig8a topology with nodes and edges
    arranged in a hierarchical layout.
"""

n_edge = 6
n_agg = 1
n_backbone = 1
internet = 'internet'

G = generate_topology_fig8a_single_agg_layer(
    internet=internet,
    n_edge=n_edge,
    n_agg=n_agg,
    n_backbone=n_backbone,
    p_backbone_agg=1.0,
    p_agg_edge=0.5,
    edge_redundancy=2,
    seed=1
)

backbone_nodes = [n for n, d in G.nodes(data=True) if d["layer"] == "backbone"]
agg_nodes = [n for n, d in G.nodes(data=True) if d["layer"] == "agg"]
edge_nodes = [n for n, d in G.nodes(data=True) if d["layer"] == "edge"]

pos = {}

for i, node in enumerate(backbone_nodes):
    pos[node] = (i, 2)

for i, node in enumerate(agg_nodes):
    pos[node] = (i + 0.5, 1)
# edge abajo
for i, node in enumerate(edge_nodes):
    pos[node] = (i * 0.7, 0)
pos[internet] = (0.5, 3)


plt.figure(figsize=(10, 6))

nx.draw_networkx_nodes(G, pos, nodelist=backbone_nodes, node_color="lightcoral", node_size=900, label="backbone")
nx.draw_networkx_nodes(G, pos, nodelist=agg_nodes, node_color="khaki", node_size=900, label="agg")
nx.draw_networkx_nodes(G, pos, nodelist=edge_nodes, node_color="lightblue", node_size=900, label="edge")

nx.draw_networkx_edges(
    G, pos,
    arrows=True,
    arrowstyle="->",
    arrowsize=18,
    width=1.8
)

nx.draw_networkx_labels(G, pos, font_size=10)

plt.title("Topology Fig8a - single agg layer")
plt.legend()
plt.axis("off")
plt.tight_layout()
plt.show()