import random


def actionSelectionFirstLevel(numberOfAction, randomProbability, qTable, junctionId, sectionId, startId, endId,
                              superAction, networkDetails):
    # Create actionSet
    actionSet = [i for i in range(numberOfAction)]
    if (junctionId == startId) and (superAction == 3 or superAction == 4):
        if sectionId in networkDetails[startId][0]:
            actionSet = [0, 1, 2, 6, 7, 8]
        elif sectionId in networkDetails[startId][1]:
            actionSet = [0, 3, 4, 9, 10, 11]
        elif sectionId in networkDetails[startId][2]:
            actionSet = [1, 3, 5, 12, 13, 14]
        else:
            actionSet = [2, 4, 5, 15, 16, 17]
    if junctionId == endId:
        if sectionId in networkDetails[endId][0]:
            if superAction == 2 or superAction == 4:
                actionSet = [0, 1, 2, 6, 7, 8]
            elif superAction == 3 or superAction == 5:
                return 19
        elif id in networkDetails[endId][1]:
            if superAction == 2 or superAction == 4:
                actionSet = [0, 3, 4, 9, 10, 11]
            elif superAction == 3 or superAction == 5:
                return 20
        elif id in networkDetails[endId][2]:
            if superAction == 2 or superAction == 4:
                actionSet = [1, 3, 5, 12, 13, 14]
            elif superAction == 3 or superAction == 5:
                return 21
        else:
            if superAction == 2 or superAction == 4:
                actionSet = [2, 4, 5, 15, 16, 17]
            elif superAction == 3 or superAction == 5:
                return 22
    # Select an Action
    if random.random() > randomProbability:
        maxQ = -float("inf")
        for tempAction in actionSet:
            if qTable[tempAction] > maxQ:
                maxQ = qTable[tempAction]
                action = tempAction
        actionType = 'best'
    else:
        temp_action = random.randint(0, len(actionSet) - 1)
        action = actionSet[temp_action]
        actionType = 'random'
    return action
