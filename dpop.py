import networkx as nx
from networkx.classes.coreviews import AdjacencyView
import matplotlib.pyplot as plt
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
import numpy as np
import json
from NodeAttributes import NodeAttributes
import Utilities as u
import Pseudotree as ptree

def compute_util_matrix(parent, child, meetingId):
    nodeUtility = child.meetings[meetingId]
    parentUtility = parent.meetings[meetingId]
    # construct a SLOTS X SLOTS matrix
    UTILMatrix = np.zeros(shape=(u.TIME_SLOTS, u.TIME_SLOTS))

    for i in range(0,u.TIME_SLOTS):
        for j in range(0,u.TIME_SLOTS):
            if i == j:
                UTILMatrix[i][j] = - 1
            else:
                UTILMatrix[i][j] = max(nodeUtility * child.preference[j], 
                                        parentUtility * parent.preference[j])
    return UTILMatrix                                    

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
            n_attributes.printNode()
            return

        # do not add same parent 
        if parent not in parents:
            parents.append(parent)
        
        p_attributes = parent['attributes']

        # find common meetings between those two
        commonMeetings = u.intersection(n_attributes.meetings, p_attributes.meetings)
        for key in commonMeetings:
            UTILMatrix = compute_util_matrix(p_attributes, n_attributes, key)          
            # find per column maximum
            MSG = {
                    'childId': n_attributes.id, 
                    'meetingId':key, 
                    'util': np.array(np.max(UTILMatrix,axis=0))
            }
            #  update parent msg (send message to parent)
            p_attributes.addUtilMsg(MSG)
            print('Update parent with id: ', p_attributes.id, 'from child with id: ', n_attributes.id)
            p_attributes.printNode()
            # print(UTILMatrix)
    
    # compute join for each parent
    # for p in parent:
    #     aaa = p['attributes']
    #     p['attributes'].joinUtilMsgs()

    compute_utils(T,parents)

def main():
    # 1st row: Number of agents;Number of meetings;Number of variables

    # Open file 
    # inputFilename = 'constraint_graphs/dcop_constraint_graph'
    inputFilename = 'constraint_graphs/dcop_simple'
    # inputFilename = 'constraint_graphs/DCOP_Problem_40'
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

    # Print nodes
    u.printNodes(G)

    # Add edges and keep track of back-edges
    [G, back_edges_candidates] = ptree.addEdges(G, agents, nrMeetings)

    # Convert to spanning tree
    T = nx.maximum_spanning_tree(G)
    # T = nx.dfs_successors(G, 0)

    # Create back edges
    T = ptree.addBackEdges(T, back_edges_candidates)

    layout = graphviz_layout(T, prog="dot")

    edges = T.edges()
    colors = [T[u][v]['color'] for u,v in edges]
    #print(list(nx.bfs_edges(T,3)))
    compute_utils(T, ptree.getLeafNodes(T))
    
    # nx.draw(T, layout, edge_color=colors, with_labels=True)
    # plt.show()

if __name__ == '__main__':
    main()	
