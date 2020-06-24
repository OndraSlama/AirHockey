# ****************************************************************************** #
# Author: Ondrej Slama
# -------------------

# Zdrojovy kod vytvoreny v ramci projektu robotickeho vzdusneho hokeje - diplomova prace
#  na VUT FSI ustavu automatizace a informatiky v Brne.

# Source code created as a part of robotic air hockey table project - Diploma thesis
# at BUT FME institute of automation and computer sience.

# ****************************************************************************** #
import numpy as np
from Constants import *
from random import randint

class Population():
	def __init__(self, mutRate = 0.35, surRatio = 0.75):
		self.members = []
		self.genomes = []
		self.generation = 0
		self.mutationRate = mutRate
		self.surviveRatio = surRatio
		self.globalBestMember = None
		self.bestMembers = []
		self.availableGenoms = []
		
	def createGeneration(self, gameEntities, popSize = None):
		if popSize is None: popSize = len(gameEntities)
		
		self.popSize = popSize
		self.generation += 1
		self.genomes = []
		self.members = []
		for i in range(len(gameEntities)):			
			self.members.append(Member(gameEntities[i]))  

		self.availableGenoms = [i for i in range(popSize)]

	def geneticCycle(self):
		self.computeFitness()
		self.saveBest()
		self.selection()
		self.populate()
		self.mutate()
		return self.genomes

	def computeFitness(self):
		for member in self.members:
			member.relativeFitness = member.gameEntity.score
			member.absoluteFitness = member.relativeFitness

	def saveBest(self):
		# Sort acording to fitness
		self.members.sort(key=lambda x: x.relativeFitness, reverse=True)

		# Save best members
		self.bestMembers.append(self.members[0])
		if self.globalBestMember != None:
			if self.globalBestMember.absoluteFitness < self.members[0].absoluteFitness: self.globalBestMember = self.members[0]
		else:
			self.globalBestMember = self.members[0]

	def selection(self):		
		# Sort acording to fitness
		self.members.sort(key=lambda x: x.relativeFitness, reverse=True)

		# Save best genomes
		for i in range(round(len(self.members)*self.surviveRatio)):
			self.genomes.append(self.members[i].gameEntity.strategy.brain)		

	def populate(self):
		# normalize fitness
		bestFitness = self.members[0].relativeFitness
		for member in self.members:
			member.relativeFitness = member.absoluteFitness / max(bestFitness, 1) # divide by the best member
		
		# create probability array for wich genomes are to be cloned
		fitnessSum = sum(p.relativeFitness for p in self.members[:len(self.genomes)-1]) #sum normalized fitness of the selected members
		probArray = [] 
		for i in range(len(self.genomes)):
			probArray.append(self.members[i].relativeFitness/max(fitnessSum, 1))	  

		# create new population
		newGenomes = []
		for i in range(self.popSize):			
			newGenomes.append(self.selectGenom(probArray))
		
		self.genomes = newGenomes

	def selectGenom(self, probArray):
		if np.random.rand() < 0.7:
			cumProbability = 0
			p = np.random.rand()
			for i in range(len(probArray)): 
				cumProbability += probArray[i]
				if(p <= cumProbability):				
					return self.genomes[i].copy()	
			return self.genomes[randint(0, len(self.genomes)-1)].copy()

		elif np.random.rand() < 0.7:
			return self.genomes[randint(0, len(self.genomes)-1)].copy()
		else:
			return self.genomes[randint(0, len(self.genomes)-1)].copy().setRandomWeights()

	def mutate(self):
		for genom in self.genomes:
			genom.mutate(self.mutationRate)

	def getDistinctGenom(self):
		randIndex = randint(0, len(self.availableGenoms)-1)
		return self.genomes[self.availableGenoms.pop(randIndex)].copy()


class Member():
	def __init__(self, gameEntity):
		self.gameEntity = gameEntity
		self.relativeFitness = 0
		self.absoluteFitness = 0



