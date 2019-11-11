from HelperClasses import *
import pygame.math as gameMath
from Constants import *
from random import random

class Camera():
	def __init__(self, game, fps):
		self.game = game
		self.filter = Filter(150, 2, 1.3)
		# self.delay = 0.1 # in seconds
		self.frameRate = fps
		self.stepsSinceLastCapture = 0
		self.newData = False
		self.ballPosition = gameMath.Vector2(0, 0)
		self.positionHistory = []
		self.xGrid = []
		self.yGrid = []
		self.createGrid(35)

	def update(self):
		stepsToCapture = round((1/self.frameRate)/self.game.simulation.timeStep) 
		if self.stepsSinceLastCapture >= stepsToCapture:
			self.capture()
			self.game.redPlayer.strategy.newData = True
			self.game.bluePlayer.strategy.newData = True
			self.stepsSinceLastCapture = 0
			self.positionHistory.append(self.ballPosition)
			if(len(self.positionHistory) > 10):
				self.positionHistory.pop(0)

		self.stepsSinceLastCapture += 1

	def createGrid(self, step):
		self.xGrid.append(0)
		i = 0
		while self.xGrid[i] < self.game.field.width:
			self.xGrid.append(self.xGrid[i] + step)
			i += 1
		
		
		self.yGrid.append(-FIELD_HEIGHT/2)
		i = 0
		while (self.yGrid[i] < self.game.field.height/2):
			self.yGrid.append(self.yGrid[i] + step)
			i += 1

	def capture(self):
		self.ballPosition = gameMath.Vector2(self.game.ball.pos.copy())
		self.ballPosition.x += random()*5
		self.ballPosition.y += random()*5
		# for (let ax of self.game.redPlayer.axes) :
		# 	let dist = self.ballPosition.x - ax.absoluteX
		# 	if(abs(dist) < BALL_RADIUS*1.5):				
		# 		self.ballPosition.x = ax.absoluteX + Math.sign(dist) * BALL_RADIUS + 0.5*(dist)
		# 		break
						
		
		
		# for (let ax of self.game.bluePlayer.axes) :
		# 	let dist = self.ballPosition.x - ax.absoluteX
		# 	if(abs(dist) < BALL_RADIUS*1.5):				
		# 		self.ballPosition.x = ax.absoluteX + Math.sign(dist) * BALL_RADIUS + 0.5*(dist)
		# 		break
						
		

		tempPos = 0
		for element in self.xGrid:
			if (abs(self.ballPosition.x - element) < abs(self.ballPosition.x - tempPos)):
				tempPos = element
	
		self.ballPosition.x = tempPos

		tempPos = 0
		for element in self.yGrid:
			if (abs(self.ballPosition.y - element) < abs(self.ballPosition.y - tempPos)):
				tempPos = element
	
		self.ballPosition.y = tempPos
		self.ballPosition = self.filter.filterData(self.ballPosition)