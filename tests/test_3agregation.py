import sys
sys.path.append('..')

import matplotlib.pyplot as plt
import networkx as nx
import math

from topology import generate_topology_fig8c_aggregation_ring
"""
Test for generating and visualizing the Fig8c topology with an aggregation ring.

This test creates a hierarchical network topology with three layers:
Backbone -> Aggregation -> Edge. The topology is generated using the 
`generate_topology_fig8c_aggregation_ring` function and visualized with `matplotlib`.

Topology structure:
    - Backbone nodes connect to aggregation nodes.
    - Aggregation nodes are connected in a ring structure.
    - Edge nodes are redundantly connected to the aggregation nodes.

Node placement:
    - Backbone nodes are placed at the top.
    - Aggregation nodes are placed in a circular ring.
    - Edge nodes are placed around their primary aggregation node.

Parameters:
    n_edge (int): Number of edge nodes.
    n_aggregation (int): Number of aggregation nodes (set to 4 for Fig8c).
    n_backbone (int): Number of backbone nodes (set to 2 for Fig8c).
    edge_uplinks_max (int): Maximum number of uplinks each edge node can have.

Expected Output:
    A visual representation of the Fig8c topology with nodes and edges
    arranged in a hierarchical layout, with aggregation nodes forming a ring.
"""

n_edge = 8
n_aggregation = 5
n_backbone = 3
edge_uplinks_max = 5

G = generate_topology_fig8c_aggregation_ring(
    n_edge=n_edge,
    n_aggregation=n_aggregation,
    n_backbone=n_backbone,
    p_aggregation_to_edge=0.5,
    edge_uplinks_max=edge_uplinks_max,
    seed=1
)



backbone_nodes = [n for n, d in G.nodes(data=True) if d["layer"] == "backbone"]
aggregation_nodes = [n for n, d in G.nodes(data=True) if d["layer"] == "aggregation"]
edge_nodes = [n for n, d in G.nodes(data=True) if d["layer"] == "edge"]
pos = {}

if backbone_nodes:
        x_backbone = [-2, 2] if len(backbone_nodes) == 2 else list(range(len(backbone_nodes)))
        for i, b in enumerate(backbone_nodes):
            pos[b] = (x_backbone[i], 3.5)

R_agg = 2.0
for i, a in enumerate(aggregation_nodes):
    theta = 2 * math.pi * i / len(aggregation_nodes)
    x = R_agg * math.cos(theta)
    y = R_agg * math.sin(theta)
    pos[a] = (x, y)


edge_groups = {a: [] for a in aggregation_nodes}
unassigned = []

for e in edge_nodes:
    parents = [u for u in G.predecessors(e) if u in aggregation_nodes]
    if parents:
        edge_groups[parents[0]].append(e)
    else:
        unassigned.append(e)

R_edge = 0.9
for a in aggregation_nodes:
    x0, y0 = pos[a]
    group = edge_groups[a]
    k = len(group)

    if k == 0:
        continue

    base_angle = math.atan2(y0, x0)

    spread = math.pi / 3
    if k == 1:
        angles = [base_angle]
    else:
        angles = [
            base_angle - spread / 2 + i * spread / (k - 1)
            for i in range(k)
        ]

    for e, ang in zip(group, angles):
        xe = x0 + R_edge * math.cos(ang)
        ye = y0 + R_edge * math.sin(ang)
        pos[e] = (xe, ye)

for i, e in enumerate(unassigned):
    pos[e] = (-1 + i * 0.5, -3.5)

plt.figure(figsize=(10, 8))

nx.draw_networkx_nodes(
    G, pos, nodelist=backbone_nodes, node_color="#e57373", node_size=1200, label="backbone"
)
nx.draw_networkx_nodes(
    G, pos, nodelist=aggregation_nodes, node_color="#e6d96a", node_size=1200, label="aggregation ring"
)
nx.draw_networkx_nodes(
    G, pos, nodelist=edge_nodes, node_color="#a8d0df", node_size=800, label="edge"
)

nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=18, width=1.6)
nx.draw_networkx_labels(G, pos, font_size=10)

plt.title("Topology Fig8c - ordered aggregation ring")
plt.legend()
plt.axis("off")
plt.tight_layout()
plt.show()