import numpy as np
from Constants import *
from Genome import *
from math import floor
from ConnectionHistory import Innovation
from Species import *
class Population():
    def __init__(self, mutRate = 0.15, surRatio = 0.25):
        self.innovations = Innovation()
        self.players = []
        self.genomes = []
        self.species = []
        self.generation = 0
        self.mutationRate = mutRate
        self.surviveRatio = surRatio
        self.globalBestPlayer = None
        self.globalBestFitness = 0
        self.bestPlayers = []
        self.massExtinctionEvent = False

        # for i in range(10):
        #     self.genomes.append(Genome(5, 2))
        #     self.genomes[i].AddConnection(self.innovations, 1, 6)
        #     self.genomes[i].AddConnection(self.innovations, 2, 5)
        #     self.genomes[i].AddNode(self.innovations, 0)
        #     self.genomes[i].AddNode(self.innovations, 1)
        #     self.genomes[i].AddNode(self.innovations)
        #     self.genomes[i].Mutate(self.innovations)
        #     self.genomes[i].GenerateNetwork()
        #     self.players.append(debugPlayer(self.genomes[i]))
        
        # self.Speciate()
        # self.SortSpecies()
        # self.genomes
        
        
    def CreateGeneration(self, gameEntities = []):
        self.players = []
        self.genomes = []

        for i in range(len(gameEntities)):
            if gameEntities[i].aiControlled:
                self.players.append(gameEntities[i])  
        self.Speciate()
        self.popSize = len(self.players)
        self.generation += 1
        

    def GeneticCycle(self):        
        self.ComputeFitness()
        self.SortSpecies() #sort the self.species to be ranked in fitness order, best first
        self.SetBestPlayer() #save the best player
        self.Selection() #select worthy players
        self.Populate()
        return self.genomes

    def Speciate(self):
        for s in self.species:
            s.players = []
        
        for player in self.players:
            speciesFound = False
            for s in self.species:
                if s.SameSpecies(player.brain):
                    s.AddPlayer(player)
                    speciesFound = True
                    break
            
            if not speciesFound:
                self.species.append(Species(player))

        for i in range(len(self.species) - 1, -1, -1):            
            if len(self.species[i].players) == 0:
                self.species.pop(i)

    def ComputeFitness(self):
        for player in self.players:
            player.CalculateFitness()

    def SortSpecies(self):
        # sort players
        self.players.sort(key=lambda x: x.fitness, reverse=True) 

        # sort the players within a self.species
        for s in self.species:
            s.SortSpecies()        

        # sort the self.species by the fitness of its best player
        self.species.sort(key=lambda x: x.bestFitness, reverse=True)    
    
    def Selection(self):
        if self.massExtinctionEvent:
            self.MassExtinction()
            self.massExtinctionEvent = False
        self.CullSpecies() #kill off the bottom half of each self.species
        self.KillStaleSpecies() #remove self.species which haven't improved in the last 15(ish)self.generations
        self.KillBadSpecies() #kill self.species which are so bad that they cant reproduce

    def MassExtinction(self):
        for i in range(len(self.species) - 1, 5, -1):
            self.species.pop(i)

    def CullSpecies(self):
        for s in self.species:
            s.Cull() #kill bottom half
            # s.FitnessSharing() #also while we're at it lets do fitness sharing
            s.SetAverageFitness() #reset averages because they will have changed

    def SetBestPlayer(self):
        # Save best players
        self.bestPlayers.append(self.players[0])
        if self.globalBestPlayer != None:
            if self.globalBestFitness < self.players[0].fitness: 
                self.globalBestPlayer = self.players[0]
                self.globalBestFitness = self.players[0].fitness
        else:
            self.globalBestPlayer = self.players[0]        
        

    def KillStaleSpecies(self):
        if len(self.species) > 1:
            for i in range(len(self.species) - 1, -1, -1):
                if self.species[i].staleness >= 200:
                    self.species.pop(i)

    def KillBadSpecies(self):
        averageSum = self.GetAvgFitnessSum()

        for i in range(len(self.species) - 1, -1, -1):
            if not(averageSum == 0):
                if self.species[i].averageFitness / averageSum * len(self.players) < 1:  #if wont be given a single child
                    self.species.pop(i)   
            elif len(self.species[i].players) == 0:
                self.species.pop(i)


    def Populate(self):
        averageSum = self.GetAvgFitnessSum()

        for s in self.species: #for each self.species
            self.genomes.append(s.rep.Clone()) #add representant without any mutation
            if not(averageSum == 0):
                noOfChildren = floor(s.averageFitness / averageSum * len(self.players)) - 1 #the number of children self self.species is allowed, note -1 is because the champ is already added
            else:
                noOfChildren = len(self.players) - 1

            for i in range(noOfChildren):  #get the calculated amount of children from self self.species
                self.genomes.append(s.GetChild(self.innovations))

        while (len(self.genomes) < len(self.players)): #if not enough babies (due to flooring the number of self.genomes to get a whole 
            self.genomes.append(self.species[0].GetChild(self.innovations)) #get babies from the best self.species
        
        for genom in self.genomes: #generate networks for each of the children
            genom.GenerateNetwork()
        

    def GetAvgFitnessSum(self):
        averageSum = 0
        for s in self.species:
            averageSum += s.averageFitness        
        return averageSum
    

class debugPlayer():
    def __init__(self, genom):
        self.brain = genom
        self.fitness = random.randint(0,100)
        self.color = None




