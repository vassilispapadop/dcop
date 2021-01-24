from variable import Variable
from variable import AgentClass

def readLine(input):
    try:
        [a, b, c] = input.readline().strip().split(';')
    except ValueError as e:
        return []

    return int(a), int(b), int(c)

def readVariables(input, nr_vars):
    vars = []
    for i in range(0, nr_vars):

        [agentId, meetingId, meetingUtil] = readLine(input)
        var = Variable(i, agentId, meetingId, meetingUtil) 
        vars.append(var)

    # agents.sort(key=sortBy)
    agents = groupByAgents(vars)
    return vars, agents   

def searchAgent(meetingId, agentsList):
    i = 0
    while i < len(agentsList):
        if agentsList[i].findMeeting(meetingId):
            return i

    return -1

def groupByAgents(vars):
    agents = {}
    for v in vars:
        if v.agentId not in agents:
            agents[v.agentId] = AgentClass(v.agentId)

        agents[v.agentId].addMeeting(v.meetingId)
        # index = searchAgent(v.meetingId, agents)
        # if index == -1:
        #     continue

        # agents[index].meetings.append(v.meetingId)

    return agents