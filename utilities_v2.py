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


def readPrerefence(input, agentsList):
    # for a in agentsList:
    #     for i in range(0,7):
    #         [agentId, _, pref] = readLine(input)
    #         print(agentId)
    #         # if agentId == agentsList[a].id:
    #         agentsList[a].addPrefSlot(pref)


    [agentId, _, pref] = readLine(input)
    while True:
        try:
            agentsList[agentId].addPrefSlot(pref)
            [agentId, _, pref] = readLine(input)
        except ValueError as v:
            break

    return agentsList

def searchAgent(meetingId, agentsList):
    i = 0
    while i < len(agentsList):
        if agentsList[i].findMeeting(meetingId):
            return i
        i += 1
        
    return -1

def groupByAgents(vars):
    agents = {}
    for v in vars:
        if v.agentId not in agents:
            agents[v.agentId] = AgentClass(v.agentId)

        agents[v.agentId].addMeeting(v.meetingId)

    return agents