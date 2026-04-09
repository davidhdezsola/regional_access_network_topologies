import sys
sys.path.append('..')

import matplotlib.pyplot as plt
import networkx as nx
import math

from topology import generate_topology_fig8c_aggregation_ring


# PARÁMETROS

n_edge = 6
n_aggregation = 5
n_backbone = 2
edge_uplinks_max = 3
internet = 'internet'

G = generate_topology_fig8c_aggregation_ring(
    internet=internet,
    n_edge=n_edge,
    n_aggregation=n_aggregation,
    n_backbone=n_backbone,
    p_aggregation_to_edge=0.5,
    edge_uplinks_max=edge_uplinks_max,
    seed=1
)

# CLASIFICACIÓN DE NODOS

backbone_nodes = [n for n, d in G.nodes(data=True) if d["layer"] == "backbone"]
aggregation_nodes = [n for n, d in G.nodes(data=True) if d["layer"] == "aggregation"]
edge_nodes = [n for n, d in G.nodes(data=True) if d["layer"] == "edge"]
pgw_nodes = [n for n, d in G.nodes(data=True) if d["layer"] == "pgw"]
wan_nodes = [n for n, d in G.nodes(data=True) if d["layer"] == "wan"]

pos = {}

# INTERNET

pos[internet] = (0, 5)

# BACKBONE 

bb_groups = {}
for n in backbone_nodes:
    bb = n.split("_")[0]
    bb_groups.setdefault(bb, []).append(n)

x_spacing = 3
for i, (bb, switches) in enumerate(sorted(bb_groups.items())):
    x_center = - (len(bb_groups)-1)*x_spacing/2 + i*x_spacing

    for j, sw in enumerate(sorted(switches)):
        pos[sw] = (x_center + (j-0.5)*0.5, 4)

# AGGREGATION 

agg_to_bb = {}
for u, v in G.edges():
    if u in backbone_nodes and v in aggregation_nodes:
        agg_to_bb[v] = u.split("_")[0]

agg_groups = {bb: [] for bb in bb_groups}
for a in aggregation_nodes:
    agg_groups[agg_to_bb[a]].append(a)

# curva global (arco)
total_aggs = len(aggregation_nodes)
R = 3.5

for i, a in enumerate(sorted(aggregation_nodes)):
    theta = math.pi * (i / (total_aggs - 1))  # arco (no círculo completo)

    x = R * math.cos(theta)
    y = 2 + 0.8 * math.sin(theta)

    pos[a] = (x, y)

# ========================
# EDGE (robusto + dual-homing)
# ========================

for e in range(n_edge):
    e_id = f"e{e}"
    sw1, sw2 = f"{e_id}_sw1", f"{e_id}_sw2"

    # aggregations padres de cada switch
    parents_sw1 = [u for u in G.predecessors(sw1) if u in aggregation_nodes]
    parents_sw2 = [u for u in G.predecessors(sw2) if u in aggregation_nodes]

    if parents_sw1 and parents_sw2:
        a1 = parents_sw1[0]
        a2 = parents_sw2[0]

        x1, y1 = pos[a1]
        x2, y2 = pos[a2]

        # punto medio entre aggregations
        x_mid = (x1 + x2) / 2
        y_mid = min(y1, y2) - 1.2

        # separar ligeramente los switches
        pos[sw1] = (x_mid - 0.25, y_mid)
        pos[sw2] = (x_mid + 0.25, y_mid)

# PGW

for pgw in pgw_nodes:
    parent = list(G.predecessors(pgw))[0]
    if parent in pos:
        x, y = pos[parent]
        pos[pgw] = (x, y - 1)

# WAN

for wan in wan_nodes:
    edge_id = "e" + wan.replace("wan", "")

    pgw1 = f"{edge_id}_pgw1"
    pgw2 = f"{edge_id}_pgw2"

    if pgw1 in pos and pgw2 in pos:
        x = (pos[pgw1][0] + pos[pgw2][0]) / 2
        y = pos[pgw1][1] - 1.2
        pos[wan] = (x, y)

# DIBUJO

plt.figure(figsize=(11, 9))

nx.draw_networkx_nodes(G, pos, nodelist=[internet], node_color="black", node_size=900, label="internet")

nx.draw_networkx_nodes(G, pos, nodelist=backbone_nodes, node_color="#e57373", node_size=1200, label="backbone")
nx.draw_networkx_nodes(G, pos, nodelist=aggregation_nodes, node_color="#e6d96a", node_size=1200, label="aggregation")
nx.draw_networkx_nodes(G, pos, nodelist=edge_nodes, node_color="#a8d0df", node_size=800, label="edge")
nx.draw_networkx_nodes(G, pos, nodelist=pgw_nodes, node_color="#90caf9", node_size=700, label="pgw")
nx.draw_networkx_nodes(G, pos, nodelist=wan_nodes, node_color="#b0bec5", node_size=900, label="wan")

nx.draw_networkx_edges(G, pos, arrows=False, width=1.5, alpha=0.6)
nx.draw_networkx_labels(G, pos, font_size=8)

plt.title("Fig8c topology (clean hierarchical layout)")
plt.legend()
plt.axis("off")
plt.tight_layout()
plt.show()