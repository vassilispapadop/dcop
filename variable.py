class Variable:
    def __init__(self, _agentId, _meetingId, _utility):
        self.index = str(_agentId) + "_" + str(_meetingId)
        self.agentId = _agentId 
        self.meetingId = _meetingId
        self.utility = _utility
    
    def __str__ (self):
        return "Variable %s -> Agent Id:%d, Meeting Id:%d, Utility:%d" % (self.index, self.agentId, self.meetingId, self.utility) 
    
    def __repr__(self):  
        return "Variable %s -> Agent Id:%d, Meeting Id:%d, Utility:%d\n" % (self.index, self.agentId, self.meetingId, self.utility) 
         