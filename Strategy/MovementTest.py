from Strategy.BaseStrategy import BaseStrategy
from Strategy.StrategyStructs import *
from UniTools import Line
from pygame.math import Vector2
from numpy import sign
from Constants import *

class MovementTest(BaseStrategy):
	def __init__(self):
		super().__init__()
		self.description = "Movement test"
		self.lastCommand = 0
		self.movementTime = 0

	def _process(self):
		self.movementTime += self.stepTime
		
		times = [0, 1.577, 3.235, 5.01, 7]
		positions = [[200, 0],
					[400, -200],
					[90,0],
					[400,43],
					[200, 0]]

		for i in range(len(times)):
			if self.movementTime > times[i]:
				self.setDesiredPosition(Vector2(positions[i][0], positions[i][1]))

		if self.movementTime > times[-1]:
			self.movementTime = 0 

		

	

		
		

		