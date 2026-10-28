
import random
from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from hamster import YEARS, snapshots

random.seed(56)
N_SOURCES = 300 


def avg_distance(H, k=N_SOURCES):

    giant = H.subgraph(max(nx.connected_components(H), key=len))
    src = random.sample(list(giant), min(k, giant.number_of_nodes()))
    tot = cnt = 0
    for s in src:
        d = nx.single_source_shortest_path_length(giant, s)
        tot += sum(d.values())
        cnt += len(d) - 1
    return tot / cnt


rows = []
for y in YEARS:
    H = snapshots[y]
    n, m = H.number_of_nodes(), H.number_of_edges()
    giant = max(nx.connected_components(H), key=len)
    deg = [d for _, d in H.degree()]
    rows.append({
        "year": y,
        "nodes": n,
        "edges": m,
        "avg_degree": 2 * m / n,
        "max_degree": max(deg),
        "density": nx.density(H),
        "components": nx.number_connected_components(H),
        "giant_size": len(giant),
        "giant_frac": len(giant) / n,
        "avg_clustering": nx.average_clustering(H),
        "transitivity": nx.transitivity(H),
        "avg_distance": avg_distance(H),
    })

df = pd.DataFrame(rows).set_index("year")
pd.set_option("display.width", 200)
print(df.round(4))
df.round(4).to_csv("q21stats.csv")

# degree dist 
fig, ax = plt.subplots(figsize=(6, 4.5))
cmap = plt.get_cmap("magma", len(YEARS))
for i, y in enumerate(YEARS):
    c = Counter(d for _, d in snapshots[y].degree())
    ks = np.array(sorted(c))
    pk = np.array([c[k] for k in ks]) / snapshots[y].number_of_nodes()
    ax.loglog(ks[ks > 0], pk[ks > 0], ".", color=cmap(i), label=str(y), alpha=0.8)
ax.set_xlabel("degree k")
ax.set_ylabel("P(k)")
ax.legend(title="snapshot", fontsize=8)
fig.tight_layout()
fig.savefig("q21degdist.png", dpi=200)

# stats over time
fig, axs = plt.subplots(2, 3, figsize=(12, 6.5))
series = [("nodes", "Nodes"), ("edges", "Edges"), ("avg_degree", "Average degree"),
          ("avg_clustering", "Avg. clustering coeff."), ("avg_distance", "Avg. distance (giant)"),
          ("density", "Density")]
magma = plt.get_cmap("magma", len(series) + 2)
for i, (ax, (col, title)) in enumerate(zip(axs.ravel(), series)):
    ax.plot(df.index, df[col], "o-", color=magma(i))
    ax.set_title(title)
    ax.set_xlabel("year")
fig.tight_layout()
fig.savefig("q21stats.png", dpi=200)
