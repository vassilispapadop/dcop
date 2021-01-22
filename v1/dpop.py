import networkx as nx
from networkx.classes.coreviews import AdjacencyView
import matplotlib.pyplot as plt
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
import numpy as np
import json
from NodeAttributes import NodeAttributes
import Utilities as u
import pseudotree as ptree
                                 
def compute_utils(T, nodes):
    # compute utility from each node and pass it to parents
    # keep track of parents
    parents = []
    for node in nodes:
        n_attributes = node['attributes']
        print('')
        print('----------------Computing utility for node: ', n_attributes.id, '----------------')
        n_attributes.joinUtilMsgs()
        # find parent of current node
        parent = ptree.getParent(T, n_attributes.id, pseudo=False)
        if parent == None:
            print('Node is root of tree, stop Util propagation and proceed with Value propagation')
            # n_attributes.printNode()
            return

        # do not add same parent 
        if parent not in parents:
            parents.append(parent)
        
        p_attributes = parent['attributes']

        # find common meetings between those two
        commonMeetings = u.intersection(n_attributes.meetings, p_attributes.meetings)
        for key in commonMeetings:
            msg = {
                'meetingId': key,
                'childId': n_attributes.id,
                'util': np.array(np.max(n_attributes.relations[p_attributes.id]['matrix'], axis=0))
            }
            p_attributes.addUtilMsg(msg)

    compute_utils(T,parents)

def main():
    # 1st row: Number of agents;Number of meetings;Number of variables

    # Open file 
    # inputFilename = 'constraint_graphs/dcop_constraint_graph'
    # inputFilename = 'constraint_graphs/dcop_simple'
    inputFilename = 'constraint_graphs/DCOP_Problem_50'
    input = open(inputFilename, 'r') 

    # Read first line
    [nrAgents, nrMeetings, nrVars] = u.readLine(input)

    # Read agents/variables/constraints
    agents = u.readMeetings(input, nrVars)

    # Read preferences per agent
    agents = u.readPreferences(input, agents, nrAgents)

    # Create graph
    G = nx.Graph()
    
    # Add agents/nodes
    G = ptree.addNodes(G, agents)

    # Add edges and keep track of back-edges
    [G, back_edges_candidates] = ptree.addEdges(G, agents, nrMeetings)

    # Convert to spanning tree
    T = nx.maximum_spanning_tree(G)
    # T = nx.dfs_successors(G, 0)

    # Create back edges
    T = ptree.addBackEdges(T, back_edges_candidates)

    # Print nodes
    print('----------------ALL NODES----------------')
    # u.printNodes(T)


    layout = graphviz_layout(T, prog="dot")

    edges = T.edges()
    colors = [T[u][v]['color'] for u,v in edges]
    #print(list(nx.bfs_edges(T,3)))
    compute_utils(T, ptree.getLeafNodes(T))
    
    nx.draw(T, layout, edge_color=colors, with_labels=True)
    plt.show()

        # Print nodes
    print('----------------ALL NODES----------------')
    u.printNodes(T)

if __name__ == '__main__':
    main()	
