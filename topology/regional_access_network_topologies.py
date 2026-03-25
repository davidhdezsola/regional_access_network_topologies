import random
import networkx as nx
from typing import List, Optional, Tuple

def _add_random_bipartite_edges(G: nx.DiGraph,src: List[str],tgt: List[str],p: float,min_deg_tgt: int = 1,max_deg_tgt: Optional[int] = None,rng: Optional[random.Random] = None,):
    """
    Adds random edges from 'src' to 'tgt' with probability 'p' and ensures that
    each node in 'tgt' has at least 'min_deg_tgt' incoming edges. Optionally,
    limits the maximum number of incoming edges for each node in 'tgt'.

    Parameters:
        G (nx.DiGraph): The directed graph to which edges will be added.
        src (List[str]): List of source nodes.
        tgt (List[str]): List of target nodes.
        p (float): Probability of adding an edge between a source and a target node.
        min_deg_tgt (int): Minimum number of incoming edges for each target node.
        max_deg_tgt (Optional[int]): Maximum number of incoming edges for each target node (optional).
        rng (Optional[random.Random]): Random number generator instance (optional).

    Returns:
        None
    """
    rng = rng or random.Random()

    for u in src:
        for v in tgt:
            if rng.random() < p:
                G.add_edge(u, v)

    for v in tgt:
        in_neighbors = list(G.predecessors(v))
        need = max(0, min_deg_tgt - len(in_neighbors))
        if need > 0:
            choices = src[:]  
            rng.shuffle(choices)
            for u in choices:
                if need == 0:
                    break
                if not G.has_edge(u, v):
                    G.add_edge(u, v)
                    need -= 1


def generate_topology_fig8a_single_agg_layer(internet: str='internet' ,n_edge: int = 30,n_agg: int = 2,n_backbone: int = 1,p_backbone_agg: float = 1.0,p_agg_edge: float = 0.25,edge_redundancy: int = 2,seed: int = 1) -> nx.DiGraph:
    """
    Generates a hierarchical network topology with a single aggregation layer
    . The topology consists of three layers: Backbone -> Aggregation -> Edge.

    Structure:
        - Each backbone node connects to exactly one aggregation node.
        - Aggregation nodes are interconnected.
        - Each edge node connects to 1..edge_redundancy aggregation nodes.

    Parameters:
        n_edge (int): Number of edge nodes.
        n_agg (int): Number of aggregation nodes.
        n_backbone (int): Number of backbone nodes.
        p_backbone_agg (float): Probability of connecting backbone nodes to aggregation nodes.
        p_agg_edge (float): Probability of connecting aggregation nodes to edge nodes.
        edge_redundancy (int): Number of aggregation nodes each edge node connects to.
        seed (int): Random seed for reproducibility.

    Returns:
        nx.DiGraph: The generated directed graph representing the topology.
    """
    rng = random.Random(seed)
    G = nx.DiGraph()

    backbone = [f"bb{i}" for i in range(n_backbone)]
    agg = [f"agg{i}" for i in range(n_agg)]
    edge = [f"e{i}" for i in range(n_edge)]
    internet = "internet"

    G.add_nodes_from(backbone, layer="backbone")
    G.add_nodes_from(agg, layer="agg")
    G.add_nodes_from(edge, layer="edge")
    G.add_node(internet, layer="internet")

    for bb in backbone:
        G.add_edge(internet, bb)
    for i, bb in enumerate(backbone):
        target_agg = agg[i % n_agg]
        G.add_edge(bb, target_agg)

    # agg <-> agg: conectarlos entre sí
    for i in range(n_agg):
        for j in range(i + 1, n_agg):
            G.add_edge(agg[i], agg[j])
            G.add_edge(agg[j], agg[i])

    # agg -> edge: esto sí sigue siendo aleatorio
    _add_random_bipartite_edges(
    G, agg, edge, p=p_agg_edge,
    min_deg_tgt=1, max_deg_tgt=edge_redundancy, rng=rng
)

    return G


def generate_topology_fig8c_aggregation_ring(internet: str='internet'  ,n_edge: int = 80,n_aggregation: int = 8,n_backbone: int = 2,p_aggregation_to_edge: float = 0.25,edge_uplinks_max: int = 2,seed: int = 1) -> nx.DiGraph:
    """
    Generates a hierarchical network topology with an ordered aggregation ring
    (Figure 8c structure). The topology consists of three layers: Backbone -> Aggregation -> Edge.

    Structure:
        - Each backbone node connects to exactly one aggregation node.
        - Aggregation nodes are connected in a ring structure.
        - Each edge node connects to 1..edge_redundancy aggregation nodes.

    Parameters:
        n_edge (int): Number of edge nodes.
        n_agg (int): Number of aggregation nodes.
        n_backbone (int): Number of backbone nodes.
        p_backbone_agg (float): Probability of connecting backbone nodes to aggregation nodes.
        p_agg_edge (float): Probability of connecting aggregation nodes to edge nodes.
        edge_redundancy (int): Number of aggregation nodes each edge node connects to.
        seed (int): Random seed for reproducibility.

    Returns:
        nx.DiGraph: The generated directed graph representing the topology.
    """
    rng = random.Random(seed)
    G = nx.DiGraph()

    if n_aggregation < 2:
        raise ValueError("Para un anillo, n_aggregation debe ser al menos 2.")

    if n_edge * edge_uplinks_max < n_aggregation:
        raise ValueError(
            "No es posible garantizar que cada aggregation tenga al menos un edge "
            "si n_edge * edge_uplinks_max < n_aggregation."
        )

    backbone = [f"bb{i}" for i in range(n_backbone)]
    aggregation = [f"agg{i}" for i in range(n_aggregation)]
    edge = [f"e{i}" for i in range(n_edge)]
    internet = "internet"
    
    G.add_node(internet, layer="internet")
    G.add_nodes_from(backbone, layer="backbone")
    G.add_nodes_from(aggregation, layer="aggregation")
    G.add_nodes_from(edge, layer="edge")

    for b in backbone:
        G.add_edge(internet, b)
    for i, b in enumerate(backbone):
        a = aggregation[i % n_aggregation]
        G.add_edge(b, a)

    #aggregation en anillo
    for i in range(n_aggregation):
        a1 = aggregation[i]
        a2 = aggregation[(i + 1) % n_aggregation]
        G.add_edge(a1, a2)
        G.add_edge(a2, a1)

   
    edge_parents = {e: set() for e in edge}

    #asegurar que cada aggregation tenga al menos un edge
    for i, a in enumerate(aggregation):
        e = edge[i % n_edge]
        if len(edge_parents[e]) < edge_uplinks_max:
            edge_parents[e].add(a)
        else:
            # buscar otro edge con hueco
            assigned = False
            for ee in edge:
                if len(edge_parents[ee]) < edge_uplinks_max:
                    edge_parents[ee].add(a)
                    assigned = True
                    break
            if not assigned:
                raise RuntimeError("No se pudo asignar un edge a cada aggregation.")

    #asegurar que cada edge tenga al menos un aggregation upstream
    for e in edge:
        if len(edge_parents[e]) == 0:
            a = rng.choice(aggregation)
            edge_parents[e].add(a)

    #añadir redundancia extra aleatoria sin superar edge_uplinks_max
    for e in edge:
        available = [a for a in aggregation if a not in edge_parents[e]]
        rng.shuffle(available)

        for a in available:
            if len(edge_parents[e]) >= edge_uplinks_max:
                break
            if rng.random() < p_aggregation_to_edge:
                edge_parents[e].add(a)

    for e, parents in edge_parents.items():
        for a in parents:
            G.add_edge(a, e)

    return G

