import networkx as nx
import matplotlib.pyplot as plt
import networkx as nx
import pydot
from networkx.drawing.nx_pydot import graphviz_layout

def readLine(input):
    [a, b, c] = input.readline().strip().split(';')
    return int(a), int(b), int(c)

def printAgents(agents):
    for item in agents:
        print(item)

def readMeetings(input, vars):
    agents = []
    for i in range(0, vars):
        [agentId, meetingId, meetingUtil] = readLine(input)
        agent = {
                    'id': agentId,  
                        'meetings': {
                            meetingId: meetingUtil
                    }
                }
        index = search(agentId, agents)
        if index > -1:
            update_meeting = agents[index]
            update_meeting['meetings'].update({meetingId:meetingUtil})
        else:
            agents.append(agent)

    agents.sort(key=sortBy)
    printAgents(agents)
    return agents

def sortBy(e):
      return e['id']

# list comprehension
def search(id, agents):
    index = 0
    while index < len(agents):
        if agents[index]['id'] == id:
            return index
        index += 1
    return -1        
    
def meetingSharedBy(agents, meetingId):
    sharedBy = []
    for item in agents:
        for m_id in item['meetings'].keys():
            if m_id == meetingId:
                sharedBy.append(item['id'])
                break

    #print (sharedBy)
    sharedBy.sort()
    return sharedBy


def getChildrenNodes(tree, parent):
    neighbors = tree.adj[parent]
    return [x for x in neighbors if x > parent]

def main():
    # 1st row: Number of agents;Number of meetings;Number of variables

    # Open file 
    inputFilename = 'dcop_constraint_graph'
    input = open(inputFilename, 'r') 

    # Read first line
    [nrAgents, nrMeetings, nrVars] = readLine(input)

    # Read agents/variables/constraints
    agents = readMeetings(input, nrVars)

    # Create graph
    G = nx.Graph()
    
    # Add agents/nodes
    for agent in agents:
        G.add_node(agent['id'])

    # Add edges and keep track of back-edges
    back_egdes = []
    #PTC = dict.fromkeys(range(nrAgents), 0)
    for meetingId in range(0, nrMeetings):
        ids = meetingSharedBy(agents, meetingId)
        i = 0
        while i < len(ids) -1 :
            next = i + 1
            e = (ids[i], ids[next])
            if len(G.adj[ids[i]]) < 2:
                G.add_edge(*e,  color='b')
                # PTC[ids[i]] = PTC[ids[i]] + 1
            else:
               back_egdes.append([*e])    

            i += 1
    
    # Convert to spanning tree
    T = nx.minimum_spanning_tree(G)

    # Create back edges
    back_egdes.sort()
    for edge in back_egdes:
        [parent, child] = edge
        color = 'r'
        if len(getChildrenNodes(T, parent)) < 2:
            color = 'b'

        T.add_edge(*edge, color = color)

    # print('parents: ', PTC)
    print('back-edges: ', back_egdes)

    layout = graphviz_layout(T, prog="dot")

    edges = T.edges()
    colors = [T[u][v]['color'] for u,v in edges]

    nx.draw(T, layout, edge_color=colors, with_labels=True)
    print(getChildrenNodes(T, 2))
    plt.show()

if __name__ == '__main__':
    main()	
