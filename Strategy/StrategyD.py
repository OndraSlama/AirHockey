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
ATTACK_STAND_BEHIND = 14
DEFEND = 20
STOP_PUCK = 30

class StrategyD(BaseStrategy):
	def __init__(self):
		super().__init__()
		self.description = "Advanced game mechanics with puck prediction and advanced aiming algoritms."
		self.actionState = 0
		self.lineToGoal = Line()
		self.state = DEFEND
		self.subState = DEFEND
		self.lastPuckStop = 0

	def _process(self):

		def case(state):
			return state == self.state

		def subCase(state):
			return state == self.subState
		
		if case(DEFEND):
			# 3 Main decisions		
			self.debugString = "Deffending"
			if self.isPuckBehingStriker(): # IF puck is behing striker
				self.defendGoalLastLine()
			elif self.canAttack(): # If striker can attack
				self.subState = WAITING
				if self.shouldStop():
					self.state = STOP_PUCK
				else:
					self.state = ATTACK				
			elif self.shouldIntercept(): # If it is good idea to try to intercept current trajectory of the puck 
				self.defendTrajectory()
			else:
				self.defendGoalDefault() 

		elif case(ATTACK):
			if self.puck.velocity.x > self.maxSpeed*0.7 or self.getPredictedPuckPosition(self.puck.position).x > STRIKER_AREA_WIDTH:
				self.subState = WAITING
				self.state = DEFEND
						

			self.getPredictedPuckPosition(self.puck.position)
			if subCase(WAITING):
				self.debugString = "Attacking"
				self.lineToGoal = Line(self.predictedPosition, Vector2(FIELD_WIDTH*1.2, 0))
				
				if self.puck.vector.x > 0:
					self.subState = ATTACK_STAND_BEHIND

				elif abs(self.goalLineIntersection) < GOAL_SPAN/2 and self.puck.state == ACURATE or self.puck.speedMagnitude > 200:

					self.subState = ATTACK_SHOOT
					self.debugString = "Attacking: Without init"
				else:
					if self.puck.speedMagnitude < 100:
						self.lastPuckStop = self.gameTime
					self.subState = ATTACK_INIT
				
			elif subCase(ATTACK_STAND_BEHIND):
				self.debugString = "Attacking: Standing behind puck"
				if self.puck.state == ACURATE:
					desiredY = self.getPredictedPuckPosition(self.puck.position, 1).y
					maxPos = FIELD_HEIGHT/2 - PUCK_RADIUS
					if abs(desiredY) > maxPos:
						desiredY = sign(desiredY) * (maxPos - (abs(desiredY) - maxPos))
					self.setDesiredPosition(Vector2(self.puck.position.x - 4*STRIKER_RADIUS, desiredY))

				if self.puck.speedMagnitude < 30 or self.puck.state == ACURATE and abs(self.puck.velocity.y) < self.maxSpeed*.8:
					self.subState = ATTACK_SHOOT
			
			elif subCase(ATTACK_INIT):
				# wait a bit for decision
				if self.gameTime > self.lastPuckStop + 0.15:
					randomNum = random()
					chosen = False

					if not self.puck.state == ACURATE and self.puck.speedMagnitude < 30: # try wall bounce only if puck is almost still
						topBounce = Line(self.predictedPosition, Vector2(FIELD_WIDTH*0.9, FIELD_HEIGHT))
						vectorFromGoal = topBounce.start - topBounce.end
						vectorFromGoal.scale_to_length(STRIKER_RADIUS*6)
						if self.puck.position.y > YLIMIT - STRIKER_RADIUS*2 or (not self.striker.position.y < -FIELD_HEIGHT*0.3 and randomNum < 0.4):
							self.debugString = "Attacking: Top bounce"

							self.lineToGoal = topBounce
							finalVector = vectorFromGoal
							chosen = True
						bottomBounce = Line(self.predictedPosition, Vector2(FIELD_WIDTH*0.9, FIELD_HEIGHT))
						vectorFromGoal = bottomBounce.start - bottomBounce.end
						vectorFromGoal.scale_to_length(STRIKER_RADIUS*6)			
						if self.puck.position.y < -YLIMIT + STRIKER_RADIUS*2 or (not self.striker.position.y > FIELD_HEIGHT*0.3 - STRIKER_RADIUS*4 and randomNum > 0.6):
							self.debugString = "Attacking: Bottom bounce"
							self.lineToGoal = bottomBounce
							finalVector = vectorFromGoal
							chosen = True

					if not chosen:
						self.debugString = "Attacking: Straight shot"
						center = Line(self.predictedPosition, Vector2(FIELD_WIDTH*1.15, 0))
						vectorFromGoal = center.start - center.end
						vectorFromGoal.scale_to_length(STRIKER_RADIUS*6)		
						finalVector = vectorFromGoal	
						self.lineToGoal = center
						# print("center")

					self.setDesiredPosition(self.predictedPosition + finalVector)
					self.subState = ATTACK_PREPARE_POSITION
			

			elif subCase(ATTACK_PREPARE_POSITION):
				self.debugString = "Attacking: Preparing position"
				if self.striker.position.distance_squared_to(self.striker.desiredPosition) < CLOSE_DISTANCE**2 or self.isPuckDangerous() or self.isInGoodPosition(self.lineToGoal) or self.puck.speedMagnitude > 100:
					self.subState = ATTACK_SHOOT

			elif subCase(ATTACK_SHOOT):

				stepToPuck = (self.puck.position - self.striker.position)
				# Accurate shot
				if len(self.puck.trajectory) > 0 and self.getPointLineDist(self.striker.position, self.puck.trajectory[0]) < STRIKER_RADIUS/3 or (stepToPuck.magnitude() < 3*STRIKER_RADIUS and self.puck.vector.x < -.7) or self.puck.speedMagnitude < 100:
					
					# A bit of aiming
					# self.debugString += " - Acurate shot (aimming)"

					vectorToGoal = self.lineToGoal.end - self.lineToGoal.start
					step = (self.puck.position - self.striker.position)
					step.scale_to_length(PUCK_RADIUS*3)
					angleDiff = self.getAngleDifference(vectorToGoal, step)
					step = step.rotate(angleDiff)
					stepFromStriker = (self.puck.position - self.striker.position) + step

					if abs(self.puck.position.y) > YLIMIT - STRIKER_RADIUS: # and self.puck.position.x > XLIMIT + STRIKER_RADIUS:	
						self.setDesiredPosition(self.striker.position + stepFromStriker)
					else:
						self.clampDesired(self.striker.position, stepFromStriker)
				
				# Inaccurate shot
				else:
					# self.debugString = " - Inaccurate shot (aimming)"
					perpendicularPoint = self.getPerpendicularPoint(self.striker.position, self.puck.trajectory[0])
					self.getPredictedPuckPosition(perpendicularPoint, 0.8)
					if perpendicularPoint.x < self.predictedPosition.x and self.puck.vector.x < 0:
						step = (self.predictedPosition - self.striker.position)
					elif self.puck.vector.x > 0:
						self.getPredictedPuckPosition(self.puck.position, 0.8)
						step = (self.predictedPosition - self.striker.position)
					else:
						self.getPredictedPuckPosition(self.puck.position)
						step = (self.predictedPosition - self.striker.position)

					step.scale_to_length(PUCK_RADIUS*3)
					self.clampDesired(self.predictedPosition, step)

				if self.isPuckBehingStriker() or (self.badAttackingAngle(self.striker.desiredPosition) and abs(self.puck.position.y) < YLIMIT - STRIKER_RADIUS and self.puck.position.x > XLIMIT + STRIKER_RADIUS and self.puck.vector.x < 0) or abs(self.puck.velocity.y) > self.maxSpeed*.8:					
					if self.shouldIntercept():
						self.defendTrajectory()
					else:
						self.defendGoalDefault()
					self.subState = WAITING
					self.state = DEFEND

			else: 
				self.subState = WAITING
			self.debugLines.append(self.lineToGoal)
		elif case(STOP_PUCK):
			self.slowDownPuck()
			if self.striker.desiredPosition.x > self.puck.position.x:
				self.defendGoalDefault()
				self.subState = WAITING
				self.state = DEFEND

			if self.puck.speedMagnitude < 100 or self.isPuckDangerous() or (self.puck.state == ACURATE and self.puck.vector.x > 0):
				self.subState = WAITING
				self.state = ATTACK				
		else:			
			pass
		
		# 'Always' fucntions
		pos = self.getPredictedPuckPosition(self.striker.desiredPosition, 1)
		if self.isPuckBehingStriker(pos) and self.puck.speedMagnitude > 100 and self.state == DEFEND:			
			self.defendGoalLastLine()
			self.subState = WAITING
			self.state = DEFEND

		self.moveIfStuck()

		

	# Other functions

	def defendTrajectory(self):	
		if len(self.puck.trajectory) > 0:
			desiredPos = self.getPerpendicularPoint(self.striker.position, self.puck.trajectory[0])			

			isLate = False
			if self.getPredictedPuckPosition(desiredPos, 1.5).x < desiredPos.x: # If puck cant make it to interception point
				desiredPos = self.predictedPosition # Try to intercept at the predicted position
				isLate = True
			else:
				
				desiredPos = self.getBothCoordinates(self.puck.trajectory[0], x = min(self.predictedPosition.x, STOPPING_LINE)) # Limit striker not to try to block at its movement limits

			if abs(desiredPos.y) > FIELD_HEIGHT/2 - PUCK_RADIUS:
				if isLate:
					self.defendGoalDefault()
				else:
					if self.puck.trajectory[0].end.x > STRIKER_AREA_WIDTH - STRIKER_RADIUS*2:
						self.setDesiredPosition(self.getPerpendicularPoint(self.striker.position, self.puck.trajectory[-1]))
					else:
						self.setDesiredPosition(self.puck.trajectory[0].end)
			else:
				if desiredPos.x > FIELD_WIDTH/4:
					desiredPos = self.getBothCoordinates(self.puck.trajectory[0], x = FIELD_WIDTH/4)
				self.setDesiredPosition(desiredPos)

			self.debugString = "strategyD.defendTrajectory"

			# self.debugLines.append(self.puck.trajectory[0])
			# self.debugLines.append(Line(self.striker.position, secondPoint))

	def slowDownPuck(self):
		self.debugString = "strategyD.slowDownPuck"
		if len(self.puck.trajectory) > 0:
			desiredPos = self.getPerpendicularPoint(self.striker.position, self.puck.trajectory[0])			
			if self.getPredictedPuckPosition(desiredPos, 1).x > desiredPos.x:				
				desiredPos = self.getBothCoordinates(self.puck.trajectory[0], x = max(DEFENSE_LINE, min(DEFENSE_LINE + (self.predictedPosition.x - desiredPos.x)*1, STOPPING_LINE)))
		self.setDesiredPosition(desiredPos)

	def shouldIntercept(self):
		if len(self.puck.trajectory) == 0 or (self.puck.vector.x > -0.7):
			return False
		if self.puck.position.x > FIELD_WIDTH/2 and self.puck.speedMagnitude < 800: # If puck is at the other side and is slow
			return False
		if self.puck.state == ACURATE and (not self.willBounce or self.puck.trajectory[-1].start.x < STRIKER_AREA_WIDTH - STRIKER_RADIUS*3 ) and self.puck.vector.x < 0: # Puck will not bounce or will bounce on robot side of the field (minus some distance) and is pointing towards robot
			return True
		else:
			if self.puck.state == ACURATE and self.puck.vector.x < 0 and sign(self.puck.position.y) == sign(self.puck.trajectory[-1].start.y) and abs(self.puck.trajectory[-1].end.y) > GOAL_SPAN/2: # If the bounce will occur at the same side as puck position and the rebaunce will end up oustisde of goal on the same side
				return True
			else:
				return False

	def isPuckDangerous(self):
		if self.puck.position.x > STRIKER_AREA_WIDTH and not (self.puck.state == ACURATE and abs(self.goalLineIntersection) < GOAL_SPAN/2):
			return True
		
		if abs(self.puck.velocity.y) > self.maxSpeed and self.puck.vector.x < 0:
			return True

		if self.willBounce and self.puck.state == ACURATE and self.puck.vector.x < 0: # If puck is pointing at robot side and is about to bounce from sidewalls
			if len(self.puck.trajectory) > 0:
				if self.getPointLineDist(self.striker.position, self.puck.trajectory[0]) > PUCK_RADIUS and self.getPointLineDist(self.striker.position, self.puck.trajectory[-1]) > PUCK_RADIUS :  # If striker is not in the way of trajectory
					perpendicularPoint = self.getPerpendicularPoint(self.striker.position, self.puck.trajectory[0])				
					if perpendicularPoint.x > self.getPredictedPuckPosition(perpendicularPoint).x and (self.puck.trajectory[0].end.x < STOPPING_LINE and .2 < sign(self.puck.vector.y) < .7 ): # If striker cant make it for block and  
						return True

		if self.striker.position.x > self.puck.position.x - PUCK_RADIUS: # If puck is alomst behind striker
			return True

		if abs(self.goalLineIntersection) < (GOAL_SPAN/2) * 1.2 and self.puck.state == ACURATE: # If puck is poiting to goal
			if len(self.puck.trajectory) > 0:
				if self.getPointLineDist(self.striker.position, self.puck.trajectory[-1]) > PUCK_RADIUS: # If striker is not in the way of trajectory
					return True
		return False

	def isInGoodPosition(self, lineToGoal):
		return self.getPointLineDist(self.striker.position, lineToGoal) < CLOSE_DISTANCE and self.striker.position.distance_squared_to(self.puck.position) > (STRIKER_RADIUS*3)**2

	def badAttackingAngle(self, pos):
		radius, attackAngle = (pos - self.striker.position).as_polar()
		return abs(attackAngle) > 65

	def canAttack(self):		
		# if self.puck.position.x
		return not self.isPuckDangerous() and (self.getPredictedPuckPosition(Vector2(STRIKER_AREA_WIDTH, self.striker.position.y), 1).x < STRIKER_AREA_WIDTH - STRIKER_RADIUS or self.puck.speedMagnitude < 100) and self.puck.velocity.x < self.maxSpeed*.6 # (not self.isPuckOutsideLimits(self.getPredictedPuckPosition(self.puck.position)) or self.puck.vector.x > 0) 

	def shouldStop(self):
		desiredPos = self.getPerpendicularPoint(self.striker.position, self.puck.trajectory[0])
		if desiredPos.x < XLIMIT + 2*STRIKER_RADIUS or abs(desiredPos.y) > YLIMIT - STRIKER_RADIUS: # If there is no place for te slowing down
			return False

		if not self.puck.state == ACURATE:
			return False 

		if self.puck.vector.x > - .65: # If puck trajectory is "steep" or faces other direction
			return False

		if .3 < abs(self.puck.vector.y) and random() < 0.7:
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

		
		

		