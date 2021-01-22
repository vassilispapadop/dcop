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
    inputFilename = 'constraint_graphs/DCOP_Problem_10'
    input = open(inputFilename, 'r') 
    
    # Read first line
    [nrAgents, nrMeetings, nrVars] = uv2.readLine(input)
    print("Number of agents:%d \nNumber of meetings:%d \nNumber of variables:%d" %(nrAgents, nrMeetings, nrVars))

    # Read variables
    varList = uv2.readVariables(input, nrVars)
    print(varList)

    # Create graph
    G = nx.Graph()

    equalityEdges = ptree.addEqualityConstraintsEdges(varList)
    inequalityEdges = ptree.addInequalityConstraintsEdges(varList)

    G.add_edges_from(equalityEdges + inequalityEdges)

    layout = graphviz_layout(G, prog="neato")
    nx.draw(G, layout, with_labels=True)
    plt.show()

if __name__ == "__main__":
    main()