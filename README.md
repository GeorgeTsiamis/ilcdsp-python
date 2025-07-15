# ILCDSP – Iterative Local Community Detection

This repository contains a Python implementation of the ILCDSP algorithm (Xia et al., 2014) for local community detection in graphs.

## Requirements

- Python 3.7 or higher  
- `networkx>=2.5`  

(Optional, if you want to handle very large graphs in compressed form)  
- `python-igraph` (for memory‐efficient loading of large graphs)  
- `gzip` (built‑in)

Install dependencies with:

```bash
pip install networkx
# pip install python-igraph   # if you plan to use igraph

