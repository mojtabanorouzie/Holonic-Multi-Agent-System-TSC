from AAPI import *


class Holon:
    def __init__(self):
        self.numberOfNode = 0
        self.Q = 0
        self.members = []
        self.edgeMember = []
        self.max = 0

    def insertMember(self, member):
        self.members.append(member)
        self.numberOfNode += 1

    def isMember(self, member):
        if member in self.members:
            return True
        else:
            return False

    def calculateQ(self, weight):
        self.Q = weight / 2


class Edge:
    def __init__(self, identification):
        self.id1 = identification
        self.numberOfVehicles = None
        self.distance = 700
        self.startNode = None
        self.endNode = None
        self.id2 = None
        self.weight = None


def createFirstGraph(agents):
    graphNodes = []
    graphEdges = {}
    for index in agents:
        graphNodes.append(agents[index].id)
        for i in range(4):
            e = Edge(agents[index].idSectionIn[i])
            if e.id1 not in graphEdges:
                e.endNode = agents[index].id
                e.id1 = agents[index].idSectionIn[i]
                graphEdges[e.id1] = e
            elif graphEdges[e.id1].endNode is None:
                tempEdge = graphEdges[e.id1]
                tempEdge.endNode = agents[index].id
                graphEdges[e.id1] = tempEdge
            e = Edge(agents[index].idSectionOut[i])
            if e.id1 not in graphEdges:
                e.startNode = agents[index].id
                e.id1 = agents[index].idSectionOut[i]
                graphEdges[e.id1] = e
            elif graphEdges[e.id1].startNode is None:
                tempEdge = graphEdges[e.id1]
                tempEdge.startNode = agents[index].id
                graphEdges[e.id1] = tempEdge
    return [graphNodes, graphEdges]
# tempEdge


def createSecondGraph(graphEdges):
    for e in graphEdges:
        startNodeList = []
        for ee in graphEdges:
            if graphEdges[e].startNode == graphEdges[ee].startNode:
                startNodeList.append(graphEdges[ee].id1)
        if startNodeList.__len__() > 4:
            startNodeList = startNodeList[0:4]
        graphEdges[e].numberOfVehicles = calculateNumberOfVehicles(graphEdges[e].id1, startNodeList)
    idList = []
    for e in graphEdges:
        for ee in graphEdges:
            if ee not in idList and e not in idList and graphEdges[e].endNode == graphEdges[ee].startNode and \
                            graphEdges[e].startNode == graphEdges[ee].endNode:
                graphEdges[e].numberOfVehicles += graphEdges[ee].numberOfVehicles
                graphEdges[e].id2 = graphEdges[ee].id1
                idList.append(ee)
    for item in idList:
        del graphEdges[item]
    for e in graphEdges:
        graphEdges[e].weight = float(graphEdges[e].numberOfVehicles) / float(2)
    return graphEdges


def calculateNumberOfVehicles(edgeId, listId):
    a = AKIVehStateGetNbVehiclesSection(edgeId, True)
    b = sum(AKIVehStateGetNbVehiclesSection(i, True) for i in listId)
    if b == 0:
        return 0
    else:
        return float(a)/float(b)


def createHolon(graphNodes, graphEdges):
    tempGraphEdges = graphEdges.copy()
    holons = []
    holonNodes = []
    while graphEdges:
        maxWeight = 0
        index = None
        for e in graphEdges:
            if graphEdges[e].weight > maxWeight:
                maxWeight = graphEdges[e].weight
                index = e

        if (graphEdges[index].startNode is None) or (graphEdges[index].endNode is None):
            del graphEdges[index]
            continue

        if (graphEdges[index].startNode not in holonNodes) and (graphEdges[index].endNode not in holonNodes):
            h = Holon()
            h.insertMember(graphEdges[index].startNode)
            h.insertMember(graphEdges[index].endNode)
            h.calculateQ(graphEdges[index].weight)
            h.edgeMember.append(graphEdges[index])
            holonNodes.append(graphEdges[index].startNode)
            holonNodes.append(graphEdges[index].endNode)
            holons.append(h)
            # refrom graph

        elif (graphEdges[index].startNode not in holonNodes) or (graphEdges[index].endNode not in holonNodes):
            tempIndex = 0
            if graphEdges[index].startNode in holonNodes:
                for holon in range(len(holons)):
                    if holons[holon].isMember(graphEdges[index].startNode):
                        h = holons[holon]
                        tempIndex = holon
                        break
                newQ = ((h.Q * h.numberOfNode) + graphEdges[index].weight) / (h.numberOfNode + 1)
                if newQ > h.Q:
                    h.insertMember(graphEdges[index].endNode)
                    holonNodes.append(graphEdges[index].endNode)
                    h.Q = newQ
                    h.edgeMember.append(graphEdges[index])
                    holons[tempIndex] = h
                    # refrom graph
            else:
                for holon in range(len(holons)):
                    if holons[holon].isMember(graphEdges[index].endNode):
                        h = holons[holon]
                        tempIndex = holon
                        break
                newQ = ((h.Q * h.numberOfNode) + graphEdges[index].weight) / (h.numberOfNode + 1)
                if newQ > h.Q:
                    h.insertMember(graphEdges[index].startNode)
                    holonNodes.append(graphEdges[index].startNode)
                    h.Q = newQ
                    h.edgeMember.append(graphEdges[index])
                    holons[tempIndex] = h
                    # refrom graph
        else:
            for holon in range(len(holons)):
                if holons[holon].isMember(graphEdges[index].startNode):
                    h1 = holons[holon]
                    tempIndex1 = holon
                    break
            for holon in range(len(holons)):
                if holons[holon].isMember(graphEdges[index].startNode):
                    h2 = holons[holon]
                    tempIndex2 = holon
                    break
            newQ = ((h1.Q * h1.numberOfNode) + (h2.Q * h2.numberOfNode) + graphEdges[index].weight) /\
                   (h1.numberOfNode + h2.numberOfNode)
            if newQ > (h1.Q + h2.Q):
                for member in h2.members:
                    h1.insertMember(member)
                for edge in h2.edgeMember:
                    h1.edgeMember.append(edge)
                h1.Q = newQ
                h1.edgeMember.append(graphEdges[index])
                holons.append(h1)
                del holons[tempIndex1]
                del holons[tempIndex2]
                # reform graph
        del graphEdges[index]
    # create single holon
    for x in holonNodes:
        graphNodes.remove(x)
    for n in graphNodes:
        h = Holon()
        h.insertMember(n)
        holons.append(h)
    # AKIPrintString(str(tempGraphEdges))
    # for h in holons:
    #     for i in h.edgeMember:
    #         AKIPrintString(str(i.id1))
    #         del tempGraphEdges[i.id1]
    # h = Holon()
    # h.edgeMember = tempGraphEdges
    # holons.append(h)
    return holons
