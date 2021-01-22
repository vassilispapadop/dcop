import utilities_v2 as uv2
from variable import Variable
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

    varList = uv2.readVariables(input, nrVars)
    print(varList)

if __name__ == "__main__":
    main()