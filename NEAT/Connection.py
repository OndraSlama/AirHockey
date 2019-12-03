import numpy as np
import random

class Connection():
    def __init__(self, fromNode, toNode, weight, innovation):
        self.fromNode = fromNode
        self.toNode = toNode
        self.weight = weight
        self.innovationNo = innovation
        self.enabled = True

    def MutateWeight(self):
        if random.random() < 0.1: # 10% of the time completely change the this.weight
            self.weight = random.random() * 2 - 1
        else:
            self.weight += random.gauss(0, 1/35)
            if self.weight > 1: self.weight = 1
            if self.weight < -1: self.weight = -1

    def Clone(self, fromNode, toNode):
        clone = Connection(fromNode, toNode, self.weight, self.innovationNo)
        clone.enabled = self.enabled
        return clone
