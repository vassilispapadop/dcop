import networkx as nx
from networkx.classes.coreviews import AdjacencyView
import matplotlib.pyplot as plt
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
import numpy as np
import json
from NodeAttributes import NodeAttributes
import Utilities as u


# return all children including pseudo-children
# note, T is sorted meaning higher node_id is lower in tree-depth
def getChildren(T, node):
    true_children = []
    pseudo_children = []
    successors = [n for n in T.adj[node] if n > node]
    for s in successors:
        child_node = T.nodes(data=True)[s]
        edge_color = T.adj[node][s]['color']
        true_children.append(child_node) if edge_color == 'b' else pseudo_children.append(child_node)

    return true_children, pseudo_children

#NOTE: check whether we need to distiguish between true and psedo parents
def getParent(tree, node, pseudo=False):
    c = 'b' if pseudo == False else 'r'
    # get all predecessors of current node 'node'
    predecessors = [n for n in tree.adj[node] if n < node]
    # iterate through predecessors and get true parent, predecessors might hold pseudo parents
    for p in predecessors:
        edge_color = tree.adj[node][p]['color']
        if edge_color == c:
            return tree.nodes(data=True)[p]

    return None

def getLeafNodes(tree):
    leaves = []
    for n in tree.nodes():
        [true_children, pseudo_children] = getChildren(tree,n)
        if len(true_children + pseudo_children) == 0:
            leaves.append(tree.nodes(data=True)[n])

    print('')
    print('----------------Tree leaves are:----------------')
    for l in leaves:
        l['attributes'].print_node()
    return leaves

def compute_utils(T, nodes):

    # compute utility from each node and pass it to parents
    for node in nodes:
        n_attributes = node['attributes']
        print('')
        print('----------------Computing utility for node: ', n_attributes.id, '----------------')
        # n_attributes.print_node()

        # find parent of current node
        parent = getParent(T, n_attributes.id, pseudo=False)
        if parent == None:
            print('Node is root of tree, stop utility propagation')
            break
        
        p_attributes = parent['attributes']

        # find common meetings between those two
        commonMeetings = u.intersection(n_attributes.meetings, p_attributes.meetings)
        for key in commonMeetings:
            nodeUtility = n_attributes.meetings[key]
            parentUtility = p_attributes.meetings[key]
            # construct a SLOTS X SLOTS matrix
            UTILMatrix = np.zeros(shape=(u.TIME_SLOTS, u.TIME_SLOTS))

            for i in range(0,u.TIME_SLOTS):
    	        for j in range(0,u.TIME_SLOTS):
                    if i == j:
                        UTILMatrix[i][j] = - 1
                    else:
                        UTILMatrix[i][j] = max(nodeUtility * n_attributes.preference[j], 
                                                parentUtility * p_attributes.preference[j])
            
            # find per column maximum
            MSG = {
                    'childId': n_attributes.id, 
                    'meetingId':key, 
                    'util': np.array(np.max(UTILMatrix,axis=0))
            }
            #  update parent msg (send message to parent)
            p_attributes.addUtilMsg(MSG)
            # p_attributes.print_node()
            print(UTILMatrix)

def addNodes(G, agents):
    print ('----------------Adding nodes----------------')
    for agent in agents:
        attr = NodeAttributes(agent['id'], agent['meetings'], agent['preference'])
        G.add_node(agent['id'], attributes=attr)
    return G

def addEdges(G, agents, nrMeetings):
    print('')
    print ('----------------Adding edges and keep track of back edges----------------')
    back_edges_candidates = []
    added = []
    for meetingId in range(0, nrMeetings):
        ids = u.meetingSharedBy(agents, meetingId)
        i = 0
        while i < len(ids) -1 :
            next = i + 1
            e = (ids[i], ids[next])
            # since there is already an edge skip
            if G.has_edge(*e):
                i += 1
                continue

            if len(G.adj[ids[i]]) < 2:
                G.add_edge(*e,  color='b')
                added.append(e)
            else:
                back_edges_candidates.append([*e])   

            i += 1

    return G, back_edges_candidates

def addBackEdges(T, back_edges_candidates):
    print('')
    print ('----------------Adding back edges candidates----------------')
    print(back_edges_candidates)
    back_edges_candidates.sort()
    for edge in back_edges_candidates:
        has_edge = T.has_edge(*edge)
        if has_edge:
            continue

        [parent, _] = edge
        color = 'r'
        [true, pseudo] = getChildren(T, parent)
        if len(true+pseudo) < 2:
            color = 'b'

        T.add_edge(*edge, color = color)

    return T

def main():
    # 1st row: Number of agents;Number of meetings;Number of variables

    # Open file 
    # inputFilename = 'dcop_constraint_graph'
    inputFilename = 'dcop_simple'
    # inputFilename = 'DCOP_Problem_40'
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
    G = addNodes(G, agents)

    # Print nodes
    u.printNodes(G)

    # Add edges and keep track of back-edges
    [G, back_edges_candidates] = addEdges(G, agents, nrMeetings)

    # Convert to spanning tree
    T = nx.maximum_spanning_tree(G)
    # T = nx.dfs_successors(G, 0)

    # Create back edges
    T = addBackEdges(T, back_edges_candidates)

    layout = graphviz_layout(T, prog="dot")

    edges = T.edges()
    colors = [T[u][v]['color'] for u,v in edges]
    #print(list(nx.bfs_edges(T,3)))
    compute_utils(T, getLeafNodes(T))

    # nx.draw(T, layout, edge_color=colors, with_labels=True)
    # plt.show()

if __name__ == '__main__':
    main()	
