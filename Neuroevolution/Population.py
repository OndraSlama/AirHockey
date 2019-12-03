import numpy as np
from Constants import *
class Population():
    def __init__(self, mutRate = 0.15, surRatio = 0.25):
        self.players = []
        self.genomes = []
        self.generation = 0
        self.mutationRate = mutRate
        self.surviveRatio = surRatio
        self.globalBestPlayer = None
        self.bestPlayers = []
        
    def CreateGeneration(self, gameEntities):
        self.popSize = len(gameEntities)
        self.generation += 1
        self.genomes = []
        self.players = []
        for i in range(self.popSize):
            if gameEntities[i].aiControlled:
                self.players.append(Player(gameEntities[i]))  

    def GeneticCycle(self):
        self.ComputeFitness()
        self.Selection()
        self.Populate()
        self.Mutate()
        return self.genomes

    def ComputeFitness(self):
        for player in self.players:
            player.fitness = (player.gameEntity.length - snakeInitialLength) * player.gameEntity.traveled/10
            player.absoluteFitness = player.fitness

    def Selection(self):
        # Sort acording to fitness
        self.players.sort(key=lambda x: x.fitness, reverse=True)

        # Save best players
        self.bestPlayers.append(self.players[0])
        if self.globalBestPlayer != None:
            if self.globalBestPlayer.absoluteFitness < self.players[0].absoluteFitness: self.globalBestPlayer = self.players[0]
        else:
            self.globalBestPlayer = self.players[0]

        # Save best genomes
        for i in range(round(self.popSize*self.surviveRatio)):
            self.genomes.append(self.players[i].gameEntity.brain)        

    def Populate(self):
        # normalize fitness
        bestFitness = self.players[0].fitness
        for player in self.players:
            player.fitness = player.fitness / max(bestFitness, 1) # divide by the best player
        
        # create probability array for wich genomes are to be cloned
        fitnessSum = sum(p.fitness for p in self.players[:len(self.genomes)-1]) #sum normalized fitness of the selected players
        probArray = [] 
        for i in range(len(self.genomes)):
            probArray.append(self.players[i].fitness/max(fitnessSum, 1))      

        # create new population
        # self.genomes = []
        for i in range(self.popSize - len(self.genomes)):            
            self.genomes.append(self.SelectGenom(probArray).Copy())

    def SelectGenom(self, probArray):
        cumProbability = 0
        p = np.random.rand()
        for i in range(len(probArray)): 
            cumProbability += probArray[i]
            if(p <= cumProbability):
                return self.genomes[i]

    def Mutate(self):
        for genom in self.genomes:
            genom.Mutate(self.mutationRate)

    



class Player():
    def __init__(self, gameEntity):
        self.gameEntity = gameEntity
        self.fitness = 0
        self.absoluteFitness = 0



