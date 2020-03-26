from Strategy.BaseStrategy import BaseStrategy
from Strategy.StrategyStructs import *
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
		self.description = "Slightly advanced game mechanics. No puck position prediction."
		self.actionState = 0
		self.lineToGoal = Line()
		self.state = DEFEND
		self.subState = DEFEND

	def _process(self):

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

			if self.puck.velocity.x > self.maxSpeed*0.7 or self.puck.position.x > STRIKER_AREA_WIDTH:
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
				self.setDesiredPosition(self.puck.position + vectorFromGoal)

				if self.striker.position.distance_squared_to(self.striker.desiredPosition) < CLOSE_DISTANCE**2 or self.isPuckDangerous():
					self.subState = ATTACK_SHOOT

			elif subCase(ATTACK_SHOOT):
				step = (self.puck.position - self.striker.position)
				step.scale_to_length(PUCK_RADIUS*3)
				self.setDesiredPosition(self.puck.position + step)

				if self.isPuckBehingStriker():
					self.subState = WAITING
					self.state = DEFEND

			else: 
				self.subState = WAITING

		else:
			pass

		self.moveIfStuck()

		self.limitMovement()

	

		
		

		