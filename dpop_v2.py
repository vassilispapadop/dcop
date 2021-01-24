import utilities_v2 as uv2
from variable import Variable
import networkx as nx
from networkx.classes.coreviews import AdjacencyView
from networkx.drawing.nx_pydot import graphviz_layout
import matplotlib.pyplot as plt
import pydot
import pseudotree_v2 as ptree

def main():
    # 1st row: Number of agents;Number of meetings;Number of variables

    # Open file 
    # inputFilename = 'constraint_graphs/dcop_constraint_graph'
    # inputFilename = 'constraint_graphs/dcop_simple'
    inputFilename = 'constraint_graphs/DCOP_Problem_50'
    input = open(inputFilename, 'r') 
    
    # Read first line
    [nrAgents, nrMeetings, nrVars] = uv2.readLine(input)
    print("Number of agents:%d \nNumber of meetings:%d \nNumber of variables:%d" %(nrAgents, nrMeetings, nrVars))

    # Read variables
    [varList, agentsList] = uv2.readVariables(input, nrVars)
    # print(varList)
    # print(agentsList)

    print('-----------Variables Graph--------------')   
    graphVariables = {}
    for v in varList:
        graphVariables[v.varId] = ptree.getAllVarsWithSameMeeting(varList, v.meetingId, v.varId)

    print (graphVariables) 

    print('-----------Agents Graph--------------')  
    graphAgents = {}
    for id, attr in agentsList.items():
        graphAgents[id] = ptree.getAllAgentsWithSameMeeting(agentsList, attr.meetings, id)

    print (graphAgents)

    # Add all edges to graph
    edges = []
    for k, l in graphAgents.items():
        for v in l:
            edges.append((k,v))
    edges = [list(tpl) for tpl in list(set([tuple(sorted(pair)) for pair in edges]))]
    print(edges)

    # Create graph
    G = nx.Graph()
    for e in edges:
        G.add_edge(*e, style = 'solid')

    # Create dfs tree with speficied node
    rootNode = 5
    T = nx.dfs_tree(G, rootNode)
    print("----------------")
    back_edges = []
    for node, connected in graphAgents.items():
        e = set(T.edges([node]))
        shouldBe = []
        for con in connected:
            if (node, con) in e: continue
            if (con, node) in e: continue
            if T.has_edge(node,con): continue
            if T.has_edge(con,node): continue

            shouldBe.append((node, con))

        back = set(shouldBe) - e
        back_edges.append(back)


    back_edges = [item for sublist in back_edges for item in sublist]
    back_edges = [list(tpl) for tpl in list(set([tuple(sorted(pair)) for pair in back_edges]))]
    print(back_edges)
    for e in back_edges:
        T.add_edge(*e, color = 'blue')


    layout = graphviz_layout(T, prog="dot")

    edges = T.edges.data('color', default='black')
    colors = []
    for _,_,c in edges:
        colors.append(c)

    nx.draw(T, layout, edge_color=colors, with_labels=True) #style='dashed', connectionstyle="arc3,rad=0.1"
    output = "root_"+str(rootNode)+".png"
    plt.savefig(output, format="PNG")

if __name__ == "__main__":
    main()