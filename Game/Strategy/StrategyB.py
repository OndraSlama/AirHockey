from Game.Strategy.BaseStrategy import BaseStrategy
from Game.Strategy.StrategyStructs import *
from pygame.math import Vector2
from numpy import sign
from Constants import *

class StrategyB(BaseStrategy):
	def __init__(self):
		super().__init__()
		self.actionState = 0
		self.lineToGoal = Line()
		

	def process(self, stepTime):
		self.stepTick(stepTime)	
		self.getPredictedPuckPosition(self.striker.desiredPosition)

		if self.isPuckBehingStriker():
			self.defendGoalLastLine()
		elif self.predictedPosition.x < STRIKER_AREA_WIDTH and not (self.bounces and self.puck.state == ACURATE):			
			self.setDesired(self.predictedPosition)
		elif self.shouldIntercept():
			self.defendTrajectory()
		else:
			self.defendGoalLastLine()

		self.limitMovement()

	def defendGoalDefault(self):
		if self.bounces and self.puck.state == ACURATE:
			fromPoint = self.puck.trajectory[-1].start
		else:
			fromPoint = self.puck.position

		a = Line(fromPoint, Vector2(0,0))
		b = Line(gameMath.Vector2(DEFENSE_LINE, 0), gameMath.Vector2(DEFENSE_LINE, FIELD_HEIGHT))
		desiredPosition = self.getIntersectPoint(a, b)
		if desiredPosition is not None:
			self.setDesired(Vector2(desiredPosition))

	def defendGoalLastLine(self):
		if not self.goalLineIntersection == -10000 and self.puck.state == ACURATE:
			self.setDesired(Vector2(STRIKER_RADIUS, self.goalLineIntersection))
		else:
			self.setDesired(Vector2(STRIKER_RADIUS, sign(self.puck.position.y) * min(GOAL_SPAN/2, abs(self.puck.position.y))))

	def defendTrajectory(self):
		if len(self.puck.trajectory) > 0:
			vector = Vector2(-self.puck.vector.y, self.puck.vector.x)
			secondPoint = self.striker.position + vector
			
			self.setDesired(self.getIntersectPoint(self.puck.trajectory[0], Line(self.striker.position, secondPoint)))

	def isPuckBehingStriker(self):
		return self.striker.position.x > self.puck.position.x - PUCK_RADIUS

	def shouldIntercept(self):
		if len(self.puck.trajectory) == 0:
			return 0
		return self.puck.state == ACURATE and (not self.bounces or (sign(self.puck.vector.y) * self.puck.trajectory[-1].end.y > GOAL_SPAN )) and self.puck.vector.x < 0

	def isPuckDangerous(self):
		if self.puck.position.x > FIELD_WIDTH/2:
			return True

		if self.bounces:
			return True

		if self.striker.position.x > self.puck.position.x - PUCK_RADIUS:
			return True

		if abs(self.goalLineIntersection) < (GOAL_SPAN/2) * 1.2 and self.puck.state == ACURATE:
			if len(self.puck.trajectory) > 0:
				if self.getPointLineDist(self.striker.position, self.puck.trajectory[-1]) > PUCK_RADIUS:
					return True
		return False

		
		

		