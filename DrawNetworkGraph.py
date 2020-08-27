import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import json

with open('similarity_matrix.json', 'r') as f:
    data = json.load(f)
G = nx.Graph()
rows = len(data)
cols = len(data[0])
count = 0
ls = []
for i in range(rows):
    G.add_node(i)
    for j in range(i+1, cols):
        if data[i][j] > 50:
            G.add_edge(i, j, weight=data[i][j])
nx.draw(G,
        pos = nx.spectral_layout(G),
        node_color = 'b',
        edge_color = 'r',
        font_size =18,
        with_labels = True,
        node_size =10)
nx.write_gexf(G, 'NetworkGraphForGephi.gexf')