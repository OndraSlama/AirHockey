from Strategy.BaseStrategy import BaseStrategy
from Strategy.StrategyStructs import *
from pygame.math import Vector2
from numpy import sign
from Constants import *
from random import random
from Neuroevolution.NeuralNetwork import NeuralNetwork


class NN_StrategyA(BaseStrategy):
	def __init__(self):
		super().__init__()
		self.brain = NeuralNetwork(8, [6, 3], 2)

	def _process(self):  
		brainInput = self.normalizeInput()
		brainOutput = self.brain.forward(brainInput)
		# print(self.denormalizeOutput(brainOutput))
		# self.setDesiredPosition(self.denormalizeOutput(brainOutput))
		self.setDesiredVelocity(self.denormalizeOutput(brainOutput))

	def normalizeInput(self):
		return [self.puck.position.x/FIELD_WIDTH, 
				(self.puck.position.y + FIELD_HEIGHT/2)/FIELD_HEIGHT,
				self.puck.velocity.x/3000, 
				self.puck.velocity.y/3000,
				self.striker.position.x/(FIELD_WIDTH/2),
				(self.striker.position.y + FIELD_HEIGHT/2)/FIELD_HEIGHT,
				self.striker.velocity.x/self.maxSpeed, 
				self.striker.velocity.y/self.maxSpeed				
				]

	def denormalizeOutput(self, brainOutput):
		return Vector2((brainOutput[0]-0.5)*self.maxSpeed, (brainOutput[1]-0.5)*self.maxSpeed)
		# return Vector2(brainOutput[0]*FIELD_WIDTH/2, (brainOutput[1]*FIELD_HEIGHT) - FIELD_HEIGHT/2)
		