from Strategy.StrategyStructs import *
from UniTools import Filter, Line, oppositeSigns
from Constants import *
from numpy import sign
from pygame.math import Vector2
from Functions import *

class BaseStrategy():
	def __init__(self):
		self.description = "Strategy with no gameplay mechanics."
		# DEBUG
		self.debugLines = []
		self.debugPoints = []
		self.debugString = ""

		# Striker
		self.striker = StrategyStriker()
		self.opponentStriker = StrategyStriker()

		# Striker Limits
		self.maxSpeed = MAX_SPEED
		self.acceleration = MAX_ACCELERATION
		self.gain = KP_GAIN

		# Puck
		self.puck = StrategyPuck()
		self.puckHistory = []
		self.puckHistory.append(self.puck)
		self.lastMove = 0

		# Trajectory info
		self.goalLineIntersection = 0
		self.willBounce = False

		# Parameters
		self.historySize = 50
		self.noOfBounces = 1
		self.minSpeedLimit = 100
		self.highAngleTolerance = 50
		self.mediumAngleTolerance = 15
		self.lowAngleTolerance = 8
		self.positionTolerance = 100
		self.capturesWithBadLowAngle = 0
		self.capturesWithBadMediumAngle = 0

		# States
		self.stepTime = 0
		self.gameTime = 0
		self.timeSinceLastCameraInput = 0
		self.sameCameraInputsInRow = 0
		self.previousErrorSide = 0
		self.firstUsefull = 1
		self.predictedPosition = Vector2(0,0)

		# Filter
		self.angleFilter = Filter(15, 2, 1, isVector=False)

		# Init
		for i in range(self.historySize - 1):
			self.puckHistory.append(StrategyPuck())

	#  Main process function -----------------------------------------------------------------------------------
	def process(self, stepTime):
		# DEBUG
		self.debugLines = []	
		self.debugPoints = []
		# self.debugString = ""

		self.stepTick(stepTime)
		self._process()
		self.limitMovement()
		self.calculateDesiredVelocity()
		

	# Only this should be overwriten in inherited strategies 
	def _process(self):
		self.setDesiredPosition(self.striker.position) # Placeholder

		# Your strategy code
	
	# Puck position handlers ------------------------------------------------------------------

	def stepTick(self, stepTime):
		self.stepTime = stepTime
		self.gameTime += stepTime
		for puck in self.puckHistory:
			puck.timeSinceCaptured += stepTime

	def cameraInput(self, pos):
		if pos == self.puck.position: return
		self.initialCheck(pos)
		self.setPuck(pos)
		self.checkState()
		self.calculateTrajectory()	


	def initialCheck(self, pos):

		currentStepVector = pos - self.puck.position
		stepDistance = currentStepVector.magnitude()
		
		if self.puck.timeSinceCaptured == 0:
			stepSpeed = 0
		else:
			stepSpeed = stepDistance/self.puck.timeSinceCaptured

		errorAngle = self.getAngleDifference(currentStepVector, self.puck.velocity)

		# Low angle condition
		if abs(errorAngle) > self.lowAngleTolerance and sign(errorAngle) == self.previousErrorSide:
			self.capturesWithBadLowAngle += 1
			if(self.capturesWithBadLowAngle > 4):
				# print("Low Angle error")

				for i in range(4):
					self.puckHistory[self.firstUsefull].state = USELESS
					if self.firstUsefull > 1: self.firstUsefull -= 1
		else:
			self.capturesWithBadLowAngle = 0

		self.previousErrorSide = sign(errorAngle)

		if stepSpeed > 200 and stepDistance > 4 and abs(errorAngle):
			# Medium angle condition
			if abs(errorAngle) > self.mediumAngleTolerance and sign(errorAngle) == self.previousErrorSide:
				self.capturesWithBadMediumAngle += 1
				if(self.capturesWithBadMediumAngle > 3):
					# print("Low angle condition.. 4 states -> useless")
					self.capturesWithBadLowAngle = 0	
					self.capturesWithBadMediumAngle = 0
					# print("Medium Angle error")
					for i in range(3, len(self.puckHistory)):
						self.puckHistory[i].state = USELESS		

			else:
				self.capturesWithBadMediumAngle = 0

			# Debug
			# if len(self.puck.trajectory) > 0:
			# trajectoryLine = Line(self.puckHistory[self.firstUsefull].position, self.puck.position)
			# bounceLine = Line(Vector2(0, sign(pos.y) * (FIELD_HEIGHT/2 - PUCK_RADIUS)), Vector2(FIELD_WIDTH,  sign(pos.y) * (FIELD_HEIGHT/2 - PUCK_RADIUS)))
			# self.debugLines.append(trajectoryLine)
			# self.debugLines.append(bounceLine)
			# self.debugPoints.append(self.getIntersectPoint(trajectoryLine, bounceLine))

			# High angle condition
			if(abs(errorAngle) > self.highAngleTolerance) or (stepSpeed > 700 and stepDistance > 25 and abs(errorAngle) > self.highAngleTolerance * .4):
				self.capturesWithBadLowAngle = 0	
				self.capturesWithBadMediumAngle = 0	

				# print("Angle condition: " + str(errorAngle))
				if abs(pos.y) > max(200, FIELD_HEIGHT/2 - (stepDistance * abs(self.puck.vector.y) + PUCK_RADIUS)) and sign(currentStepVector.x) == sign(self.puck.velocity.x) and sign(self.puck.velocity.y) == sign(pos.y) and self.puck.state == ACURATE: # seems like bounce from sidewalls occured
					trajectoryLine = Line(self.puckHistory[self.firstUsefull].position, self.puck.position)
					bounceLine = Line(Vector2(0, sign(pos.y) * (FIELD_HEIGHT/2 - PUCK_RADIUS)), Vector2(FIELD_WIDTH,  sign(pos.y) * (FIELD_HEIGHT/2 - PUCK_RADIUS)))

					bouncePoint = trajectoryLine.getIntersectPoint(bounceLine)
					self.debugLines.append(trajectoryLine)
					self.debugLines.append(bounceLine)
					bouncePoint = trajectoryLine.getIntersectPoint(bounceLine)
					self.puck.position = bouncePoint
					# print(bouncePoint)
				for i in range(len(self.puckHistory)):
					self.puckHistory[i].state = USELESS

					# print("High Angle error: " + str(abs(errorAngle)))


		# Quick acceleration - does nothing for now
		# i = self.firstUsefull - 1
		# while self.puckHistory[firstUsefull].position.distance_squared_to(self.puckHistory[i].position) < positionTolerance**2:
		# 	if i <= 1: break
		# 	i -= 1
	
	def setStriker(self, pos, velocity = None):
		if velocity == None:
			step = pos - self.striker.position
			velocity = Vector2(step)
			stepMag = step.magnitude()
			if stepMag > 0.001:
				if self.stepTime == 0:
					velocity.scale_to_length(0)
				else:
					velocity.scale_to_length(stepMag / self.stepTime)

		self.striker.velocity = Vector2(velocity)
		self.striker.position = Vector2(pos)

	def setOpponentStriker(self, pos, velocity = None):
		if velocity == None:
			step = pos - self.opponentStriker.position
			velocity = Vector2(step)
			stepMag = step.magnitude()
			if stepMag > 0.001:
				if self.stepTime == 0:
					velocity.scale_to_length(0)
				else:
					velocity.scale_to_length(stepMag / self.stepTime)

		self.striker.velocity = Vector2(velocity)
		self.opponentStriker.position = Vector2(pos)
		
	def setPuck(self, pos):
		self.puck = StrategyPuck(ACURATE, pos)
		self.puckHistory.pop(-1)
		self.puckHistory.insert(0, self.puck)

		self.firstUsefull = len(self.puckHistory) - 1
		while(self.puckHistory[self.firstUsefull].state == USELESS):
			self.firstUsefull -= 1
			if self.firstUsefull == 1: break

		# print(self.firstUsefull)
		
		if not self.puckHistory[self.firstUsefull].timeSinceCaptured == 0:
			# if self.firstUsefull > 3:
			stepVector = pos - self.puckHistory[self.firstUsefull].position
			self.puck.velocity = stepVector / self.puckHistory[self.firstUsefull].timeSinceCaptured

			# Filter velocity and normal vector
			(r, fi) = self.puck.velocity.as_polar()
			fi = self.angleFilter.filterData(fi, cyclic=360)
			self.puck.velocity.from_polar((r, fi if fi <= 180 else fi - 360))
			# print("-----")
			# print(fi)
			# print(r)
			# self.puck.velocity = self.velocityFilter.filterData(self.puck.velocity)

			self.puck.vector = self.puck.velocity.normalize()
			self.puck.speedMagnitude = r
			self.puck.angle = fi if fi > 0 else 360 - abs(fi)
		# else:
			# 	self.puck.state = INACURATE

			self.puck.timeSinceCaptured = 0
	
	def checkState(self):
		# Check for inacurate
		if abs(self.puck.speedMagnitude < self.minSpeedLimit):
			self.puck.state = INACURATE

		# if abs(self.puck.vector.y) > 0.9:
		# 	self.puck.state = INACURATE

		if self.puck.speedMagnitude < self.minSpeedLimit * 5 and self.firstUsefull < min(3, round(self.historySize/20)):
			self.puck.state = INACURATE


	# Desired position / velocity modification -------------------------------------------------------------------

	def setDesiredPosition(self, pos):
		self.striker.desiredPosition = Vector2(pos)
		self.limitMovement()
		self.calculateDesiredVelocity()

	def setDesiredVelocity(self, vel):
		
		posNextStep = self.striker.position + vel * self.stepTime

		if posNextStep.x > STRIKER_AREA_WIDTH:
			vel.x = 0

		if abs(posNextStep.y) > YLIMIT:
			vel.y = 0

		if posNextStep.x < XLIMIT: 
			vel.x = 0

		self.striker.desiredVelocity = vel

	def clampDesired(self, fromPos, step):
		desiredPos = fromPos + step
		line = Line(fromPos, desiredPos)
		self.debugLines.append(line)
		if desiredPos.x > STRIKER_AREA_WIDTH:
			desiredPos = line.getBothCoordinates(x = STRIKER_AREA_WIDTH)

		if abs(desiredPos.y) > YLIMIT:
			desiredPos = line.getBothCoordinates(y = sign(desiredPos.y) * YLIMIT)

		if desiredPos.x < XLIMIT: 
			desiredPos = line.getBothCoordinates(x = XLIMIT)

		self.setDesiredPosition(desiredPos)


	def limitMovement(self):
		if self.striker.desiredPosition.x > STRIKER_AREA_WIDTH:
			self.striker.desiredPosition.x = STRIKER_AREA_WIDTH

		if abs(self.striker.desiredPosition.y) > YLIMIT:
			self.striker.desiredPosition.y = sign(self.striker.desiredPosition.y) * YLIMIT

		if self.striker.desiredPosition.x < XLIMIT: 
			self.striker.desiredPosition.x = XLIMIT

		# Check if near corner
		if self.striker.desiredPosition.x < XLIMIT + STRIKER_RADIUS:
			if abs(self.striker.desiredPosition.y) > FIELD_HEIGHT/2 - (STRIKER_RADIUS + PUCK_RADIUS*2):
				self.striker.desiredPosition.y = sign(self.striker.desiredPosition.y) * (FIELD_HEIGHT/2 - (STRIKER_RADIUS + PUCK_RADIUS*2))

	def calculateDesiredVelocity(self):
		# self.striker.desiredVelocity = self.gain*(self.striker.desiredPosition - self.striker.position)
		# speedDiff = abs(self.striker.velocity.x) - abs(self.striker.velocity.y)

		# maxSpeed = max(abs(self.striker.velocity.x), abs(self.striker.velocity.y), self.maxSpeed/10)
		# xmag = max(abs(self.striker.velocity.x),self.maxSpeed/10)/maxSpeed
		# ymag = max(abs(self.striker.velocity.y),self.maxSpeed/10)/maxSpeed
		
		# self.striker.desiredVelocity.x = xmag * self.gain*(self.striker.desiredPosition.x - self.striker.position.x)
		# self.striker.desiredVelocity.y = ymag * self.gain*(self.striker.desiredPosition.y - self.striker.position.y)

		self.striker.desiredVelocity.x = self.gain*(self.striker.desiredPosition.x - self.striker.position.x)
		self.striker.desiredVelocity.y = self.gain*(self.striker.desiredPosition.y - self.striker.position.y)
		
		# if oppositeSigns(self.striker.desiredVelocity.x, self.striker.velocity.x):
		# 	self.striker.desiredVelocity.x = 10 * self.gain*(self.striker.desiredPosition.x - self.striker.position.x)

		# if oppositeSigns(self.striker.desiredVelocity.y, self.striker.velocity.y):		
		# 	self.striker.desiredVelocity.y = 10 * self.gain*(self.striker.desiredPosition.y - self.striker.position.y)
	# Checkers ------------------------------------------------------------------------------

	def isOutsideLimits(self, pos):
		if pos.x > STRIKER_AREA_WIDTH: return True
		if abs(pos.y) > YLIMIT: return True
		if pos.x < XLIMIT: return True
		if pos.x > FIELD_WIDTH - XLIMIT: return True

		return False

	def isPuckOutsideLimits(self, pos):

		if pos.x > STRIKER_AREA_WIDTH: return True
		if abs(pos.y) > FIELD_HEIGHT/2 - PUCK_RADIUS*0.8: return True
		if pos.x < PUCK_RADIUS*0.8: return True
		if pos.x > FIELD_WIDTH - PUCK_RADIUS*0.8: return True

		return False

	def isPuckBehingStriker(self, pos = None):
		if pos is None: pos = self.puck.position
		return self.striker.position.x > pos.x - PUCK_RADIUS*2
	
			
	# Get functions --------------------------------------------------------------

	def getAngleDifference(self, vector1, vetor2):
		errorAngle = vector1.angle_to(vetor2)
		if abs(errorAngle) > 180: errorAngle -= sign(errorAngle) * 360
		return errorAngle

	def getPredictedPuckPosition(self, strikerPos = None, reserve=1.3):
		if strikerPos is None: strikerPos = self.striker.desiredPosition
		if self.puck.state == INACURATE:
			self.predictedPosition = Vector2(self.puck.position)
			return Vector2(self.puck.position)
		if len(self.puck.trajectory) > 0:
			try:
				step = strikerPos - self.striker.position
				dist = step.magnitude()

				# Compute time, that will take striker to move to desired position
				a = getValueInXYdir(step.x, step.y, self.acceleration).magnitude() # Acceleration in direction to desired pos
				vm = getValueInXYdir(step.x, step.y, self.maxSpeed).magnitude() # Max velocity in direction to desired pos
				v0 = sign(self.striker.velocity.dot(step)) * (step * self.striker.velocity.dot(step) / step.dot(step)).magnitude() # Projected current velocity in direction to desired pos 
																																	#(how fast the striker is moving in the right direction)
				
				t1 = (vm - v0)/a # Time it would take for striker to accelerate to max speed in the direction to desired pos
				d1 = 1/2 * a * t1**2 + v0*t1 # Distance the striker would cover in t1 time in direction to desiered pos
				if d1 > dist: # if the "would be" distance is greater than actual distance to desired pos then: 
					time = max((-v0 + (v0**2 + 2*a*dist)**.5)/a, (-v0 - (v0**2 + 2*a*dist)**.5)/a) # Calculate time to travel that distance with good old kinematic formula Δx=1/2at^2 + v0t
				else: # else:
					time = t1 + (dist - d1)/vm # Get the calculated t1 time and add time calculated as (residual distance)/maximum velocity

				# time = dist/vm
				vector = Vector2(self.puck.vector) * (self.puck.speedMagnitude * time)
				position =  self.puck.position + vector * reserve
				if position.x < PUCK_RADIUS and abs(position.y) < FIELD_HEIGHT - PUCK_RADIUS:
					position.x = PUCK_RADIUS
					position.y = self.goalLineIntersection		
				self.predictedPosition = position
				return position
			except:
				return Vector2(0,0)


	# Line math ---------------
	def calculateTrajectory(self):
		self.puck.trajectory = []		
		yBound = (FIELD_HEIGHT / 2 - PUCK_RADIUS)
		myLine = Line(self.puck.position, self.puck.position)
		tempVector = Vector2(self.puck.vector)
		
		self.goalLineIntersection = -10000

		for i in range(self.noOfBounces + 1):
			if not tempVector.x == 0:
				a = tempVector.y / tempVector.x
				b = myLine.start.y - a * myLine.start.x
			else:
				a = 0
				b = 0				

			if tempVector.x == 0: # not a function - vertical line
				myLine.end.x =	myLine.start.x	
				myLine.end.y = sign(tempVector.y) * yBound

			elif a == 0:  # no slope - horizontal line
				myLine.end.x =	sign(tempVector.x) * FIELD_WIDTH
				myLine.end.y = myLine.start.y

			else: # normal linear line
				myLine.end.x = (sign(tempVector.y) * yBound - b) / a
				myLine.end.y = sign(tempVector.y) * yBound

			tempVector.y *= -1	

			if myLine.end.x < PUCK_RADIUS:
				myLine.end.x = PUCK_RADIUS
				myLine.end.y = a*myLine.end.x + b
				tempVector.x *= -1
				tempVector.y *= -1

				# Set goal interection
				self.goalLineIntersection = myLine.end.y

			elif myLine.end.x > FIELD_WIDTH - PUCK_RADIUS:
				myLine.end.x = FIELD_WIDTH - PUCK_RADIUS
				myLine.end.y = a*myLine.end.x + b
				tempVector.x *= -1
				tempVector.y *= -1
				

			self.puck.trajectory.append(myLine.copy())
			# If puck aims at goal, break
			if abs(myLine.end.y) < FIELD_HEIGHT/2 - PUCK_RADIUS: break
			myLine.start.x = myLine.end.x
			myLine.start.y = myLine.end.y

		if len(self.puck.trajectory) > 1:
			self.willBounce = True
		else:
			self.willBounce = False

	# Basic strategy functions used in Process method ---------------------------------------------

	def defendGoalDefault(self):
		if self.willBounce and self.puck.state == ACURATE\
				and (self.puck.vector.x < -0.5 or (self.puck.vector.x < 0 and self.puck.trajectory[-1].end.x <= PUCK_RADIUS))\
				and not (self.puck.position.x > FIELD_WIDTH*.6 and self.puck.speedMagnitude < 500):
			if self.puck.trajectory[-1].end.x > XLIMIT + STRIKER_RADIUS:
				fromPoint = self.puck.trajectory[-1].end
			else:
				fromPoint = self.puck.trajectory[-1].start
		else:
			fromPoint = self.puck.position

		a = Line(fromPoint, Vector2(0,0))
		b = Line(Vector2(DEFENSE_LINE, -FIELD_HEIGHT/2), Vector2(DEFENSE_LINE, FIELD_HEIGHT/2))

		desiredPosition = a.getIntersectPoint(b)

		self.debugLines.append(a)
		self.debugLines.append(b)
		self.debugString = "basic.defendGoalDefault"

		if desiredPosition is not None:
			self.setDesiredPosition(Vector2(desiredPosition))
	
	def defendGoalLastLine(self):
		if self.puck.position.x < self.striker.position.x and abs(self.puck.position.y) < GOAL_SPAN*.7: # if puck is behind striker and is infront of goal
			self.setDesiredPosition(Vector2(self.striker.position.x, GOAL_SPAN/2 * -sign(self.puck.position.y)))
			if abs(self.striker.position.y - GOAL_SPAN/2 * -sign(self.puck.position.y)) < CLOSE_DISTANCE or self.striker.position.x < XLIMIT + CLOSE_DISTANCE:
				self.setDesiredPosition(Vector2(XLIMIT, GOAL_SPAN/2 * -sign(self.puck.position.y)))
				if self.striker.position.x < XLIMIT + CLOSE_DISTANCE:
					self.setDesiredPosition(Vector2(XLIMIT, self.puck.position.y))
			
			return

		if self.striker.position.x < self.puck.position.x - PUCK_RADIUS < self.striker.position.x + PUCK_RADIUS + STRIKER_RADIUS: # if puck is just next to striker
			blockY = self.puck.position.y
		elif not self.goalLineIntersection == -10000 and self.puck.state == ACURATE and self.puck.vector.x < 0:
			if self.puck.vector.x > -.7:
				self.defendGoalDefault()
				return
			else:
				blockY = self.goalLineIntersection
		elif self.puck.state == ACURATE and self.puck.vector.x < 0:
			blockY = self.puck.trajectory[0].end.y
		else: 
			blockY = self.puck.position.y

		# self.debugLines.append(a)
		self.debugString = "basic.defendGoalLastLine"

		self.setDesiredPosition(Vector2(XLIMIT,  sign(blockY) * min(GOAL_SPAN/2 + STRIKER_RADIUS, abs(blockY))))
			# self.setDesiredPosition(Vector2(XLIMIT, sign(self.puck.position.y) * min(GOAL_SPAN/2, abs(self.puck.position.y))))

	def defendTrajectory(self):
		if len(self.puck.trajectory) > 0:
			vector = Vector2(-self.puck.vector.y, self.puck.vector.x)
			secondPoint = self.striker.position + vector

			self.debugString = "basic.defendTrajectory"
			self.debugLines.append(self.puck.trajectory[0])
			self.debugLines.append(Line(self.striker.position, secondPoint))
			self.setDesiredPosition(self.puck.trajectory[0].getIntersectPoint(Line(self.striker.position, secondPoint)))
	
	def moveIfStuck(self):
		if self.puck.speedMagnitude > 100 or self.puck.position.x > STRIKER_AREA_WIDTH + PUCK_RADIUS*.8:
			self.lastMove = self.gameTime

		if 3 < self.gameTime - self.lastMove < 5:
			self.setDesiredPosition(self.puck.position)

	def shouldIntercept(self):
		if len(self.puck.trajectory) == 0:
			return 0
		return self.puck.state == ACURATE and (not self.willBounce or (sign(self.puck.vector.y) * self.puck.trajectory[-1].end.y > GOAL_SPAN )) and self.puck.vector.x < 0


	def isPuckDangerous(self):
		if self.puck.position.x > STRIKER_AREA_WIDTH:
			return True

		if abs(self.puck.velocity.y) > self.maxSpeed:
			return True

		if self.willBounce:
			return True

		if self.striker.position.x > self.puck.position.x - PUCK_RADIUS:
			return True

		if abs(self.goalLineIntersection) < (GOAL_SPAN/2) * 1.2 and self.puck.state == ACURATE:
			if len(self.puck.trajectory) > 0:
				if self.puck.trajectory[-1].getPointLineDist(self.striker.position) > PUCK_RADIUS:
					return True
		return False
