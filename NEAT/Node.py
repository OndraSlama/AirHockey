import numpy as np

class Node():
    def __init__(self, number):
        self.number = number
        self.inputSum = 0
        self.outputValue = 0
        self.outputConnections = []
        self.layer = 0
        self.drawPos = None

    def Engage(self):
        if self.layer != 0: #no sigmoid for the inputs and bias
            self.outputValue = self.Sigmoid(self.inputSum)        

        for output in self.outputConnections: # for each connection
            if output.enabled:
                output.toNode.inputSum += output.weight * self.outputValue; #add the weighted output to the sum of the inputs of whatever node is connected to  
        
        self.inputSum = 0

    def Sigmoid(self, num):
        return 1/(1 + np.exp(-num))

    def isConnectedTo(self, node):
        # if node.layer == self.layer: return False

        for output in self.outputConnections:
            if output.toNode == node:
                return True

        return False

    def Clone(self):
        clone = Node(self.number)
        clone.inputSum = self.inputSum
        clone.outputValue = self.outputValue
        clone.outputConnections = self.outputConnections
        clone.layer = self.layer
        return clone
