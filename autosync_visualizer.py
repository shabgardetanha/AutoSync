import json
from pyvis.network import Network
import networkx as nx

# Load dependency graph
with open("autosync_graph_snapshot.json", "r", encoding="utf-8") as f:
    snapshot = json.load(f)

nodes_data = snapshot["nodes"]
edges_data = snapshot["edges"]

G = nx.DiGraph()

# Add nodes
for node_id, node in nodes_data.items():
    title = f"{node_id}\nType: {node['type']}\nGaps: {', '.join(node['gaps'])}"
    color = "green"
    if node["gaps"]:
        color = "red"
    G.add_node(node_id, label=node_id.split("/")[-1], title=title, color=color)

# Add edges
for edge in edges_data:
    if edge["to"] in nodes_data:
        G.add_edge(edge["from"], edge["to"])

# PyVis visualization
net = Network(height="1000px", width="100%", directed=True)
net.from_nx(G)
net.show("autosync_dependency_map.html")
print("Interactive dependency map saved as autosync_dependency_map.html")
