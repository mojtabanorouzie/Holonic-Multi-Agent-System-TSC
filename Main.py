from AAPI import *
from ReinforcementLearningPack import QLearning, GetState, GetReward, CreateDataSet
from SecondLevelRL import CreateHolon, SecondLevelAgent, ActionSelection

# Global Variables
warmup = 1800
cycle = 100
eGreedy = 0.01
initLearningRate = 0.5
initDiscountFactor = 0.5
decayProbability = 0.02
decayLearningRate = 0.005
incrementDiscountFactor = 0.005
numberOfState = 24
numberOfAction = 19
tempTime = -1
agents = {}
createDataSet = False

# Second level agent global variables
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
secondLevelAgents = []

# Network details
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
    numberOfJunctions = AKIInfNetNbJunctions()
    global agents
    for index in range(numberOfJunctions):
        # Get attribute of network
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
        # Initial Agent
        agents[AKIInfNetGetJunctionId(index)] = QLearning.ReinforcementLearningAgent(junctionId, junctionIdSectionIn,
                                                                                     junctionIdSectionOut, controlType,
                                                                                     numOfPhases, numberOfAction,
                                                                                     numberOfState, initLearningRate,
                                                                                     initDiscountFactor)
    return 0


def AAPIManage(time, timeSta, timTrans, SimStep):
    return 0


def AAPIPostManage(time, timeSta, timTrans, SimStep):
    global agents, nodes, edges, tempTime, flag, secondLevelAgents
    if time == 0.75:
        # 1. Create first graph from network
        [nodes, edges] = CreateHolon.createFirstGraph(agents)
    if int(time) % cycle == 0 and int(time) != tempTime and int(time) > warmup and flag:
        tempTime = int(time)
        flag = False
        tempEdges = edges.copy()
        # 2. Create final graph
        tempEdges = CreateHolon.createSecondGraph(tempEdges)
        # 3. Create holons
        holons = CreateHolon.createHolon(nodes, tempEdges)
        for i in range(len(holons)):
            holonsMap[i] = []
            edgesMap[i] = []
            for j in holons[i].members:
                holonsMap[i].append(j)
            for j in holons[i].edgeMember:
                edgesMap[i].append(j)
        for index in range(len(holons)):
            AKIPrintString("holon [" + str(index) + "]  =  " + str(holonsMap[index]))
        # 4. Create second level agents
        secondLevelAgents.append(
            SecondLevelAgent.SecondLevelRLAgent(numberOfStateSecondLevel, numberOfActionSecondLevel,
                                                initLearningRateSecondLevel, initDiscountFactorSecondLevel))
    if int(time) % cycle == 0 and int(time) != tempTime and int(time) > warmup:
        tempTime = int(time)
        for h in range(len(secondLevelAgents)):
            if len(holonsMap[h]) > 1:
                # Get state first level
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
                        tempDensity[0] = statisticalInfo.Density / 200
                        tempDensity[1] = e.id1
                        tempDensity[2] = e.startNode
                        tempDensity[3] = e.endNode
                        allSectionDensity.append(tempDensity)
                    tempDensity = [0, 0, 0, 0]
                    statisticalInfo = AKIEstGetParcialStatisticsSection(e.id2, 100, 0)
                    if statisticalInfo.report == 0:
                        tempDensity[0] = statisticalInfo.Density / 200
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
                    ECIChangeTimingPhase(agents[index].id, 1, phaseDuration[0], timeSta)
                    ECIChangeTimingPhase(agents[index].id, 3, phaseDuration[1], timeSta)
                    ECIChangeTimingPhase(agents[index].id, 5, phaseDuration[2], timeSta)
                    ECIChangeTimingPhase(agents[index].id, 7, phaseDuration[3], timeSta)
                # Get reward second level
                [rewardSecondLevel, secondLevelAgents[h].oldDta] = getRewardSecondLevel(dta, secondLevelAgents[h].oldDta)
                for key in holonsMap[h]:
                    if (secondLevelAgents[h].currentAction == 3 or secondLevelAgents[h].currentAction == 5) and (agents[key].id == density[3]):
                        if agents[key].id == 536:
                            AKIPrintString("Forced Action")
                        agents[key].state = agents[key].currentState
                        agents[key].action = agents[key].currentAction
                    else:
                        [reward, agents[key].oldDta] = GetReward.getReward(agents[key].idSectionIn, agents[key].oldDta)
                        reward = (0.7 * reward) + (0.3 * rewardSecondLevel)
                        # Update Q-table
                        agents[key].qTable[agents[key].state][agents[key].action] += \
                            agents[key].learningRate * (reward + (
                            agents[key].discountFactor * agents[key].qTable[agents[key].currentState][
                                agents[key].currentAction]) - agents[key].qTable[agents[key].state][agents[key].action])
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

                secondLevelAgents[h].qTable[secondLevelAgents[h].state][secondLevelAgents[h].pre_action] \
                    += secondLevelAgents[h].learningRate * (rewardSecondLevel + (secondLevelAgents[h].discountFactor *
                                                                        secondLevelAgents[h].
                                                                        qTable[secondLevelAgents[h].
                                                                        currentState][secondLevelAgents[h].action])
                                                  - secondLevelAgents[h].qTable[secondLevelAgents[h].
                                                  state][secondLevelAgents[h].pre_action])
                if secondLevelAgents[h].learningRate >= 0.01:
                    secondLevelAgents[h].learningRate -= decay_learningRate_h
                if secondLevelAgents[h].discountFactor <= 0.8:
                    secondLevelAgents[h].discountFactor += decay_discountFactor_h
                if h == 3:
                    AKIPrintString("[secondLevelAgents 0]from " + str(secondLevelAgents[h].state) + " to " +
                                   str(secondLevelAgents[h].currentState) + " with action " +
                                   str(secondLevelAgents[h].action) + " reward : " + str(rewardSecondLevel))
                secondLevelAgents[h].state = secondLevelAgents[h].currentState
            else:
                for key in holonsMap[h]:
                    agents[key].currentState = get_state(agents[key].idSectionIn)
                    agents[key].pre_action = agents[key].action
                    density = [0, 0, 0, 0]
                    agents[key].action = \
                        action_selection_sub_holon(key, density[1], density[2], density[3], 0)
                    do_action(agents[key].id, timeSta, agents[key].action)
                    [reward, agents[key].old_dta] = \
                        get_reward_sub_holon(agents[key].idSectionIn, agents[key].old_dta)
                    # Update Q-table
                    agents[key].qTable[agents[key].state][agents[key].pre_action] += \
                        agents[key].learningRate * (reward + (agents[key].discountFactor *
                                                           agents[key].qTable[agents[key].
                                                           currentState][agents[key].action]) -
                                                 agents[key].
                                                 qTable[agents[key].state][agents[key].pre_action])
                    if agents[key].learningRate >= 0.01:
                        agents[key].learningRate -= decay_learningRate
                    if agents[key].discountFactor <= 0.8:
                        agents[key].discountFactor += decay_discountFactor
                    if agents[key].id == 536:
                        AKIPrintString("from " +
                                       str(agents[key].state) + " to " + str(agents[key].currentState) +
                                       " with action " + str(agents[key].action) + " reward : " + str(reward))
                    agents[key].state = agents[key].currentState


        ################################################################################################################
        numberOfJunctions = AKIInfNetNbJunctions()
        for index in xrange(numberOfJunctions):
            # 1. Get feature from network (Long Queue, Delay Time and Density)
            longQueueInSection = [0] * 4
            delayTime = [0] * 4
            density = [0] * 4
            if AKIIsGatheringStatistics() >= 0:
                for i in range(4):
                    statisticalInfo = AKIEstGetParcialStatisticsSection(agents[index].idSectionIn[i], 100, 0)
                    if statisticalInfo.report == 0:
                        longQueueInSection[i] = statisticalInfo.LongQueueMax
                        delayTime[i] = statisticalInfo.DTa
                        density[i] = statisticalInfo.Density
                    else:
                        longQueueInSection[i] = 0
                        delayTime[i] = 0
                        density[i] = 0
            else:
                AKIPrintString("Warning AKIIsGatheringStatistics")
            # 2. Get State
            currentState = GetState.getState(longQueueInSection)
            # 3.1 Action Selection
            [currentAction, phaseDuration, actionType] = ActionSelection.actionSelection(
                agents[index].probabilityOfRandomAction[currentState], agents[index].qTable[currentState],
                numberOfAction)
            if agents[index].probabilityOfRandomAction[currentState] >= eGreedy and actionType == "random":
                agents[index].probabilityOfRandomAction[currentState] -= decayProbability
            # 3.2 Set green time for each phase
            ECIChangeTimingPhase(agents[index].id, 1, phaseDuration[0], timeSta)
            ECIChangeTimingPhase(agents[index].id, 3, phaseDuration[1], timeSta)
            ECIChangeTimingPhase(agents[index].id, 5, phaseDuration[2], timeSta)
            ECIChangeTimingPhase(agents[index].id, 7, phaseDuration[3], timeSta)
            # 4. Get Reward
            [reward, agents[index].oldDta] = GetReward.getReward(agents[index].oldDta, delayTime)
            # 5 .Create dataset of agent experience
            if createDataSet and actionType == "best" and CreateDataSet.check_convergence(
                    agents[index].counter[agents[index].state], reward):
                CreateDataSet.create_dataset(agents[index].state, agents[index].action, delayTime, density,
                                             longQueueInSection)
            # 6. Update Q-Table
            agents[index].qTable[agents[index].state][agents[index].action] = QLearning.updateQTable(
                agents[index].qTable[agents[index].state][agents[index].action],
                agents[index].qTable[currentState][currentAction], agents[index].state, agents[index].action,
                currentState, currentAction, reward, agents[index].learningRate, agents[index].discountFactor)
            # 7. Update learning rate and discount factor
            if agents[index].learningRate >= 0.01:
                agents[index].learningRate -= decayLearningRate
            if agents[index].discountFactor <= 0.9:
                agents[index].discountFactor += incrementDiscountFactor
            if agents[index].id == 549:
                AKIPrintString(
                    "from " + str(agents[index].state) + " to " + str(currentState) + " | with action " + str(
                        agents[index].action) + " | reward : " + str(reward) + " | action type : " + str(actionType))
            # 8. Set new state and action
            agents[index].counter[agents[index].state] += 1
            agents[index].state = currentState
            agents[index].action = currentAction
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
