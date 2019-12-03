from Node import *
from Connection import *
from ConnectionHistory import *
import numpy as np
import random

class Genome():
    def __init__(self, inputs, outputs, copying = False):
        self.connections = []
        self.nodes = []
        self.inputs = inputs
        self.outputs = outputs
        self.layers = 2
        self.nextNode = 0
        self.network = []

        if copying:
            return

        for i in range(self.inputs):
            self.nodes.append(Node(i))
            self.nodes[i].layer = 0
            self.nextNode += 1
        
        for i in range(self.outputs):
            self.nodes.append(Node(i + self.inputs))
            self.nodes[i + self.inputs].layer = 1
            self.nextNode += 1

        self.nodes.append(Node(self.nextNode))
        self.biasNode = self.nextNode
        self.nodes[self.biasNode].layer = 0
        self.nextNode += 1

    def FullyConnect(self, innovation):
        for i in range(self.inputs):
            for o in range(self.outputs):
                innovationNo = self.GetInnovationNumber(innovation, self.nodes[i], self.nodes[len(self.nodes) - o - 2])
                self.connections.append(Connection(self.nodes[i], self.nodes[len(self.nodes) - o - 2], random.random() * 2 - 1, innovationNo))
        
        for o in range(self.outputs):
            innovationNo = self.GetInnovationNumber(innovation, self.nodes[self.biasNode], self.nodes[len(self.nodes) - o - 2])
            self.connections.append(Connection(self.nodes[self.biasNode], self.nodes[len(self.nodes) - o - 2], random.random() * 2 - 1, innovationNo))
        # innovationNo = self.GetInnovationNumber(innovation, self.nodes[i], self.nodes[len(self.nodes) - j - 2])

    def GetNode(self, nodeNo):
        for node in self.nodes:
            if node.number == nodeNo:
                return node
        
        return None

    def FullyConnected(self):
        maxConnections = 0
        nodesInLayers = []
        for layer in range(self.layers):
            nodesInLayers.append(0)

        for node in self.nodes:
            nodesInLayers[node.layer] += 1
        
        for layer in range(self.layers):
            nodesInFront = 0
            for i in range(self.layers - layer - 1):
                nodesInFront += nodesInLayers[i + 1]

            maxConnections += nodesInLayers[layer] * nodesInFront
        
        for layer in range(2, self.layers):
            nodesInBack = 0
            for i in range(2, layer):
                nodesInBack += nodesInLayers[i - 1]

            maxConnections += nodesInLayers[layer] * nodesInBack

        if maxConnections == len(self.connections): return True

        return False

    def Forward(self, inputValues):
        # set the outputs of the input self.nodes
        for i in range(self.inputs): 
            self.nodes[i].outputValue = inputValues[i]
        
        self.nodes[self.biasNode].outputValue = 1 # output of bias is 1

        for node in self.network: # for each node in the network engage it(see node class for what self does)
            node.Engage()
        
        outs = []
        # the outputs are self.nodes[inputs] to self.nodes [inputs+outputs-1]
        for i in range(self.outputs):
            outs.append(self.nodes[self.inputs + i].outputValue)    

        # for node in self.nodes: # reset all the self.nodes for the next feed forward
        #     node.inputSum = 0
        

        return outs
    



    def AddConnection(self, innovation, randNode1 = None, randNode2 = None):

        if self.FullyConnected():
            # print("Already fully connected")
            return
        if randNode1 == None:
            randNode1 = random.randint(0, len(self.nodes)-1)
        if randNode2 == None:
            randNode2 = random.randint(0, len(self.nodes)-1)

        while self.BadConnectionNodes(randNode1, randNode2):
            randNode1 = random.randint(0, len(self.nodes)-1)
            randNode2 = random.randint(0, len(self.nodes)-1)

        if self.nodes[randNode1].layer == self.nodes[randNode2].layer:
            self.InsertLayerAfter(self.nodes[randNode1].layer)
            self.nodes[randNode2].layer += 1

        innovationNo = self.GetInnovationNumber(innovation, self.nodes[randNode1], self.nodes[randNode2])
        self.connections.append(Connection(self.nodes[randNode1], self.nodes[randNode2], random.random() * 2 - 1, innovationNo))
        self.ConnectNodes()

    def BadConnectionNodes(self, node1, node2):
        if self.nodes[node1] == self.nodes[node2]: return True
        if self.nodes[node1].layer == self.nodes[node2].layer and (self.nodes[node1].layer == 0 or self.nodes[node1].layer == self.layers - 1): return True
        if self.nodes[node2].layer == 0: return True
        if self.nodes[node1].isConnectedTo(self.nodes[node2]): return True

    def InsertLayerAfter(self, layer):
        for node in self.nodes:
            if node.layer > layer:
                node.layer += 1
        self.layers += 1

    def AddNode(self, innovation, randConnection = None):
        print('Adding node.')
        if len(self.connections) == 0:
            self.AddConnection(innovation)
            return

        if randConnection == None:
            randConnection = random.randint(0, len(self.connections)-1)

        while self.BadRandomConnection(randConnection):
            randConnection = random.randint(0, len(self.connections)-1)

        self.connections[randConnection].enabled = False

        newNodeNo = self.nextNode
        self.nodes.append(Node(newNodeNo))
        self.nextNode += 1
        
        innovationNo = self.GetInnovationNumber(innovation, self.connections[randConnection].fromNode, self.GetNode(newNodeNo))
        self.connections.append(Connection(self.connections[randConnection].fromNode, self.GetNode(newNodeNo), 1, innovationNo))

        innovationNo = self.GetInnovationNumber(innovation, self.GetNode(newNodeNo), self.connections[randConnection].toNode)
        self.connections.append(Connection(self.GetNode(newNodeNo), self.connections[randConnection].toNode, self.connections[randConnection].weight, innovationNo))

        innovationNo = self.GetInnovationNumber(innovation, self.nodes[self.biasNode], self.GetNode(newNodeNo))
        self.connections.append(Connection(self.nodes[self.biasNode], self.GetNode(newNodeNo), 0, innovationNo))

        fromLayer = self.connections[randConnection].fromNode.layer
        toLayer = self.connections[randConnection].toNode.layer
        if fromLayer < toLayer:
            if fromLayer + 1 == self.connections[randConnection].toNode.layer:
                self.InsertLayerAfter(fromLayer)

            self.GetNode(newNodeNo).layer = fromLayer + 1
        else:
            if toLayer + 1 == self.connections[randConnection].toNode.layer:
                self.InsertLayerAfter(toLayer)

            self.GetNode(newNodeNo).layer = toLayer + 1

        self.ConnectNodes()

    def BadRandomConnection(self, randConnection):
        if self.connections[randConnection].fromNode == self.nodes[self.biasNode] and len(self.connections) != 1: return True
        if self.connections[randConnection].fromNode.layer > self.connections[randConnection].toNode.layer: return True
        return False

    def Mutate(self, innovation):
        if len(self.connections) == 0:
            self.AddConnection(innovation)
        
        if random.random() < 0.8:
            for connection in self.connections:
                connection.MutateWeight()

        if random.random() < 0.05:
            self.AddConnection(innovation)

        if random.random() < 0.008:
            self.AddNode(innovation)
    
    def Crossover(self, parent2):
        child = Genome(self.inputs, self.outputs, True)
        child.connections = []
        child.nodes = []
        child.layers = self.layers
        child.nextNode = self.nextNode
        child.biasNode = self.biasNode
        childGenes = []
        isEnabled = []

        for connection in self.connections:
            setEnabled = True
            parent2Connection = self.MatchingConnection(parent2, connection.innovationNo)
            if parent2Connection != -1:
                if not connection.enabled or not parent2.connections[parent2Connection].enabled:
                    if random.random() < 0.75: setEnabled = False

                if random.random() < 0.5: 
                    childGenes.append(connection)
                else:
                    childGenes.append(parent2.connections[parent2Connection])
            else: # disjoint or excess connection
                childGenes.append(connection)
                setEnabled = connection.enabled

            isEnabled.append(setEnabled)

        for node in self.nodes:
            child.nodes.append(node.Clone())

        for i in range(len(childGenes)):
            child.connections.append(childGenes[i].Clone(child.GetNode(childGenes[i].fromNode.number), child.GetNode(childGenes[i].toNode.number)))
            child.connections[i].enabled = isEnabled[i]

        child.ConnectNodes()
        return child

                    

    def MatchingConnection(self, parent2, innovationNumber):
        for i in range(len(parent2.connections)):
            if parent2.connections[i].innovationNo == innovationNumber: return i
        return -1

    def ConnectNodes(self):
        for node in self.nodes:
            node.outputConnections = [] # clear connections

        for connection in self.connections:
            connection.fromNode.outputConnections.append(connection) # assign connection to node

    def GenerateNetwork(self):
        self.ConnectNodes()
        self.network = []

        for layer in range(self.layers):
            for node in self.nodes:
                if node.layer == layer:
                    self.network.append(node)

    def GetInnovationNumber(self, innovation, fromN, toN):
        connectionNo = innovation.nextInno
        isNew = True
   
        for history in innovation.history:
            if history.matches(self, fromN, toN):
                isNew = False
                connectionNo = history.innovationNumber
                # print("old Innovation")
                break

        if isNew:
            inNumbers = []
            for connection in self.connections:
                inNumbers.append(connection.innovationNo)
                
            innovation.history.append(ConnectionHistory(fromN.number, toN.number, connectionNo, inNumbers))
            innovation.nextInno += 1
            # print("new Innovation")

        return connectionNo


    def Clone(self):
        clone = Genome(self.inputs, self.outputs, True)

        for node in self.nodes:
            clone.nodes.append(node.Clone())

        for connection in self.connections:
            clone.connections.append(connection.Clone(clone.GetNode(connection.fromNode.number), clone.GetNode(connection.toNode.number)))

        clone.layers = self.layers
        clone.nextNode = self.nextNode
        clone.biasNode = self.biasNode
        clone.ConnectNodes()
        return clone

        
    
