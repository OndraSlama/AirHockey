# ****************************************************************************** #
# Author: Ondrej Slama
# -------------------

# Zdrojovy kod vytvoreny v ramci projektu robotickeho vzdusneho hokeje - diplomova prace
#  na VUT FSI ustavu automatizace a informatiky v Brne.

# Source code created as a part of robotic air hockey table project - Diploma thesis
# at BUT FME institute of automation and computer science.

# ****************************************************************************** #
from Strategy.BaseStrategy import BaseStrategy
from Strategy.StrategyStructs import *
from UniTools import Line
from pygame.math import Vector2
from numpy import sign
from Constants import *

DEFEND = 0
WAITING = 0
ATTACK = 10
ATTACK_INIT = 11
ATTACK_SHOOT = 12
DEFEND = 20

class StrategyC(BaseStrategy):
	def __init__(self):
		super().__init__()
		self.description = "Combination of A and B. Slightly advanced mechanics with puck prediction."
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
			elif self.canAttack():
				self.subState = WAITING
				self.state = ATTACK				
			elif self.shouldIntercept():
				self.defendTrajectory()
			else:
				self.defendGoalDefault()

		elif case(ATTACK):

			if self.puck.velocity.x > self.maxSpeed*0.7 or self.getPredictedPuckPosition(self.puck.position).x > STRIKER_AREA_WIDTH:
				self.subState = WAITING
				self.state = DEFEND

			self.getPredictedPuckPosition(self.puck.position)
			if subCase(WAITING):
				if abs(self.goalLineIntersection) < GOAL_SPAN/2 and self.puck.state == ACURATE or self.puck.speedMagnitude > 200:
					self.subState = ATTACK_SHOOT
				else:
					self.subState = ATTACK_INIT
			
			elif subCase(ATTACK_INIT):
				self.lineToGoal = Line(self.predictedPosition, Vector2(FIELD_WIDTH*1, 0))
				vectorFromGoal = self.lineToGoal.start - self.lineToGoal.end
				vectorFromGoal.scale_to_length(STRIKER_RADIUS*4)
				self.setDesiredPosition(self.predictedPosition + vectorFromGoal)

				if self.striker.position.distance_squared_to(self.striker.desiredPosition) < CLOSE_DISTANCE**2 or self.isPuckDangerous() or self.isInGoodPosition(self.lineToGoal):
					self.subState = ATTACK_SHOOT

			elif subCase(ATTACK_SHOOT):

				# Accurate shot
				if len(self.puck.trajectory) > 0 and self.puck.trajectory[0].getPointLineDist(self.striker.position) < STRIKER_RADIUS:
					step = (self.puck.position - self.striker.position)
					step.scale_to_length(PUCK_RADIUS*3)
					self.clampDesired(self.puck.position, step)

				
				# Inaccurate shot
				else:
					perpendicularPoint = self.puck.trajectory[0].getPerpendicularPoint(self.striker.position)
					self.getPredictedPuckPosition(perpendicularPoint)
					if perpendicularPoint.x < self.predictedPosition.x:
						step = (self.predictedPosition - self.striker.position)
						step.scale_to_length(PUCK_RADIUS*3)
						self.clampDesired(self.predictedPosition, step)
					else:
						self.getPredictedPuckPosition(self.puck.position)
						step = (self.predictedPosition - self.striker.position)
						step.scale_to_length(PUCK_RADIUS*3)
						self.clampDesired(self.predictedPosition, step)

				if self.isPuckBehingStriker() or self.badAttackingAngle(self.striker.desiredPosition):
					self.defendTrajectory()
					self.subState = WAITING
					self.state = DEFEND

			else: 
				self.subState = WAITING

		else:
			pass

		# 'Always' fucntions
		pos = self.getPredictedPuckPosition(self.striker.desiredPosition, 1)
		if self.isPuckBehingStriker(pos) and self.puck.speedMagnitude > 100 and self.state == DEFEND:			
			self.defendGoalLastLine()
			self.subState = WAITING
			self.state = DEFEND


	# Other functions

	def defendTrajectory(self):		

		if len(self.puck.trajectory) > 0:
			desiredPos = self.puck.trajectory[0].getPerpendicularPoint(self.striker.position)
			isLate = False
			if self.getPredictedPuckPosition(desiredPos, 1.5).x < desiredPos.x:
				desiredPos = self.predictedPosition
				isLate = True

			if abs(desiredPos.y) > FIELD_HEIGHT/2 - PUCK_RADIUS:
				if isLate:
					self.defendGoalDefault()
				else:
					self.setDesiredPosition(self.puck.trajectory[0].end)
			else:
				self.setDesiredPosition(desiredPos)

	def shouldIntercept(self):
		if len(self.puck.trajectory) == 0:
			return 0
		return self.puck.state == ACURATE and (not self.willBounce or self.puck.trajectory[-1].start.x < STRIKER_AREA_WIDTH - STRIKER_RADIUS*3 ) and self.puck.vector.x < 0

	def isPuckDangerous(self):
		if self.puck.position.x > FIELD_WIDTH/2:
			return True

		if self.willBounce and self.puck.state == ACURATE and self.puck.vector.x < 0:
			if len(self.puck.trajectory) > 0:
				if self.puck.trajectory[0].getPointLineDist(self.striker.position) > PUCK_RADIUS:
					perpendicularPoint = self.puck.trajectory[0].getPerpendicularPoint(self.striker.position)				
					if perpendicularPoint.x > self.getPredictedPuckPosition(perpendicularPoint).x:
						return True

		if self.striker.position.x > self.puck.position.x - PUCK_RADIUS:
			return True

		if abs(self.goalLineIntersection) < (GOAL_SPAN/2) * 1.2 and self.puck.state == ACURATE:
			if len(self.puck.trajectory) > 0:
				if self.puck.trajectory[-1].getPointLineDist(self.striker.position) > PUCK_RADIUS:
					return True
		return False

	def isInGoodPosition(self, lineToGoal):
		return lineToGoal.getPointLineDist(self.striker.position) < CLOSE_DISTANCE and self.striker.position.distance_squared_to(self.puck.position) > (STRIKER_RADIUS*3)**2

	def badAttackingAngle(self, pos):
		radius, attackAngle = (pos - self.striker.position).as_polar()
		return abs(attackAngle) > 50

	def canAttack(self):		
		return not self.isPuckDangerous() and not self.isOutsideLimits(self.getPredictedPuckPosition(self.puck.position))

	def moveToByPortion(self, toPos, portion=0.5):
		stepVector = toPos - self.striker.desiredPosition
		self.setDesiredPosition(self.striker.desiredPosition + stepVector * portion)

		
		

		