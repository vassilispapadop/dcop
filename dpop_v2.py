import utilities_v2 as uv2
from variable import Variable
import networkx as nx
from networkx.classes.coreviews import AdjacencyView
from networkx.drawing.nx_pydot import graphviz_layout
import matplotlib.pyplot as plt
import pydot
import pseudotree_v2 as ptree
from collections import deque
root_node = 0

agentsList = {}

sentMsgs = []
totalMsgs = []
value_prop_order = []

def get_parent(T, node):
    parent = None
    pseudo_parents = []
    in_edges = list(T.in_edges(node ,data=True))
    out_edges = list(T.out_edges(node, data=True))
    for p,_,c in in_edges:
        try:
            if c['color'] == 'blue':
                pseudo_parents.append(p) 

        except KeyError as e:
            children = []
            for _,a,c in list(T.out_edges(p, data=True)):
                try:
                    if c['color'] == 'blue':
                        # print('pseudo children skip')
                        pass
                except KeyError as k:
                    children.append(a)  

            result = set(children).issubset(sentMsgs)
            if result:
                parent = p

    return parent, pseudo_parents

def send_util_msg(T, nodes):
    # compute utility from each node and pass it to parents
    # keep track of parents
    if len(nodes) == 0:
        return    

    parents = []
    for node in nodes:

        sentMsgs.append(node)
        [parent, _] = get_parent(T,node)
        # if parent == None:
        #     return
        if parent != None:
            # for some reason sometimes send the same msg twice
            if (node,parent) not in totalMsgs:
                print("Util Message from: %d to %d" %(node,parent))
                if agentsList[node].id != node:
                    print("OOOOOPPPPS")
                    
                totalMsgs.append((node,parent))
                # store parents order to use in value propagation
                value_prop_order.append((parent,node))

            if parent not in parents:
                parents.append(parent)
        elif node != root_node:
            if node not in parents:
                parents.append(node)

    # print("checking util for:", parents)
    send_util_msg(T,parents)


def send_value_msg():
    # reverse because we use recursion in send_util_msg
    value_prop_order.reverse()
    for p in value_prop_order:
        [parent, child] = p
        print("Value Message from: %d to %d" %(parent,child))

def main():
    # 1st row: Number of agents;Number of meetings;Number of variables
    useAgents = True
    # Open file 
    # inputFilename = 'constraint_graphs/dcop_constraint_graph'
    # inputFilename = 'constraint_graphs/dcop_simple'
    inputFilename = 'constraint_graphs/DCOP_Problem_700'
    input = open(inputFilename, 'r') 
    
    # Read first line
    [nrAgents, nrMeetings, nrVars] = uv2.readLine(input)
    print("Number of agents:%d \nNumber of meetings:%d \nNumber of variables:%d" %(nrAgents, nrMeetings, nrVars))

    # Read variables
    global agentsList
    varList, agentsList = uv2.readVariables(input, nrVars)

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
    graph = graphVariables
    if useAgents == True:
        graph = graphAgents

    # Add all edges to graph
    graph_edges = []
    for k, l in graph.items():
        for v in l:
            graph_edges.append((k,v))
    graph_edges = [list(tpl) for tpl in list(set([tuple(sorted(pair)) for pair in graph_edges]))]
    print(graph_edges)

    # Create graph
    G = nx.Graph()
    
    # Constraint graph
    for e in graph_edges:
        G.add_edge(*e, color = 'black')

    # Create dfs tree with speficied node
    TreeDfs = nx.dfs_tree(G, root_node)

    print("----------------")
    back_edges = []
    for node, connected in graph.items():
        e = set(TreeDfs.edges([node]))
        shouldBe = []
        for con in connected:
            if (node, con) in e: continue
            if (con, node) in e: continue
            if TreeDfs.has_edge(node,con): continue
            if TreeDfs.has_edge(con,node): continue

            shouldBe.append((node, con))

        back = set(shouldBe) - e
        back_edges.append(back)


    back_edges = [item for sublist in back_edges for item in sublist]
    back_edges = [list(tpl) for tpl in list(set([tuple(sorted(pair)) for pair in back_edges]))]
    print(back_edges)
    for e in back_edges:
        TreeDfs.add_edge(*e, color = 'blue')

  
    # leaves = [v for v, d in TreeDfs.out_degree() if d == 0]
    # find leaves in order to start compute util process
    leaves = []
    for v in TreeDfs.nodes(data=True):
        out_edges = list(TreeDfs.out_edges(v[0], data=True))
        if len(out_edges) == 0:
            leaves.append(v[0])
            continue

        # print (v, out_edges)
        all_blue = True
        for _,_,color in out_edges:
            try:
                if color['color'] != 'blue':
                    all_blue = False
                    break
            except KeyError as key:
                    all_blue = False
                    break
        if all_blue:
            leaves.append(v[0])       

    edges = TreeDfs.edges.data('color', default='black')
    colors = []
    for _,_,c in edges:
        colors.append(c)

    layout = graphviz_layout(TreeDfs, prog="dot") 
    nx.draw(TreeDfs, layout, edge_color=colors, with_labels=True) #style='dashed', connectionstyle="arc3,rad=0.1"
    output = "root_"+str(root_node)+".png"
    plt.savefig(output, format="PNG")

    # print(nx.shortest_path_length(TreeDfs,root_node))
    print("Leaves are:", leaves)
    send_util_msg(TreeDfs, leaves)
    print("Total number of messages:%d" %(len(totalMsgs)))
    send_value_msg()
if __name__ == "__main__":
    main()