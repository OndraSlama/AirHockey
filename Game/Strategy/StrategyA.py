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
		self.lineToGoal = Line()

	def process(self, stepTime):
		self.stepTick(stepTime)	 
	
		if not self.isPuckDangerous() and self.puck.position.x < STRIKER_AREA_WIDTH - STRIKER_RADIUS:
			self.attack()
		else:
			self.defendGoalDefault()

		# if self.puck.position.x > FIELD_WIDTH/2 or self.puck.vector.x > 0:
		# 	self.defendGoalDefault()
		# else:
		# 	self.striker.desiredPosition = Vector2(100, self.puck.position.y)
		# 	pass

		# if not abs(self.goalLineIntersection) < GOAL_SPAN/2 and self.puck.state == ACURATE:
		# 	self.defendGoalLastLine()

		# if not self.isPuckDangerous():
		# 	pass
			# step = (self.puck.position - self.striker.position)
			# step.scale_to_length(step.magnitude() + PUCK_RADIUS*2)
			# self.striker.desiredPosition = self.puck.position #self.striker.position + step

	def defendGoalDefault(self):
		a = Line(self.puck.position, Vector2(0,0))
		b = Line(gameMath.Vector2(DEFENSE_LINE, 0), gameMath.Vector2(DEFENSE_LINE, FIELD_HEIGHT))
		desiredPosition = self.getIntersectPoint(a, b)
		if desiredPosition is not None:
			self.striker.desiredPosition = Vector2(desiredPosition)

	def defendGoalLastLine(self):
		self.striker.desiredPosition = Vector2(STRIKER_RADIUS, self.goalLineIntersection)

	def attack(self):
		self.lineToGoal = Line(self.puck.position, Vector2(FIELD_WIDTH*1, 0))
		vectorFromGoal = self.lineToGoal.start - self.lineToGoal.end
		vectorFromGoal.scale_to_length(STRIKER_RADIUS*4)
		self.striker.desiredPosition = self.puck.position + vectorFromGoal
		# print(self.getPointLineDist(self.striker.position, self.lineToGoal))
		if self.getPointLineDist(self.striker.position, self.lineToGoal) < PUCK_RADIUS/3:
			step = (self.puck.position - self.striker.position)
			step.scale_to_length(PUCK_RADIUS*3)
			self.striker.desiredPosition = self.puck.position + step

	def isPuckDangerous(self):
		if self.puck.position.x > FIELD_WIDTH/2:
			return True

		if abs(self.goalLineIntersection) < (GOAL_SPAN/2) * 1.2 and self.puck.state == ACURATE:
			return True

		if self.puck.speedMagnitude > 1000:
			return True

		return False
		
		

		