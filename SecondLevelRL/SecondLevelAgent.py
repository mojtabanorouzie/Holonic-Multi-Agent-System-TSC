import random


class SecondLevelRLAgent:
    def __init__(self, numberOfStateSecondLevel, numberOfActionSecondLevel, initLearningRate, initDiscountFactor):
        self.state = random.randint(0, numberOfStateSecondLevel - 1)
        self.action = random.randint(0, numberOfActionSecondLevel - 1)
        self.lastAction = random.randint(0, numberOfActionSecondLevel - 1)
        self.probabilityOfRandomAction = [1.0 for i in range(numberOfStateSecondLevel)]
        self.qTable = [[0 for i in range(numberOfActionSecondLevel)] for j in range(numberOfStateSecondLevel)]
        self.learningRate = initLearningRate
        self.discountFactor = initDiscountFactor
        self.oldDta = [0 for i in range(5)]
