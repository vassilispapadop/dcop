import json

class NodeAttributes:
    def __init__(self, _id, _meetings, _preference):
        self.id = _id
        self.meetings = _meetings
        self.preference = _preference 
        self.util_msgs = {}

    def addUtilMsg(self, util_msg):
        self.util_msgs[util_msg['childId']] = util_msg

    def print_node(self):
        text = {'id': self.id, 'meetings':self.meetings, 
                    'preference': self.preference, 'util_msgs': self.util_msgs }
        print(json.dumps(text, indent=4, sort_keys=True))