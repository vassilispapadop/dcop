import networkx as nx
from networkx.classes.coreviews import AdjacencyView
from networkx.drawing.nx_pydot import graphviz_layout
import matplotlib.pyplot as plt
import numpy as np
import pydot
import json
from variable import Variable

def getVarFromMeetingId(varList, tupleKey):
    res = []
    [varId, meetingId] = tupleKey
    for v in varList:
        if v.meetingId == meetingId and varId != v.varId:
            res.append(v)
    return res

def getVarFromAgentId(varList, agentId):
    agents =[]
    for v in varList:
        if v.agentId == agentId:
            agents.append(v)

    return agents        


def addInequalityConstraintsEdges(vars):
    nequalConst = []
    for v in vars:
        list_found = getVarFromAgentId(vars, v.agentId)
        for item in list_found:
            nequalConst.append((v.label, item.label))

    # return unique tuples, order does not matter
    nequalConst = [list(tpl) for tpl in list(set([tuple(sorted(pair)) for pair in nequalConst]))]

    return nequalConst

def addEqualityConstraintsEdges(vars):
    equalConst = []
    for v in vars:
        list_found = getVarFromMeetingId(vars, (v.varId, v.meetingId))
        for item in list_found:
            if v.label != item.label:
                equalConst.append((v.label, item.label))

    # return unique tuples, order does not matter
    equalConst = [list(tpl) for tpl in list(set([tuple(sorted(pair)) for pair in equalConst]))]

    return equalConst