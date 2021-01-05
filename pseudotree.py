import networkx as nx
from networkx.classes.coreviews import AdjacencyView
import matplotlib.pyplot as plt
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
import numpy as np

TIME_SLOTS = 3

def readLine(input):
    try:
        [a, b, c] = input.readline().strip().split(';')
    except ValueError as e:
        return []

    return int(a), int(b), int(c)

def printNodes(G):
    for id, attr in G.nodes(data=True):
        print('Node: ', id, ' Meetings: ', attr['meetings'], ' Preferences: ', attr['preference'])

def readPreferences(input, agents, nrAgents):
    for a in range(nrAgents):
        for slot in range(TIME_SLOTS):
            try:
                [id,_,pref] = readLine(input)
                agents[id]['preference'].append(pref)
            except IndexError as e:
                print('Agent ID: ', id,' not found')
                break
            except ValueError as ve:
                print ('Value Error, AgentId:', id, ' not found')
                break;

    return agents

def readMeetings(input, vars):
    agents = []
    for i in range(0, vars):
        [agentId, meetingId, meetingUtil] = readLine(input)
        agent = {
                    'id': agentId,  
                        'meetings': {
                            meetingId: meetingUtil
                        },
                        'preference': []
                }
        index = search(agentId, agents)
        if index > -1:
            update_meeting = agents[index]
            update_meeting['meetings'].update({meetingId:meetingUtil})
        else:
            agents.append(agent)

    # agents.sort(key=sortBy, reverse=True)
    agents.sort(key=sortBy)
    return agents

def sortBy(e):
    return e['id']
    #   return len(e['meetings'])

# list comprehension
def search(id, agents):
    index = 0
    while index < len(agents):
        if agents[index]['id'] == id:
            return index
        index += 1
    return -1        

# finds all agents that share meeting based on meetingId    
def meetingSharedBy(agents, meetingId):
    sharedBy = []
    for item in agents:
        for m_id in item['meetings'].keys():
            if m_id == meetingId:
                sharedBy.append(item['id'])
                break

    sharedBy.sort()
    return sharedBy

# return all children including pseudo-children
# note, T is sorted meaning higher node_id is lower in tree-depth
def getChildren(tree, node):
    neighbors = tree.adj[node]
    true_children = []
    pseudo_children = []
    for e in neighbors:
        edge_color = tree.adj[node][e]['color']
        if e > node:
            if edge_color == 'b':
                true_children.append(e)
            else:
                pseudo_children.append(e)

    return true_children, pseudo_children

def getParents(tree, node):
    neighbors = tree.adj[node]
    true_parent = []
    pseudo_parent = []
    for e in neighbors:
        edge_color = tree.adj[node][e]['color']
        if e < node:
            if edge_color == 'b':
                true_parent.append(e)
            else:
                pseudo_parent.append(e)

    return true_parent, pseudo_parent

def getLeafNodes(tree):
    leaves = []
    for n in tree.nodes():
        [true_children, pseudo_children] = getChildren(tree,n)
        if len(true_children + pseudo_children) == 0:
            leaves.append(n)

    return leaves
    
def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2)) 

def compute_utils(tree, leaves, agents):
    # compute utility from each leaf node and pass it to parents
    for leaf in leaves:
        # total_utility = np.zeros( (TIME_SLOTS, TIME_SLOTS) )
        print('Computing utility for node: ', leaf)
        # find parent of current leaf
        [parent, _] = getParents(tree, leaf)
        if len(parent) == 0:
            print('Node is root of tree, stop utility propagation')
            break
        
        leaf_agent = agents[leaf]
        parent_agent = agents[parent[0]]
        leaf_pref = leaf_agent['preference']

        for key, value in leaf_agent['meetings'].items():
            leaf_utility = value
            parent_utility = parent_agent['meetings'][key]
            parent_pref = parent_agent['preference']

            leaf_matrix = np.matrix(leaf_pref) * leaf_utility
            parent_matrix = np.transpose(np.matrix(parent_pref) * parent_utility)

            print (np.matmul(parent_matrix, leaf_matrix))


def addNodes(G, agents):
    for agent in agents:
        G.add_node(agent['id'], meetings=agent['meetings'], preference=agent['preference'])

    return G

def main():
    # 1st row: Number of agents;Number of meetings;Number of variables

    # Open file 
    # inputFilename = 'dcop_constraint_graph'
    inputFilename = 'dcop_simple'
    # inputFilename = 'DCOP_Problem_40'

    input = open(inputFilename, 'r') 

    # Read first line
    [nrAgents, nrMeetings, nrVars] = readLine(input)

    # Read agents/variables/constraints
    agents = readMeetings(input, nrVars)

    # Read preferences per agent
    agents = readPreferences(input, agents, nrAgents)

    # Create graph
    G = nx.Graph()
    
    # Add agents/nodes
    G = addNodes(G, agents)

    # Print nodes
    printNodes(G)

    # Add edges and keep track of back-edges
    back_egdes = []
    for meetingId in range(0, nrMeetings):
        ids = meetingSharedBy(agents, meetingId)
        i = 0
        while i < len(ids) -1 :
            next = i + 1
            e = (ids[i], ids[next])
            if len(G.adj[ids[i]]) < 2:
                G.add_edge(*e,  color='b')
            else:
               back_egdes.append([*e])    

            i += 1
    
    # Convert to spanning tree
    T = nx.minimum_spanning_tree(G)
    # T = nx.dfs_successors(G, 0)
    # Create back edges
    back_egdes.sort()
    for edge in back_egdes:
        [parent, _] = edge
        color = 'r'
        [true, pseudo] = getChildren(T, parent)
        if len(true+pseudo) < 2:
            color = 'b'

        T.add_edge(*edge, color = color)

    print('back-edges: ', back_egdes)

    layout = graphviz_layout(T, prog="dot")

    edges = T.edges()
    colors = [T[u][v]['color'] for u,v in edges]

    nx.draw(T, layout, edge_color=colors, with_labels=True)

    [trueNodes, pseudoNodes] = getChildren(T,3)
    print('true children: ',trueNodes, 'pseudo children: ', pseudoNodes)
    [trueParent, pseudoParent] = getParents(T,3)
    print('true parent: ',trueParent, 'pseudo parent: ', pseudoParent)

    leaves = getLeafNodes(T)
    print(leaves)
    compute_utils(T, leaves, agents)
    plt.show()

if __name__ == '__main__':
    main()	
