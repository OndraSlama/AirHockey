from Game.Strategy.BaseStrategy import BaseStrategy
from Game.Strategy.StrategyStructs import *
from pygame.math import Vector2
from numpy import sign
from Constants import *

DEFEND = 0
WAITING = 0
ATTACK = 10
ATTACK_INIT = 11
ATTACK_SHOOT = 12
DEFEND = 20


class StrategyA(BaseStrategy):
	def __init__(self):
		super().__init__()
		self.actionState = 0
		self.lineToGoal = Line()
		self.state = DEFEND
		self.subState = DEFEND

	def process(self, stepTime):
		self.stepTick(stepTime)	 

		def case(state):
			return state == self.state

		def subCase(state):
			return state == self.subState
		
		if case(DEFEND):

			if self.isPuckBehingStriker():
				self.defendGoalLastLine()
			elif not self.isPuckDangerous() and self.puck.position.x < STRIKER_AREA_WIDTH:
				self.subState = WAITING
				self.state = ATTACK				
			elif self.shouldIntercept():
				self.defendTrajectory()
			else:
				self.defendGoalDefault()

		elif case(ATTACK):

			if self.puck.velocity.x > MAX_SPEED*0.7 or self.puck.position.x > STRIKER_AREA_WIDTH:
				self.subState = WAITING
				self.state = DEFEND

			if subCase(WAITING):
				if abs(self.goalLineIntersection) < GOAL_SPAN/2 and self.puck.state == ACURATE or self.puck.speedMagnitude > 200:
					self.subState = ATTACK_SHOOT
				else:
					self.subState = ATTACK_INIT
			
			elif subCase(ATTACK_INIT):
				self.lineToGoal = Line(self.puck.position, Vector2(FIELD_WIDTH*1, 0))
				vectorFromGoal = self.lineToGoal.start - self.lineToGoal.end
				vectorFromGoal.scale_to_length(STRIKER_RADIUS*4)
				self.setDesired(self.puck.position + vectorFromGoal)

				if self.striker.position.distance_squared_to(self.striker.desiredPosition) < CLOSE_DISTANCE**2 or self.isPuckDangerous():
					self.subState = ATTACK_SHOOT

			elif subCase(ATTACK_SHOOT):
				step = (self.puck.position - self.striker.position)
				step.scale_to_length(PUCK_RADIUS*3)
				self.setDesired(self.puck.position + step)

				if self.isPuckBehingStriker():
					self.subState = WAITING
					self.state = DEFEND

			else: 
				self.subState = WAITING

		else:
			pass

		self.limitMovement()

	def defendGoalDefault(self):
		if self.bounces and self.puck.state == ACURATE:
			fromPoint = self.puck.trajectory[-1].start
		else:
			fromPoint = self.puck.position

		a = Line(fromPoint, Vector2(0,0))
		b = Line(Vector2(DEFENSE_LINE, 0), Vector2(DEFENSE_LINE, FIELD_HEIGHT))
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

		
		

		