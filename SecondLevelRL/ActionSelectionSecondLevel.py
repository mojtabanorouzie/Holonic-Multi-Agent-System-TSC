import random


def actionSelectionSecondLevel(randomProbability, qTable, numberOfAction):
    if random.random() > randomProbability:
        action = qTable.index(max(qTable))
        actionType = "best"
    else:
        action = random.randint(0, numberOfAction - 1)
        actionType = "random"
    return [action, actionType]
