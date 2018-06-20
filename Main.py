from AAPI import *
from ReinforcementLearningPack import QLearning, GetState, ActionSelection
from SecondLevelRL import CreateHolon, SecondLevelAgent, ActionSelection, GetReward

# 1.1 Global Variables
warmup = 1800
cycle = 100
eGreedy = 0.01
tempTime = -1
createDataSet = False
jamDensity = 200

# 1.2 First level agent global variables
initLearningRate = 0.5
initDiscountFactor = 0.5
decayProbability = 0.02
decayLearningRate = 0.005
incrementDiscountFactor = 0.005
numberOfState = 24
numberOfAction = 19
agents = {}

# 1.3 Second level agent global variables
dynamicHolonThreshold = 0.7
dynamicHolonEnable = False
numberOfActionSecondLevel = 5
numberOfStateSecondLevel = 5
decayProbabilitySecondLevel = 0.066
decayLearningRateSecondLevel = 0.01
incrementDiscountFactorSecondLevel = 0.01
initLearningRateSecondLevel = 0.5
initDiscountFactorSecondLevel = 0.5
flag = True
nodes = None
edges = None
holonsMap = {}
edgesMap = {}
otherEdge = {}
secondLevelAgents = []

# 1.4 Network details
networkDetails = {536: [[267, 266], [268, 270], [280, 278], [277, 276]],
                  549: [[270, 268], [282, 284], [372, 370], [322, 324]],
                  562: [[282, 284], [396, 394], [294, 296], [410, 290]],
                  575: [[396, 394], [398, 400], [406, 408], [404, 402]],
                  588: [[330, 332], [364, 362], [308, 306], [280, 278]],
                  731: [[364, 362], [368, 366], [376, 374], [372, 370]],
                  601: [[368, 366], [380, 378], [354, 356], [294, 296]],
                  614: [[380, 378], [384, 382], [467, 469], [408, 406]],
                  627: [[298, 300], [304, 302], [419, 421], [308, 306]],
                  640: [[304, 302], [348, 346], [435, 437], [374, 376]],
                  653: [[348, 346], [459, 461], [453, 451], [356, 354]],
                  666: [[459, 461], [463, 465], [483, 485], [469, 467]],
                  679: [[411, 413], [427, 429], [425, 423], [421, 419]],
                  692: [[427, 429], [443, 445], [439, 441], [437, 435]],
                  705: [[445, 443], [475, 477], [457, 455], [453, 451]],
                  718: [[475, 477], [479, 481], [489, 487], [485, 483]]}


def AAPILoad():
    AKIPrintString("Load")
    return 0


def AAPIInit():
    AKIPrintString("Init")
    # 2.1 Number of agents in first level
    numberOfJunctions = AKIInfNetNbJunctions()
    global agents
    for index in range(numberOfJunctions):
        # 2.2 Get attribute of network
        junctionId = AKIInfNetGetJunctionId(index)
        junctionIdSectionIn = []
        junctionIdSectionOut = []
        for j in range(1, ECIGetNumberSignalGroups(junctionId) + 1, 1):
            num_of_turning = ECIGetNumberTurningsofSignalGroup(junctionId, j)
            for k in range(num_of_turning):
                inputSectionId = intp()
                outputSectionId = intp()
                ECIGetFromToofTurningofSignalGroup(junctionId, j, k, inputSectionId, outputSectionId)
                junctionIdSectionIn.append(int(inputSectionId.value()))
                junctionIdSectionOut.append(int(outputSectionId.value()))
        junctionIdSectionIn = list(set(junctionIdSectionIn))
        junctionIdSectionOut = list(set(junctionIdSectionOut))
        controlType = ECIGetControlType(junctionId)
        numOfPhases = ECIGetNumberPhases(junctionId)
        # 2.2 Initial Agent
        agents[AKIInfNetGetJunctionId(index)] = QLearning.ReinforcementLearningAgent(junctionId, junctionIdSectionIn,
                                                                                     junctionIdSectionOut, controlType,
                                                                                     numOfPhases, numberOfAction,
                                                                                     numberOfState, initLearningRate,
                                                                                     initDiscountFactor)
    return 0


def AAPIManage(time, timeSta, timTrans, SimStep):
    return 0


def AAPIPostManage(time, timeSta, timTrans, SimStep):
    global agents, nodes, edges, tempTime, flag, secondLevelAgents, otherEdge
    if time == 0.75:
        # 3.1 Create first graph from network
        [nodes, edges] = CreateHolon.createFirstGraph(agents)
    if int(time) % cycle == 0 and int(time) != tempTime and int(time) > warmup and flag:
        tempTime = int(time)
        flag = False
        tempEdges = edges.copy()
        tempNodes = list(nodes)
        # 3.2 Create final graph
        tempEdges = CreateHolon.createSecondGraph(tempEdges)
        # 3.3 Create holons
        [holons, otherEdge] = CreateHolon.createHolon(tempNodes, tempEdges)
        for i in range(len(holons)):
            holonsMap[i] = []
            edgesMap[i] = []
            for j in holons[i].members:
                holonsMap[i].append(j)
            for j in holons[i].edgeMember:
                edgesMap[i].append(j)
        for index in range(len(holons)):
            AKIPrintString("holon [" + str(index) + "]  =  " + str(holonsMap[index]))
        # 3.4 Create second level agents
            secondLevelAgents.append(
                SecondLevelAgent.SecondLevelRLAgent(numberOfStateSecondLevel, numberOfActionSecondLevel,
                                                    initLearningRateSecondLevel, initDiscountFactorSecondLevel))
    if int(time) % cycle == 0 and int(time) != tempTime and int(time) > warmup:
        tempTime = int(time)
        changeFlagCreateNewHolon = False
        if dynamicHolonEnable:
            for edge in otherEdge:
                statisticalInfo = AKIEstGetParcialStatisticsSection(otherEdge[edge].id1, 100, 0)
                # AKIPrintString(str(statisticalInfo.Density / jamDensity))
                if statisticalInfo.report == 0 and statisticalInfo.Density / jamDensity > dynamicHolonThreshold:
                    changeFlagCreateNewHolon = True
                if otherEdge[edge].id2:
                    statisticalInfo = AKIEstGetParcialStatisticsSection(otherEdge[edge].id2, 100, 0)
                    # AKIPrintString(str(statisticalInfo.Density / jamDensity))
                    if statisticalInfo.report == 0 and statisticalInfo.Density / jamDensity > dynamicHolonThreshold:
                        changeFlagCreateNewHolon = True
        for h in range(len(secondLevelAgents)):
            # Check number of node in the current holon
            if len(holonsMap[h]) > 1:
                # Get state first level
                if h == 0:
                    AKIPrintString("########################################")
                for key in holonsMap[h]:
                    longQueueInSection = [0] * 4
                    for i in range(4):
                        statisticalInfo = AKIEstGetParcialStatisticsSection(agents[key].idSectionIn[i], 100, 0)
                        if statisticalInfo.report == 0:
                            longQueueInSection[i] = statisticalInfo.LongQueueMax
                    agents[key].currentState = GetState.getState(longQueueInSection)
                # Get state second level
                allSectionDensity = []
                # tempDensity = [0, 0, 0, 0]  # Density  Id  StartNode  EndNode
                dta = []
                for e in edgesMap[h]:
                    tempDensity = [0, 0, 0, 0]
                    statisticalInfo = AKIEstGetParcialStatisticsSection(e.id1, 100, 0)
                    if statisticalInfo.report == 0:
                        dta.append(statisticalInfo.DTa)
                        tempDensity[0] = statisticalInfo.Density / jamDensity
                        tempDensity[1] = e.id1
                        tempDensity[2] = e.startNode
                        tempDensity[3] = e.endNode
                        allSectionDensity.append(tempDensity)
                    tempDensity = [0, 0, 0, 0]
                    statisticalInfo = AKIEstGetParcialStatisticsSection(e.id2, 100, 0)
                    if statisticalInfo.report == 0:
                        tempDensity[0] = statisticalInfo.Density / jamDensity
                        dta.append(statisticalInfo.DTa)
                        tempDensity[1] = e.id2
                        tempDensity[2] = e.endNode
                        tempDensity[3] = e.startNode
                        allSectionDensity.append(tempDensity)
                density = SecondLevelAgent.getMaxDensity(allSectionDensity)
                currentState = SecondLevelAgent.getStateSuperHolon(density[0])
                # Action selection second level
                [currentAction, actionType] = ActionSelection.actionSelectionSecondLevel(
                    secondLevelAgents[h].probabilityOfRandomAction[currentState],
                    secondLevelAgents[h].qTable[currentState], numberOfActionSecondLevel)
                if secondLevelAgents[h].probabilityOfRandomAction[currentState] >= eGreedy and actionType == "random":
                    secondLevelAgents[h].probabilityOfRandomAction[currentState] -= decayProbabilitySecondLevel
                # Action selection first level
                for key in holonsMap[h]:
                    if currentAction == 3 or currentAction == 5 and agents[key].id == density[3]:
                        if density[1] in networkDetails[density[3]][0]:
                            phaseDuration = [53, 13, 13, 13]
                        elif density[1] in networkDetails[density[3]][1]:
                            phaseDuration = [13, 53, 13, 13]
                        elif density[1] in networkDetails[density[3]][2]:
                            phaseDuration = [13, 13, 53, 13]
                        else:
                            phaseDuration = [13, 13, 13, 53]
                    else:
                        [agents[key].currentAction, phaseDuration,
                         actionType] = ActionSelection.actionSelectionFirstLevel(numberOfAction, agents[
                            key].probabilityOfRandomAction, agents[key].qTable[agents[key].currentState], key,
                                                                                 density[1], density[2],
                                                                                 density[3], currentAction,
                                                                                 networkDetails)
                        if agents[key].probabilityOfRandomAction[
                            agents[key].currentState] >= eGreedy and actionType == "random":
                            agents[key].probabilityOfRandomAction[agents[key].currentState] -= decayProbability
                    # Set green time for each phase
                    ECIChangeTimingPhase(agents[key].id, 1, phaseDuration[0], timeSta)
                    ECIChangeTimingPhase(agents[key].id, 3, phaseDuration[1], timeSta)
                    ECIChangeTimingPhase(agents[key].id, 5, phaseDuration[2], timeSta)
                    ECIChangeTimingPhase(agents[key].id, 7, phaseDuration[3], timeSta)
                # Get reward second level
                [rewardSecondLevel, secondLevelAgents[h].oldDta] = GetReward.getRewardSecondLevel(dta,
                                                                                                  secondLevelAgents[
                                                                                                      h].oldDta)
                # Get reward first level and update Q-Table
                for key in holonsMap[h]:
                    if currentAction == 3 or currentAction == 5 and agents[key].id == density[3]:
                        if agents[key].id == 536:
                            AKIPrintString("Forced Action")
                        agents[key].state = agents[key].currentState
                        agents[key].action = agents[key].currentAction
                    else:
                        delayTime = [0] * 4
                        for i in range(4):
                            statisticalInfo = AKIEstGetParcialStatisticsSection(agents[key].idSectionIn[i], 100, 0)
                            if statisticalInfo.report == 0:
                                delayTime[i] = statisticalInfo.DTa
                        [reward, agents[key].oldDta] = GetReward.getRewardFirstLevel(agents[key].oldDta, delayTime)
                        reward = (0.7 * reward) + (0.3 * rewardSecondLevel)
                        # Update Q-table
                        agents[key].qTable[agents[key].state][agents[key].action] = QLearning.updateQTable(
                            agents[key].qTable[agents[key].state][agents[key].action],
                            agents[key].qTable[agents[key].currentState][agents[key].currentAction], agents[key].state,
                            agents[key].action, agents[key].currentState, agents[key].currentAction, reward,
                            agents[key].learningRate, agents[key].discountFactor)
                        if agents[key].learningRate >= 0.01:
                            agents[key].learningRate -= decayLearningRate
                        if agents[key].discountFactor <= 0.8:
                            agents[key].discountFactor += incrementDiscountFactor
                        if agents[key].id == 536:
                            AKIPrintString("[536]:from " +
                                           str(agents[key].state) + " to " +
                                           str(agents[key].currentState) +
                                           " with action " + str(agents[key].currentAction) +
                                           " reward : " + str(reward))
                        agents[key].state = agents[key].currentState
                        agents[key].action = agents[key].currentAction
                # Update Q-Table
                secondLevelAgents[h].qTable[secondLevelAgents[h].state][
                    secondLevelAgents[h].action] = QLearning.updateQTable(
                    secondLevelAgents[h].qTable[secondLevelAgents[h].state][secondLevelAgents[h].action],
                    secondLevelAgents[h].qTable[currentState][currentAction], secondLevelAgents[h].state,
                    secondLevelAgents[h].action, currentState, currentAction, rewardSecondLevel,
                    secondLevelAgents[h].learningRate, secondLevelAgents[h].discountFactor)
                if secondLevelAgents[h].learningRate >= 0.01:
                    secondLevelAgents[h].learningRate -= decayLearningRateSecondLevel
                if secondLevelAgents[h].discountFactor <= 0.8:
                    secondLevelAgents[h].discountFactor += incrementDiscountFactorSecondLevel
                if h == 0:
                    AKIPrintString("[high_level_agents 0]from " + str(secondLevelAgents[h].state) + " to " +
                                   str(currentState) + " with action " +
                                   str(secondLevelAgents[h].action) + " reward : " + str(rewardSecondLevel))
                secondLevelAgents[h].state = currentState
                secondLevelAgents[h].action = currentAction
            else:
                for key in holonsMap[h]:
                    # Get State
                    longQueueInSection = [0] * 4
                    for i in range(4):
                        statisticalInfo = AKIEstGetParcialStatisticsSection(agents[key].idSectionIn[i], 100, 0)
                        if statisticalInfo.report == 0:
                            longQueueInSection[i] = statisticalInfo.LongQueueMax
                    agents[key].currentState = GetState.getState(longQueueInSection)
                    # Action selection
                    [agents[key].currentAction, phaseDuration, actionType] = ActionSelection.actionSelection(
                        agents[key].probabilityOfRandomAction[agents[key].currentState],
                        agents[key].qTable[agents[key.currentState]], numberOfAction)
                    if agents[key].probabilityOfRandomAction[
                        agents[key].currentState] >= eGreedy and actionType == "random":
                        agents[key].probabilityOfRandomAction[agents[key].currentState] -= decayProbability
                    # Set green time for each phase
                    ECIChangeTimingPhase(agents[key].id, 1, phaseDuration[0], timeSta)
                    ECIChangeTimingPhase(agents[key].id, 3, phaseDuration[1], timeSta)
                    ECIChangeTimingPhase(agents[key].id, 5, phaseDuration[2], timeSta)
                    ECIChangeTimingPhase(agents[key].id, 7, phaseDuration[3], timeSta)
                    # Get reward
                    delayTime = [0] * 4
                    for i in range(4):
                        statisticalInfo = AKIEstGetParcialStatisticsSection(agents[key].idSectionIn[i], 100, 0)
                        if statisticalInfo.report == 0:
                            delayTime[i] = statisticalInfo.DTa
                    [reward, agents[key].oldDta] = GetReward.getRewardFirstLevel(agents[key].oldDta, delayTime)
                    # Update Q-value
                    agents[key].qTable[agents[key].state][agents[key].action] = QLearning.updateQTable(
                        agents[key].qTable[agents[key].state][agents[key].action],
                        agents[key].qTable[agents[key].currentState][agents[key].currentAction], agents[key].state,
                        agents[key].action, agents[key].currentState, agents[key].currentAction, reward,
                        agents[key].learningRate, agents[key].discountFactor)
                    if agents[key].learningRate >= 0.01:
                        agents[key].learningRate -= decayLearningRate
                    if agents[key].discountFactor <= 0.8:
                        agents[key].discountFactor += incrementDiscountFactor
                    agents[key].state = agents[key].currentState
                    agents[key].action = agents[key].currentAction

        if changeFlagCreateNewHolon:
            flag = True
            AKIPrintString("Holons Changed")
            changeFlagCreateNewHolon = False
        if int(time) % 3600 == 0:
            f = open('Q_val.txt', 'w')
            for h in range(len(secondLevelAgents)):
                f.write("Agent " + str(h) + "\n")
                for i in range(numberOfStateSecondLevel):
                    for j in range(numberOfActionSecondLevel):
                        f.write(str(secondLevelAgents[h].qTable[i][j]) + "   ")
                    f.write("\n")
            f.close()
        return 0
    return 0


def AAPIFinish():
    AKIPrintString("Finish")
    return 0


def AAPIUnLoad():
    AKIPrintString("UnLoad")
    return 0


def AAPIEnterVehicle(idveh, idsection):
    return 0


def AAPIExitVehicle(idveh, idsection):
    return 0
