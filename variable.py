class Variable:
    def __init__(self, _index, _agentId, _meetingId, _utility):
        self.varId = _index
        self.label = (_index, _agentId, _meetingId)
        self.agentId = _agentId 
        self.meetingId = _meetingId
        self.utility = _utility
    
    def __str__ (self):
        return "Variable %s -> Agent Id:%d, Meeting Id:%d, Utility:%d" % (str(self.label), self.agentId, self.meetingId, self.utility) 
    
    def __repr__(self):  
        return "Variable %s -> Agent Id:%d, Meeting Id:%d, Utility:%d\n" % (str(self.label), self.agentId, self.meetingId, self.utility) 


class AgentClass:
    def __init__(self, id):
        self.id = id
        self.meetings = []
        self.preference = []

    def addMeeting(self, meetingId):
        self.meetings.append(meetingId)

    def findMeeting(self, id):
        for m in self.meetings:
            if m == id:
                return True

        return False

    def addPrefSlot(self, slot):
        self.preference.append(slot)
         