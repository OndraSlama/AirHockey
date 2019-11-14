from Game.HelperClasses import Filter
import pygame.math as gameMath
from Constants import *
from random import gauss
from numpy import sign

class Camera():
	def __init__(self, game, fps):
		self.game = game
		self.filter = Filter(15, 3, 1.4)
		self.delay = 0.02 # in seconds - will not be precise
		self.frameRate = fps
		self.stepsSinceLastCapture = 0
		self.newData = False
		self.puckPosition = gameMath.Vector2(0, 0)
		self.positionHistory = []
		self.xGrid = []
		self.yGrid = []
		self.createGrid(4)

		self.historySize = max(round(self.delay/(1/self.frameRate)),1)

	def update(self):
		stepsToCapture = round((1/self.frameRate)/self.game.simulation.stepTime) 
		if self.stepsSinceLastCapture >= stepsToCapture:

			self.positionHistory.insert(0,self.capturePuck())
			if(len(self.positionHistory) > self.historySize):
				self.positionHistory.pop(-1)

			self.puckPosition = self.positionHistory[-1]
			self.newData = True
			self.stepsSinceLastCapture = 0
		self.stepsSinceLastCapture += 1

	def createGrid(self, step):
		self.xGrid.append(0)
		i = 0
		while self.xGrid[i] < FIELD_WIDTH:
			self.xGrid.append(self.xGrid[i] + step)
			i += 1
		
		
		self.yGrid.append(-FIELD_HEIGHT/2)
		i = 0
		while (self.yGrid[i] < FIELD_HEIGHT/2):
			self.yGrid.append(self.yGrid[i] + step)
			i += 1

	def capturePuck(self):
		self.puckPosition = gameMath.Vector2(self.game.simulation.puck.position)
		self.puckPosition.x += gauss(0, 2)
		self.puckPosition.y += gauss(0, 2)

		self.blockView()
		self.discretize()	

		self.puckPosition = self.filter.filterData(self.puckPosition)
		return self.puckPosition

	def discretize(self):
		tempPos = 0
		for element in self.xGrid:
			if (abs(self.puckPosition.x - element) < abs(self.puckPosition.x - tempPos)):
				tempPos = element	
		self.puckPosition.x = tempPos

		tempPos = 0
		for element in self.yGrid:
			if (abs(self.puckPosition.y - element) < abs(self.puckPosition.y - tempPos)):
				tempPos = element
		self.puckPosition.y = tempPos

	def blockView(self):
		for striker in self.game.simulation.strikers:
			dist = self.puckPosition.x - striker.position.x
			if(abs(dist) < PUCK_RADIUS*1.5):				
				self.puckPosition.x = striker.position.x + sign(dist) * PUCK_RADIUS + 0.5*(dist)
				break
		