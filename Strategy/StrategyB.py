from Strategy.BaseStrategy import BaseStrategy
from Strategy.StrategyStructs import *
from UniTools import Line
from pygame.math import Vector2
from numpy import sign
from Constants import *

class StrategyB(BaseStrategy):
	def __init__(self):
		super().__init__()
		self.description = "Basic game mechanics. Uses puck position prediction."
		self.actionState = 0
		self.lineToGoal = Line()
		

	def _process(self):
		self.getPredictedPuckPosition(self.striker.desiredPosition)

		if self.isPuckBehingStriker():
			self.defendGoalLastLine()
		elif self.predictedPosition.x < STRIKER_AREA_WIDTH and not (self.willBounce and self.puck.state == ACURATE):			
			self.setDesiredPosition(self.predictedPosition)
		elif self.shouldIntercept():
			self.defendTrajectory()
		else:
			self.defendGoalLastLine()

		# 'Always' fucntions
		pos = self.getPredictedPuckPosition(self.striker.desiredPosition, 1)
		if self.isPuckBehingStriker(pos) and self.puck.speedMagnitude > 100:			
			self.defendGoalLastLine()

		self.moveIfStuck()

		self.limitMovement()


		
		

		