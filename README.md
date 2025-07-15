# ILCDSP – Iterative Local Community Detection

This repository contains a Python implementation of the ILCDSP algorithm (Xia et al., 2014) for local community detection in graphs.

## Requirements

 Python 3.7 or higher  
- `networkx>=2.5`  

(Optional, if you want to handle very large graphs in compressed form)  
- `python-igraph` (for memory‐efficient loading of large graphs)  
- `gzip` (built‑in)

Install dependencies with:

```bash
pip install networkx
# pip install python-igraph   # if you plan to use igraph
```
## Usage
Clone the repo and run:

```bash
python evaluate_ilcdsp.py \
  --graph PATH/TO/EDGES_FILE \
  --labels PATH/TO/LABELS_FILE \
  [--gz] \
  [--seeds N] \
  [--strategy random|maxdeg]
```
## Arguments


- graph
Path to your edge list (plain text or .gz).

- labels
Path to your community file (each line: space‑separated node IDs).
 
- gz
Add this flag if your input files are gzip‑compressed.

- seeds
Number of seed nodes to sample (default: 20).

