from Strategy.BaseStrategy import BaseStrategy
from Strategy.StrategyStructs import *
from pygame.math import Vector2
from numpy import sign
from Constants import *
from random import random

DEFEND = 0
WAITING = 0
ATTACK = 10
ATTACK_INIT = 11
ATTACK_PREPARE_POSITION = 12
ATTACK_SHOOT = 13
DEFEND = 20
STOP_PUCK = 30

class StrategyD(BaseStrategy):
	def __init__(self):
		super().__init__()
		self.actionState = 0
		self.lineToGoal = Line()
		self.state = DEFEND
		self.subState = DEFEND
		self.lastPuckStop = 0

	def process(self, stepTime):
		self.stepTick(stepTime)	 

		def case(state):
			return state == self.state

		def subCase(state):
			return state == self.subState
		
		if case(DEFEND):		

			if self.isPuckBehingStriker():
				self.defendGoalLastLine()
			elif self.canAttack():
				self.subState = WAITING
				if self.shouldStop():
					self.state = STOP_PUCK
				else:
					self.state = ATTACK				
			elif self.shouldIntercept():
				self.defendTrajectory()
			else:
				self.defendGoalDefault()

		elif case(ATTACK):

			if self.puck.velocity.x > MAX_SPEED*0.7 or self.getPredictedPuckPosition(self.puck.position).x > STRIKER_AREA_WIDTH:
				self.subState = WAITING
				self.state = DEFEND

			self.getPredictedPuckPosition(self.puck.position)
			if subCase(WAITING):
				self.lineToGoal = Line(self.predictedPosition, Vector2(FIELD_WIDTH*1.2, 0))

				if abs(self.goalLineIntersection) < GOAL_SPAN/2 and self.puck.state == ACURATE or self.puck.speedMagnitude > 200:
					self.subState = ATTACK_SHOOT
				else:
					self.subState = ATTACK_INIT
			
			elif subCase(ATTACK_INIT):
				# wait a bit for decision
				if self.gameTime > self.lastPuckStop + 0.1:
					randomNum = random()
					chosen = False

					if not self.puck.state == ACURATE and self.puck.speedMagnitude < 20: # try wall bounce only if puck is almost still
						topBounce = Line(self.predictedPosition, Vector2(FIELD_WIDTH*0.9, FIELD_HEIGHT))
						vectorFromGoal = topBounce.start - topBounce.end
						vectorFromGoal.scale_to_length(STRIKER_RADIUS*6)
						if not self.striker.position.y < -FIELD_HEIGHT*0.3 and randomNum < 0.4:
							self.lineToGoal = topBounce
							finalVector = vectorFromGoal
							chosen = True
						bottomBounce = Line(self.predictedPosition, Vector2(FIELD_WIDTH*0.9, FIELD_HEIGHT))
						vectorFromGoal = bottomBounce.start - bottomBounce.end
						vectorFromGoal.scale_to_length(STRIKER_RADIUS*6)			
						if not self.striker.position.y > FIELD_HEIGHT*0.3 - STRIKER_RADIUS*4 and randomNum > 0.6:
							self.lineToGoal = bottomBounce
							finalVector = vectorFromGoal
							chosen = True

					if not chosen:
						center = Line(self.predictedPosition, Vector2(FIELD_WIDTH*1.15, 0))
						vectorFromGoal = center.start - center.end
						vectorFromGoal.scale_to_length(STRIKER_RADIUS*6)		
						finalVector = vectorFromGoal	
						self.lineToGoal = center
						# print("center")

					self.setDesiredPosition(self.predictedPosition + finalVector)
					self.subState = ATTACK_PREPARE_POSITION

			elif subCase(ATTACK_PREPARE_POSITION):
				if self.striker.position.distance_squared_to(self.striker.desiredPosition) < CLOSE_DISTANCE**2 or self.isPuckDangerous() or self.isInGoodPosition(self.lineToGoal):
					self.subState = ATTACK_SHOOT

			elif subCase(ATTACK_SHOOT):

				# Accurate shot
				if len(self.puck.trajectory) > 0 and self.getPointLineDist(self.striker.position, self.puck.trajectory[0]) < STRIKER_RADIUS/4 or self.puck.speedMagnitude < 100:
					
					# A bit of aiming
					vectorToGoal = self.lineToGoal.end - self.lineToGoal.start
					step = (self.puck.position - self.striker.position)
					step.scale_to_length(PUCK_RADIUS*3)
					angleDiff = self.getAngleDifference(vectorToGoal, step)
					step = step.rotate(angleDiff)
					stepFromStriker = (self.puck.position - self.striker.position) + step

					if abs(self.puck.position.y) > FIELD_HEIGHT/2 - STRIKER_RADIUS*2 and self.puck.position.x > STRIKER_RADIUS*2:	
						self.setDesiredPosition(self.striker.position + stepFromStriker)
					else:
						self.clampDesired(self.striker.position, stepFromStriker)
				
				# Inaccurate shot
				else:
					perpendicularPoint = self.getPerpendicularPoint(self.striker.position, self.puck.trajectory[0])
					self.getPredictedPuckPosition(perpendicularPoint, 0.8)
					if perpendicularPoint.x < self.predictedPosition.x:
						step = (self.predictedPosition - self.striker.position)
						step.scale_to_length(PUCK_RADIUS*3)
						self.clampDesired(self.predictedPosition, step)
					else:
						self.getPredictedPuckPosition(self.puck.position)
						step = (self.predictedPosition - self.striker.position)
						step.scale_to_length(PUCK_RADIUS*3)
						self.clampDesired(self.predictedPosition, step)

				if self.isPuckBehingStriker() or (self.badAttackingAngle(self.striker.desiredPosition) and abs(self.puck.position.y) < FIELD_HEIGHT/2 - STRIKER_RADIUS*2 and self.puck.position.x > STRIKER_RADIUS*2):
					self.defendTrajectory()
					self.subState = WAITING
					self.state = DEFEND

			else: 
				self.subState = WAITING

		elif case(STOP_PUCK):
			self.slowDownPuck()
			if self.puck.speedMagnitude < 100 or self.isPuckDangerous() or (self.puck.state == ACURATE and self.puck.vector.x > 0):
				self.state = ATTACK
				self.lastPuckStop = self.gameTime
		else:
			pass


	# Other functions
	def defendGoalDefault(self):
		if self.bounces and self.puck.state == ACURATE and self.puck.vector.x < 0:
			fromPoint = self.puck.trajectory[-1].start
			# offset = (min(fromPoint.x, FIELD_WIDTH/2) - DEFENSE_LINE)/3
		else:
			fromPoint = self.puck.position
			# offset = (fromPoint.x - DEFENSE_LINE)/10


		a = Line(fromPoint, Vector2(0,0))
		b = Line(Vector2(DEFENSE_LINE, 0), Vector2(DEFENSE_LINE, FIELD_HEIGHT))
		desiredPosition = self.getIntersectPoint(a, b)
		if desiredPosition is not None:
			self.setDesiredPosition(Vector2(desiredPosition))

	def defendGoalLastLine(self):
		if not self.goalLineIntersection == -10000 and self.puck.state == ACURATE:
			self.setDesiredPosition(Vector2(STRIKER_RADIUS, self.goalLineIntersection))
		else:
			self.setDesiredPosition(Vector2(STRIKER_RADIUS, sign(self.puck.position.y) * min(GOAL_SPAN/2, abs(self.puck.position.y))))

	def defendTrajectory(self):		

		if len(self.puck.trajectory) > 0:
			desiredPos = self.getPerpendicularPoint(self.striker.position, self.puck.trajectory[0])
			isLate = False
			if self.getPredictedPuckPosition(desiredPos, 1.5).x < desiredPos.x:
				desiredPos = self.predictedPosition
				isLate = True
			else:
				desiredPos = self.getBothCoordinates(self.puck.trajectory[0], x = min(self.predictedPosition.x, STOPPING_LINE))

			if abs(desiredPos.y) > FIELD_HEIGHT/2 - PUCK_RADIUS:
				if isLate:
					self.defendGoalDefault()
				else:
					self.setDesiredPosition(self.puck.trajectory[0].end)
			else:
				if desiredPos.x > FIELD_WIDTH/4:
					desiredPos = self.getBothCoordinates(self.puck.trajectory[0], x = FIELD_WIDTH/4)
				self.setDesiredPosition(desiredPos)

	def slowDownPuck(self):
		if len(self.puck.trajectory) > 0:
			desiredPos = self.getPerpendicularPoint(self.striker.position, self.puck.trajectory[0])
			if self.getPredictedPuckPosition(desiredPos, 1.5).x > desiredPos.x:				
				desiredPos = self.getBothCoordinates(self.puck.trajectory[0], x = max(DEFENSE_LINE * 2, min(DEFENSE_LINE * 2 + (self.predictedPosition.x - desiredPos.x)/2, STOPPING_LINE)))
		self.setDesiredPosition(desiredPos)

	def isPuckBehingStriker(self):
		return self.striker.position.x > self.puck.position.x - PUCK_RADIUS

	def shouldIntercept(self):
		if len(self.puck.trajectory) == 0:
			return 0
		return self.puck.state == ACURATE and (not self.bounces or self.puck.trajectory[-1].start.x < STRIKER_AREA_WIDTH - STRIKER_RADIUS*3 ) and self.puck.vector.x < 0

	def isPuckDangerous(self):
		if self.puck.position.x > FIELD_WIDTH/2:
			return True

		if self.bounces and self.puck.state == ACURATE and self.puck.vector.x < 0:
			if len(self.puck.trajectory) > 0:
				if self.getPointLineDist(self.striker.position, self.puck.trajectory[0]) > PUCK_RADIUS:
					perpendicularPoint = self.getPerpendicularPoint(self.striker.position, self.puck.trajectory[0])				
					if perpendicularPoint.x > self.getPredictedPuckPosition(perpendicularPoint).x:
						return True

		if self.striker.position.x > self.puck.position.x - PUCK_RADIUS:
			return True

		if abs(self.goalLineIntersection) < (GOAL_SPAN/2) * 1.2 and self.puck.state == ACURATE:
			if len(self.puck.trajectory) > 0:
				if self.getPointLineDist(self.striker.position, self.puck.trajectory[-1]) > PUCK_RADIUS:
					return True
		return False

	def isInGoodPosition(self, lineToGoal):
		return self.getPointLineDist(self.striker.position, lineToGoal) < CLOSE_DISTANCE and self.striker.position.distance_squared_to(self.puck.position) > (STRIKER_RADIUS*3)**2

	def badAttackingAngle(self, pos):
		radius, attackAngle = (pos - self.striker.position).as_polar()
		return abs(attackAngle) > 65

	def canAttack(self):		
		return not self.isPuckDangerous() and not self.isPuckOutsideLimits(self.getPredictedPuckPosition(self.puck.position))

	def shouldStop(self):
		desiredPos = self.getPerpendicularPoint(self.striker.position, self.puck.trajectory[0])
		if self.puck.vector.y > 2 and random() < 0.7:
			return True
		elif self.getPredictedPuckPosition(desiredPos, 2).x < desiredPos.x:
			if random() < 0.6:
				return True
		elif random() < 0.3:
			return True
		return False		

	def moveToByPortion(self, toPos, portion=0.5):
		stepVector = toPos - self.striker.desiredPosition
		self.setDesiredPosition(self.striker.desiredPosition + stepVector * portion)

		
		

		