TIME_SLOTS = 3
SLOTS= {
	0:"Morning",
	1:"Afternoon",
	2:"Evening",
    3:"Adsf",
    4:"asdf",
    5:"hhg",
    6:"sdgh",
    7:"fg45h"
}


# utilities
def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2)) 

def readLine(input):
    try:
        [a, b, c] = input.readline().strip().split(';')
    except ValueError as e:
        return []

    return int(a), int(b), int(c)

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

    agents.sort(key=sortBy)
    return agents

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
                break

    return agents

def printNodes(G):
    
    for _, attr in G.nodes(data=True):
        attr['attributes'].printNode()

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