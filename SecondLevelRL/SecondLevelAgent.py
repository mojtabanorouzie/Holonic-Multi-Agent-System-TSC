import random


class SecondLevelRLAgent:
    def __init__(self, numberOfStateSecondLevel, numberOfActionSecondLevel, initLearningRate, initDiscountFactor):
        self.state = random.randint(0, numberOfStateSecondLevel - 1)
        self.currentState = random.randint(0, numberOfStateSecondLevel - 1)
        self.action = random.randint(0, numberOfActionSecondLevel - 1)
        self.currentAction = random.randint(0, numberOfActionSecondLevel - 1)
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
