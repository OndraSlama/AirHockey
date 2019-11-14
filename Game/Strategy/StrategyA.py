from Game.Strategy.BaseStrategy import BaseStrategy
from Game.Strategy.StrategyStructs import *
from pygame.math import Vector2
from Constants import *

# WAITING = 0
# DEFEND_GOAL_DEFAULT = 1
# DEFEND_Y = 2
# DEFEND_TRAJECTORY = 3


class StrategyA(BaseStrategy):
	def __init__(self):
		super().__init__()
		self.actionState = 0

	def process(self, stepTime):
		self.stepTick(stepTime)	 

		# if self.puck.position.x > FIELD_WIDTH/2 or self.puck.vector.x > 0:
		# 	self.striker.desiredPosition = Vector2(100, 0)
		# else:
		# 	self.striker.desiredPosition = Vector2(100, self.puck.position.y)

		# if not self.goalLineIntersection == -10000 and self.puck.state == ACURATE:
		# 	self.striker.desiredPosition = Vector2(STRIKER_RADIUS, self.goalLineIntersection)

		# if not self.isPuckDangerous():
		# 	# step = (self.puck.position - self.striker.position)
		# 	# step.scale_to_length(step.magnitude() + PUCK_RADIUS*2)
		# 	self.striker.desiredPosition = self.puck.position #self.striker.position + step


	def isPuckDangerous(self):
		if self.puck.position.x > FIELD_WIDTH/2:
			return True

		if abs(self.goalLineIntersection) < (GOAL_SPAN/2) * 1.2:
			return True

		if self.puck.speedMagnitude > 1000:
			return True

		return False
		
		

		