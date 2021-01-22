from variable import Variable

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
        # agent = {
        #             'id': agentId,  
        #                 'meetings': {
        #                     meetingId: meetingUtil
        #                 },
        #                 'preference': []
        #         }
        # index = search(agentId, agents)
        # if index > -1:
        #     update_meeting = agents[index]
        #     update_meeting['meetings'].update({meetingId:meetingUtil})
        # else:
        #     agents.append(agent)

    # agents.sort(key=sortBy)
    return vars   