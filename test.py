import networkx as nx
from networkx.classes.coreviews import AdjacencyView
from networkx.drawing.nx_pydot import graphviz_layout
import matplotlib.pyplot as plt
import pydot

graph = {
    'A' : ['B','C'],
    'B' : ['D', 'E'],
    'C' : ['F'],
    'D' : [],
    'E' : ['F'],
    'F' : []
}

visited = set() # Set to keep track of visited nodes.
nodes = []
def dfs(visited, graph, node):
    if node not in visited:
        nodes.append(node)
        visited.add(node)
        for neighbour in graph[node]:
            dfs(visited, graph, neighbour)


dfs(visited, graph, 'A')
print(nodes)
edges = []
i = 0
while i < len(nodes) - 1:
    edges.append((nodes[i],nodes[i+1]))
    i += 1

print(edges)
# Create graph
G = nx.Graph()
G.add_edges_from(edges)

# aaa = G.nodes['A']
# for key, value in graph.items():
#     tree_edges = list(G.edges([key]))
#     original_edges = []
#     for o in value:
#         original_edges.append((key,o))

#     back_edge = set(original_edges) - set(tree_edges)
#     for b in back_edge:
#         [_ , to] = b
#         G.add_edge(key,to)

# print(G.edges(['A']))

layout = graphviz_layout(G, prog="dot")
nx.draw(G, layout, with_labels=True)
plt.show()