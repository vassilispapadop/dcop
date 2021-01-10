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
def getParent(T, node, pseudo=False):
    c = 'b' if pseudo == False else 'r'
    # get all predecessors of current node 'node'
    predecessors = [n for n in T.adj[node] if n < node]
    # iterate through predecessors and get true parent, predecessors might hold pseudo parents
    for p in predecessors:
        edge_color = T.adj[node][p]['color']
        if edge_color == c:
            return T.nodes(data=True)[p]

    return None
# returns leaves of tree
def getLeafNodes(T):
    leaves = []
    for n in T.nodes():
        [true_children, pseudo_children] = getChildren(T,n)
        if len(true_children + pseudo_children) == 0:
            leaves.append(T.nodes(data=True)[n])

    # print('')
    # print('----------------Tree leaves are:----------------')
    # for l in leaves:
    #     l['attributes'].printNode()
    return leaves

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
                compute_util_matrix(G.nodes(data=True)[ids[i]]['attributes'], 
                                        G.nodes(data=True)[ids[next]]['attributes'], 
                                            meetingId)
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
        [p, c] = edge
        p_attributes = T.nodes(data=True)[p]['attributes']
        c_attributes = T.nodes(data=True)[c]['attributes']
        commonMeetings = u.intersection(p_attributes.meetings, c_attributes.meetings)
        for key in commonMeetings:
            compute_util_matrix(p_attributes, c_attributes, key)

    return T

def getNodes(T):
    return T.nodes(data=True)

def compute_util_matrix(parent, child, meetingId):
    childUtility = child.meetings[meetingId]
    parentUtility = parent.meetings[meetingId]
    # construct a SLOTS X SLOTS matrix
    UTILMatrix = np.zeros(shape=(u.TIME_SLOTS, u.TIME_SLOTS))

    for i in range(0,u.TIME_SLOTS):
        for j in range(0,u.TIME_SLOTS):
            UTILMatrix[i][j] = max(childUtility * child.preference[j], 
                        parentUtility * parent.preference[j])
            # if i == j:
            #     UTILMatrix[i][j] = - 1
            # else:
            #     UTILMatrix[i][j] = max(childUtility * child.preference[j], 
            #                             parentUtility * parent.preference[j])
    MSG = {
        'withParentId': parent.id, 
        'meetingId':meetingId, 
        'matrix': UTILMatrix
    }
    child.addRelation(MSG)
    return UTILMatrix   