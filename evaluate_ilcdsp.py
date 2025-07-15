
---

**`evaluate_ilcdsp.py`**

```python
#!/usr/bin/env python3
"""
evaluate_ilcdsp.py

Python implementation of ILCDSP (Iterative Local Community Detection
with Seed Propagation) using NetworkX. Supports plain-text or gzipped
edge lists and community files.
"""

import argparse
import gzip
import random
import networkx as nx
from collections import defaultdict

def load_graph(path, gz=False):
    """
    Load an undirected graph from an edge list.
    If gz=True, the file is read with gzip.
    """
    G = nx.Graph()
    opener = gzip.open if gz else open
    mode = 'rt' if gz else 'r'
    with opener(path, mode) as f:
        for line in f:
            if line.startswith('#'):
                continue
            u, v = map(int, line.split())
            if u != v:
                G.add_edge(u, v)
    return G

def load_communities(path, gz=False):
    """
    Load ground-truth community assignments.
    Returns:
      node_to_comm: dict mapping node -> community_id
      comms: dict mapping community_id -> set of nodes
    """
    node_to_comm = {}
    comms = defaultdict(set)
    opener = gzip.open if gz else open
    mode = 'rt' if gz else 'r'
    with opener(path, mode) as f:
        for cid, line in enumerate(f):
            members = list(map(int, line.split()))
            for node in members:
                node_to_comm[node] = cid
                comms[cid].add(node)
    return node_to_comm, comms

def compute_local_density_score(G, community, node):
    """
    LDS = (# edges from node into current community) / degree(node)
    """
    neighbors = set(G.neighbors(node))
    k_in = len(neighbors & community)
    k = G.degree[node]
    return k_in / k if k > 0 else 0.0

def compute_conductance(G, community):
    """
    Conductance = cut(S, V\S) / min(vol(S), vol(V\S))
    where cut is the # edges crossing the boundary,
    and vol(S) = sum of degrees in S.
    """
    cut_edges = sum(1 for u,v in G.edges() if (u in community) ^ (v in community))
    vol_S = sum(G.degree[n] for n in community)
    vol_bar = sum(G.degree[n] for n in G.nodes() if n not in community)
    denom = min(vol_S, vol_bar)
    return cut_edges / denom if denom > 0 else 1.0

def ilcdsp(G, seeds, max_iter=None):
    """
    Run ILCDSP starting from given seed nodes.
    Greedily add the neighbor with highest LDS if it reduces conductance.
    """
    community = set(seeds)
    best_cond = compute_conductance(G, community)
    boundary = set().union(*(G.neighbors(s) for s in seeds)) - community

    iterations = 0
    while boundary and (max_iter is None or iterations < max_iter):
        # Compute LDS for each boundary node
        scores = {v: compute_local_density_score(G, community, v) for v in boundary}
        v_star = max(scores, key=scores.get)
        new_comm = community | {v_star}
        new_cond = compute_conductance(G, new_comm)
        if new_cond < best_cond:
            community = new_comm
            best_cond = new_cond
            # update boundary
            boundary |= set(G.neighbors(v_star)) - community
            boundary.discard(v_star)
            iterations += 1
        else:
            break

    return community

def evaluate(G, node_to_comm, comms, num_seeds, seed_strategy='random'):
    """
    Evaluate average precision, recall and F1 over multiple seeds.
    """
    deg = dict(G.degree())

    # Select seeds
    if seed_strategy == 'random':
        eligible = [n for n in G.nodes() if n in node_to_comm]
        seeds = random.sample(eligible, num_seeds)
    elif seed_strategy == 'maxdeg':
        # one seed per community: highest-degree node
        seeds = []
        for cid, members in comms.items():
            seed = max((n for n in members if n in G), key=lambda n: deg[n], default=None)
            if seed is not None:
                seeds.append(seed)
        if len(seeds) > num_seeds:
            seeds = random.sample(seeds, num_seeds)
    else:
        raise ValueError("Invalid seed_strategy")

    precisions = []
    recalls = []
    f1s = []
    for s in seeds:
        true_set = comms[node_to_comm[s]]
        detected = ilcdsp(G, [s])
        tp = len(detected & true_set)
        p = tp / len(detected) if detected else 0.0
        r = tp / len(true_set) if true_set else 0.0
        f1 = 2*p*r/(p+r) if (p+r) else 0.0
        precisions.append(p)
        recalls.append(r)
        f1s.append(f1)

    return sum(precisions)/len(precisions), sum(recalls)/len(recalls), sum(f1s)/len(f1s)

def main():
    parser = argparse.ArgumentParser(description="Evaluate ILCDSP on a graph")
    parser.add_argument("--graph",    required=True, help="Path to edge list file")
    parser.add_argument("--labels",   required=True, help="Path to community labels file")
    parser.add_argument("--gz",       action="store_true", help="If inputs are gzip-compressed")
    parser.add_argument("--seeds",    type=int, default=20, help="Number of seeds")
    parser.add_argument("--strategy", choices=["random","maxdeg"], default="random",
                        help="Seed selection: random or maxdeg")
    args = parser.parse_args()

    print("Loading graph...")
    G = load_graph(args.graph, gz=args.gz)
    print(f"  Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

    print("Loading ground-truth communities...")
    node_to_comm, comms = load_communities(args.labels, gz=args.gz)

    random.seed(42)
    prec, rec, f1 = evaluate(G, node_to_comm, comms, args.seeds, args.strategy)

    print("\n=== RESULTS ===")
    print(f"Seeds:     {args.seeds} ({args.strategy})")
    print(f"Precision: {prec:.3f}")
    print(f"Recall:    {rec:.3f}")
    print(f"F1 score:  {f1:.3f}")

if __name__ == "__main__":
    main()
