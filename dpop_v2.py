import utilities_v2 as uv2
from variable import Variable
import networkx as nx
from networkx.classes.coreviews import AdjacencyView
from networkx.drawing.nx_pydot import graphviz_layout
import matplotlib.pyplot as plt
import pydot
import pseudotree_v2 as ptree
from collections import deque
from sys import getsizeof
import matplotlib.pyplot as plt
from pympler import asizeof
root_node = 0

agentsList = {}

sentMsgs = []
seenMsgs = []
value_prop_order = []
MESSAGES_SIZE = []

msgSizePerCycleCounter = 0
msgSizePerCycle = []

msgCounter = 0
msgCountPerIteration =[]

cycleCounter = 0
cyclePerLevel = []

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

def send_util_msg(T, nodes, msgCounter, msgSizePerCycleCounter, cycleCounter):
    # compute utility from each node and pass it to parents
    # keep track of parents
    if len(nodes) == 0:
        print("root node: ", agentsList[root_node].createHypercube(-1))
        return    

    parents = []
    for node in nodes:

        sentMsgs.append(node)
        [parent, _] = get_parent(T,node)
        
        if parent != None:
            # for some reason sometimes send the same msg twice
            if (node,parent) not in seenMsgs:
                print("Util Message from: %d to %d" %(node,parent))
                if agentsList[node].id != node:
                    print("OOOOOPPPPS")
                else:
                    MSG = agentsList[node].createHypercube(parent)
                    # print("Message Contents:", MSG)
                    agentsList[parent].addReceivedMsgs(MSG)

                    MESSAGES_SIZE.append(asizeof.asizeof(MSG))
                    msgSizePerCycleCounter += asizeof.asizeof(MSG)

                seenMsgs.append((node,parent))
                msgCounter += 1
                msgCountPerIteration.append(msgCounter)
                # store parents order to use in value propagation
                value_prop_order.append((parent,node))

            if parent not in parents:
                # cycleCounter.append(1)
                parents.append(parent)
        elif node != root_node:
            if node not in parents:
                msgSizePerCycle.append(msgSizePerCycleCounter)
                msgSizePerCycleCounter = 0
                cycleCounter += 1
                cyclePerLevel.append(cycleCounter)
                parents.append(node)

    # print("checking util for:", parents)
    send_util_msg(T,parents, msgCounter, msgSizePerCycleCounter, cycleCounter)


def send_value_msg():
    # reverse because we use recursion in send_util_msg
    value_prop_order.reverse()
    for p in value_prop_order:
        [parent, child] = p
        print("Value Message from: %d to %d" %(parent,child))


def find_leave_nodes(TreeDfs):
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

    return leaves    


def create_relations(TreeDfs, agentsList):
    for node in TreeDfs.nodes(data=True):
        out_edges = list(TreeDfs.out_edges(node[0], data=True))
        for parent, child, edge_color in out_edges:
            sharedMeetings = uv2.intersection(agentsList[parent].meetings , agentsList[child].meetings)
            for meeting in sharedMeetings:
                pMatrix = agentsList[parent].internalMatrix[meeting]
                cMatrix = agentsList[child].internalMatrix[meeting]
                agentsList[child].addRelation(parent, meeting, pMatrix + cMatrix)
        

def main():
    # 1st row: Number of agents;Number of meetings;Number of variables
    useAgents = True
    # Open file 
    # inputFilename = 'constraint_graphs/dcop_constraint_graph'
    # inputFilename = 'constraint_graphs/dcop_simple'
    inputFilename = 'constraint_graphs/DCOP_Problem_300'
    input = open(inputFilename, 'r') 
    
    # Read first line
    [nrAgents, nrMeetings, nrVars] = uv2.readLine(input)
    print("Number of agents:%d \nNumber of meetings:%d \nNumber of variables:%d" %(nrAgents, nrMeetings, nrVars))

    # Read variables
    global agentsList
    varList, agentsList = uv2.readVariables(input, nrVars)

    # Read preference
    agentsList = uv2.readPrerefence(input, agentsList)

    # Create internal/node matrix per meeting
    agentsList = uv2.buildPrefMatrixInternal(agentsList)

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


    layout = graphviz_layout(G, prog="dot") 
    nx.draw(G, layout, with_labels=True, node_color='#efedf2', arrowsize=1)#, connectionstyle="arc3,rad=0.1"
    output = "root_"+str(root_node)+".png"
    plt.savefig(output, format="PNG")

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
        TreeDfs.add_edge(*e, color = 'blue', style='dashed')


    # create relations based on tree edges
    create_relations(TreeDfs, agentsList)

    # find leaves in order to start compute util process
    leaves = find_leave_nodes(TreeDfs)     

    edges = TreeDfs.edges.data('color', default='black')
    colors = []
    for _,_,c in edges:
        colors.append(c)

    # layout = graphviz_layout(TreeDfs, prog="dot") 
    # nx.draw(TreeDfs, layout, edge_color=colors, with_labels=True, node_color='#efedf2', arrowsize=1)#, connectionstyle="arc3,rad=0.1"
    # output = "root_"+str(root_node)+".png"
    # plt.savefig(output, format="PNG")

    # print(nx.shortest_path_length(TreeDfs,root_node))
    print("Leaves are:", leaves)
    send_util_msg(TreeDfs, leaves, msgCounter, msgSizePerCycleCounter, cycleCounter)
    send_value_msg()

    #Constraints = Number of edges + Inequality constraints
    EQConstraints = TreeDfs.number_of_edges()
    #iterate through every agent and count number of inequality constraints
    NEQConstraints = 0
    for id, attr in agentsList.items():
        i = len(attr.meetings) - 1
        count = 0
        while i > 0:
            count += i
            i -= 1
        NEQConstraints += count

    # Print table results, as in paper
    print("Number of agents:%d \nNumber of meetings:%d \nNumber of variables:%d" %(nrAgents, nrMeetings, nrVars))
    print("Total Constraints", EQConstraints+NEQConstraints)
    print("\tEquality constraints", EQConstraints)
    print("\tInequality constraints", NEQConstraints)
    print("Total number of messages:%d" %(len(msgCountPerIteration) * 2))
    print("Max message size:%d"% (max(MESSAGES_SIZE)))
    print("Cycles:%d"% (len(cyclePerLevel) * 2))
    # plt.cla()
    # plt.plot(MESSAGES_SIZE, color='green', marker='o', linestyle='dashed', linewidth=1, markersize=5)
    # plt.title("Message size evolution during util propagation")
    # plt.xlabel('Message counter')
    # plt.ylabel('Message size(Bytes)')
    # plt.savefig("msg_size_util_prop.png", format="PNG")
    
    # # plt.cla()
    # plt.plot(cyclePerLevel, msgSizePerCycle, color='green', marker='o', linestyle='dashed', linewidth=1, markersize=5)
    # plt.title("Aggregated Message size per tree level, during util propagation")
    # plt.xlabel('Tree level')
    # plt.ylabel('Aggregated Message size(Bytes)')
    # plt.savefig("msg_size_per_level_util_prop.png", format="PNG")

    # # plt.cla()
    # plt.plot(msgCountPerIteration, color='green', marker='o', linestyle='dashed', linewidth=1, markersize=5)
    # plt.title("Number of Messages during util propagation")
    # plt.xlabel('Iteration')
    # plt.ylabel('Number Messages')
    # plt.savefig("nr_msg_util_prop.png", format="PNG")



if __name__ == "__main__":
    main()