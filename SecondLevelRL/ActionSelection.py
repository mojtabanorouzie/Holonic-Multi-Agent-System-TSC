import random


def actionSelectionSecondLevel(randomProbability, qTable, numberOfAction):
    if random.random() > randomProbability:
        action = qTable.index(max(qTable))
        actionType = "best"
    else:
        action = random.randint(0, numberOfAction - 1)
        actionType = "random"
    return [action, actionType]


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
    phaseDuration = getPhaseDuration(action)
    return [action, phaseDuration, actionType]


def getPhaseDuration(action):
    phaseDuration = [23] * 4  # Action 18
    if action == 0:
        phaseDuration = [33, 33, 13, 13]
    elif action == 1:
        phaseDuration = [33, 13, 33, 13]
    elif action == 2:
        phaseDuration = [33, 13, 13, 33]
    elif action == 3:
        phaseDuration = [13, 33, 33, 13]
    elif action == 4:
        phaseDuration = [13, 33, 13, 33]
    elif action == 5:
        phaseDuration = [13, 13, 33, 33]
    elif action == 6:
        phaseDuration = [33, 23, 23, 13]
    elif action == 7:
        phaseDuration = [33, 23, 13, 23]
    elif action == 8:
        phaseDuration = [33, 13, 23, 23]
    elif action == 9:
        phaseDuration = [23, 33, 23, 13]
    elif action == 10:
        phaseDuration = [23, 33, 13, 23]
    elif action == 11:
        phaseDuration = [13, 33, 23, 23]
    elif action == 12:
        phaseDuration = [23, 23, 33, 13]
    elif action == 13:
        phaseDuration = [23, 13, 33, 23]
    elif action == 14:
        phaseDuration = [13, 23, 33, 23]
    elif action == 15:
        phaseDuration = [23, 23, 13, 33]
    elif action == 16:
        phaseDuration = [23, 13, 23, 33]
    elif action == 17:
        phaseDuration = [13, 23, 23, 33]
    return phaseDuration
