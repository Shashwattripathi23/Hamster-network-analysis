import random

import networkx as nx
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

random.seed(42)

nodes = pd.read_csv("hamster-nodes.tsv", sep="\t", quotechar='"', skipinitialspace=True)
edges = pd.read_csv("hamster-edges.tsv", sep="\t", header=None, names=["u", "v"])

# Clean string attributes (e.g. " IL" -> "IL"); empty strings -> missing
for c in nodes.select_dtypes(include="object").columns:
    nodes[c] = nodes[c].str.strip().replace("", pd.NA)

join_year = nodes.set_index("Id")["joined_year"].to_dict()

# Drop self-loops/duplicates and edges with endpoints missing from the node list
edges = edges[edges.u != edges.v]
edges = edges[edges.u.isin(join_year) & edges.v.isin(join_year)]
edges = edges.assign(a=edges[["u", "v"]].min(axis=1), b=edges[["u", "v"]].max(axis=1))
edges = edges.drop_duplicates(["a", "b"])[["a", "b"]].rename(columns={"a": "u", "b": "v"})

# Edge exists from the later of the two endpoints' join years
edges["year"] = [max(join_year[u], join_year[v]) for u, v in zip(edges.u, edges.v)]

# Full (2011) graph with node attributes
G = nx.Graph()
G.add_nodes_from((r.Id, r._asdict()) for r in nodes.itertuples(index=False))
G.add_edges_from((r.u, r.v, {"year": r.year}) for r in edges.itertuples(index=False))

YEARS = list(range(2004, 2012))


def snapshot(year):
    """Graph with all nodes joined and edges existing up to and including `year`."""
    H = nx.Graph()
    H.add_nodes_from((n, d) for n, d in G.nodes(data=True) if d["joined_year"] <= year)
    H.add_edges_from((u, v) for u, v, d in G.edges(data=True) if d["year"] <= year)
    return H

def showGraph(G, year=None):
    """Draw the graph with node colors based on joined_year."""

    plt.figure(figsize=(8, 8))
    pos = nx.spring_layout(G, seed=42)
    cmap = mpl.colormaps["plasma"].resampled(len(YEARS))
    node_colors = [cmap(YEARS.index(d["joined_year"])) for _, d in G.nodes(data=True)]
    nx.draw(G, pos, node_color=node_colors, with_labels=False, node_size=50)
    if year is not None:
        plt.title(f"Graph snapshot for year {year}")
    plt.show()


snapshots = {y: snapshot(y) for y in YEARS}

if __name__ == "__main__":
    print("nodes columns:", list(nodes.columns))
    print("joined_year range:", nodes.joined_year.min(), nodes.joined_year.max())
    print(f"Full graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    for y, H in snapshots.items():
        print(y, H.number_of_nodes(), H.number_of_edges())
    # seeing how a grapgh looks like 
    showGraph(snapshots[2004], year=2004)
    
