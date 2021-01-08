import json
import Utilities as u
import numpy as np

class NodeAttributes:
    def __init__(self, _id, _meetings, _preference):
        self.id = _id
        self.meetings = _meetings
        self.preference = _preference 
        self.util_msgs = {}
        self.join = np.zeros((u.TIME_SLOTS, u.TIME_SLOTS))

    def addUtilMsg(self, util_msg):
        self.util_msgs[util_msg['childId']] = util_msg

    def joinUtilMsgs(self):
        for i in range(0, u.TIME_SLOTS):
            for j in range(0, u.TIME_SLOTS):
                sum = 0
                for [_, dict] in self.util_msgs.items():
                    sum += dict['util'][i]

                self.join[i][j] = sum


    def printNode(self):
        info = {'id': self.id, 'meetings':self.meetings, 
                    'preference': self.preference, 
                    'util_msgs': self.util_msgs,
                    'join': self.joinUtilMsgs }
        print(info)
        # print(json.dumps(text, indent=4, sort_keys=True))
    