import random


class SecondLevelRLAgent:
    def __init__(self, numberOfStateSecondLevel, numberOfActionSecondLevel, initLearningRate, initDiscountFactor):
        self.state = random.randint(0, numberOfStateSecondLevel - 1)
        # self.currentState = random.randint(0, numberOfStateSecondLevel - 1)
        self.action = random.randint(0, numberOfActionSecondLevel - 1)
        # self.currentAction = random.randint(0, numberOfActionSecondLevel - 1)
        self.probabilityOfRandomAction = [1.0 for i in range(numberOfStateSecondLevel)]
        self.qTable = [[0 for i in range(numberOfActionSecondLevel)] for j in range(numberOfStateSecondLevel)]
        self.learningRate = initLearningRate
        self.discountFactor = initDiscountFactor
        self.oldDta = [0 for i in range(5)]


def getMaxDensity(array):
    maximum = max(array[i][0] for i in range(len(array)))
    for i in range(len(array)):
        if array[i][0] == maximum:
            return array[i]


def getStateSuperHolon(eta):
    if (0 <= eta) and (eta < 0.1):
        return 0
    elif (0.1 <= eta) and (eta < 0.2):
        return 1
    elif (0.2 <= eta) and (eta < 0.3):
        return 2
    elif (0.3 <= eta) and (eta < 0.4):
        return 3
    elif 0.4 <= eta:
        return 4
