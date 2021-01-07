import networkx as nx
from networkx.classes.coreviews import AdjacencyView
import matplotlib.pyplot as plt
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
import numpy as np

TIME_SLOTS = 3

# utilities
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

def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2)) 

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
    for n, attr in tree.nodes(data=True):
        [true_children, pseudo_children] = getChildren(tree,n)
        if len(true_children + pseudo_children) == 0:
            leaves.append(tree.nodes(data=True)[n])

    print('Tree leaves are: ', leaves)
    return leaves

def sendMessage(T, parentId, UtilMsg):
    print('Updating parentId: ', parentId, ' from childId: ', UtilMsg['childId'])
    parentNode = T.nodes[parentId]
    parentNode['util_msgs'].update({UtilMsg['childId']: UtilMsg['msg']})
    print('Parent: ', parentId, ' ', parentNode['util_msgs'])

def compute_utils(T):
    # get leaves of tree
    leaves = getLeafNodes(T)

    # compute utility from each leaf node and pass it to parents
    for leaf in leaves:
        # total_utility = np.zeros( (TIME_SLOTS, TIME_SLOTS) )
        print('Computing utility for node: ', leaf)

        leafId=leaf['id']
        leafMeetings=leaf['meetings']
        leafPref=leaf['preference']

        # find parent of current leaf
        parent = getParent(T, leafId, pseudo=False)
        if parent == None:
            print('Node is root of tree, stop utility propagation')
            break
        
        parentMeetings=parent['meetings']
        parentPref=parent['preference']
        # find common meetings between those two
        commonMeetings = intersection(leafMeetings, parentMeetings)
        for key in commonMeetings:
            leafUtility = leafMeetings[key]
            parentUtility = parentMeetings[key]
            # construct a SLOTS X SLOTS matrix
            UTILMatrix = np.matmul(np.transpose(np.matrix(parentPref)) + parentUtility,
                             np.matrix(leafPref) + leafUtility)
            # main diagonal is -1 since no two meetings can be at the same time
            np.fill_diagonal(UTILMatrix, -1)
            # find per column maximum
            MSG = {'childId': leafId, 'msg': np.array(np.max(UTILMatrix,axis=0))}
            #  update parent msg (send message to parent)
            print(UTILMatrix, MSG)
            sendMessage(T, parent['id'], MSG)



def addNodes(G, agents):
    print ('Adding nodes')
    for agent in agents:
        G.add_node(agent['id'], id=agent['id'], meetings=agent['meetings'], 
                    preference=agent['preference'],
                    util_msgs={})
    return G

def addEdges(G, agents, nrMeetings):
    print ('Adding edges and keep track of back edges')
    back_edges_candidates = []
    added = []
    for meetingId in range(0, nrMeetings):
        ids = meetingSharedBy(agents, meetingId)
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
    print ('Adding back edges candidates', back_edges_candidates)
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
    inputFilename = 'dcop_constraint_graph'
    # inputFilename = 'dcop_simple'
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
   
    nx.draw(T, layout, edge_color=colors, with_labels=True)

    # [trueNodes, pseudoNodes] = getChildren(T,1)
    # print('true children: ',trueNodes, 'pseudo children: ', pseudoNodes)
    # [trueParent, pseudoParent] = getParents(T,3)
    # print('true parent: ',trueParent, 'pseudo parent: ', pseudoParent)

    compute_utils(T)
    plt.show()

if __name__ == '__main__':
    main()	
