from Strategy.StrategyStructs import *
from HelperClasses import Filter
from Constants import *
from numpy import sign
from pygame.math import Vector2

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
					self.debugLines.append(trajectoryLine)
					self.debugLines.append(bounceLine)
					bouncePoint = self.getIntersectPoint(trajectoryLine, bounceLine)
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
			fi = self.angleFilter.filterData(fi, 360)
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
			desiredPos = self.getBothCoordinates(line, x = STRIKER_AREA_WIDTH)

		if abs(desiredPos.y) > YLIMIT:
			desiredPos = self.getBothCoordinates(line, y = sign(desiredPos.y) * YLIMIT)

		if desiredPos.x < XLIMIT: 
			desiredPos = self.getBothCoordinates(line, x = XLIMIT)

		self.setDesiredPosition(desiredPos)


	def limitMovement(self):
		if self.striker.desiredPosition.x > STRIKER_AREA_WIDTH:
			self.striker.desiredPosition.x = STRIKER_AREA_WIDTH

		if abs(self.striker.desiredPosition.y) > YLIMIT:
			self.striker.desiredPosition.y = sign(self.striker.desiredPosition.y) * YLIMIT

		if self.striker.desiredPosition.x < XLIMIT: 
			self.striker.desiredPosition.x = XLIMIT

	def calculateDesiredVelocity(self):
		gain = (self.acceleration/700)
		self.striker.desiredVelocity = gain*(self.striker.desiredPosition - self.striker.position)

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

	def getIntersectPoint(self, line1, line2):
		self.debugLines.append(line1)
		self.debugLines.append(line2)

		p1 = (line1.start.x, line1.start.y)
		p2 = (line1.end.x, line1.end.y)
		p3 = (line2.start.x, line2.start.y)
		p4 = (line2.end.x, line2.end.y)
		m1 = self.calculateGradient(p1, p2)
		m2 = self.calculateGradient(p3, p4)
		
		# See if the the lines are parallel
		if (m1 != m2):
			# Not parallel
			
			# See if either line is vertical
			if (m1 is not None and m2 is not None):
				# Neither line vertical
				b1 = self.calculateYAxisIntersect(p1, m1)
				b2 = self.calculateYAxisIntersect(p3, m2)
				x = (b2 - b1) / (m1 - m2)
				y = (m1 * x) + b1
			else:
				# Line 1 is vertical so use line 2's values
				if (m1 is None):
					b2 = self.calculateYAxisIntersect(p3, m2)
					x = p1[0]
					y = (m2 * x) + b2
				# Line 2 is vertical so use line 1's values
				elif (m2 is None):
					b1 = self.calculateYAxisIntersect(p1, m1)
					x = p3[0]
					y = (m1 * x) + b1
				else:
					assert False
					
			return Vector2(x,y)
		else:
			# Parallel lines with same 'b' value must be the same line so they intersect
			# everywhere in this case we return the start and end points of both lines
			# the calculateIntersectPoint method will sort out which of these points
			# lays on both line segments
			b1, b2 = None, None # vertical lines have no b value
			if m1 is not None:
				b1 = self.calculateYAxisIntersect(p1, m1)
			
			if m2 is not None:
				b2 = self.calculateYAxisIntersect(p3, m2)
			
			# If these parallel lines lay on one another   
			if b1 == b2:
				return None # p1,p2,p3,p4
			else:
				return None

	def getAngleDifference(self, vector1, vetor2):
		errorAngle = vector1.angle_to(vetor2)
		if abs(errorAngle) > 180: errorAngle -= sign(errorAngle) * 360
		return errorAngle

	def getPointLineDist(self, point, line):
		m = self.calculateGradient(line.start, line.end)
		k = self.calculateYAxisIntersect(line.start, m)

		if m is not None:
			return abs(k + m*point.x - point.y) / (1 + m**2)**0.5
		else:
			return abs(line.start.x - point.x)

	def getBothCoordinates(self, line, y=None, x = None):
		a = self.calculateGradient(line.start, line.end)
		b = self.calculateYAxisIntersect(line.start, a)

		if a is not None:
			if y is not None:
				if not a==0:
					x = (y - b)/a				
			elif x is not None:
				y = a*x + b
		elif y is not None:
			x = line.start.x
		return Vector2(x, y)

	def getPerpendicularPoint(self, pos, line):
		vector = line.end - line.start
		perpendiculatVector = Vector2(-vector.y, vector.x)
		# secondPoint = pos + perpendiculatVector

		return self.getIntersectPoint(line, Line(pos - perpendiculatVector, pos + perpendiculatVector))

	def getValueInXYdir(self, dir_x, dir_y, value):
		if dir_x == 0 and dir_y == 0:
			return Vector2([value/2,value/2])
	
		def map(val, in_min, in_max, out_min, out_max): # maps from interval to other interval
			return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
		# dir_x = vektor rychlosti x
		# dir_y = vektor rychlosti y
		dir_0 = -dir_x - dir_y
		dir_1 = dir_x - dir_y
		absdir_0 = abs(dir_0)
		absdir_1 = abs(dir_1)
		bigger = absdir_0 if absdir_0 > absdir_1 else absdir_1

		absdir_0 = map(absdir_0 , 0 , bigger, 0, value)
		absdir_1 = map(absdir_1 , 0 , bigger, 0, value)

		dir_0 = absdir_0 if dir_0>=0 else -absdir_0
		dir_1 = absdir_1 if dir_1>=0 else -absdir_1

		return Vector2([round(-dir_0 + dir_1), round(-dir_0 - dir_1)])

	def getPredictedPuckPosition(self, strikerPos = None, reserve=1.3):
		if strikerPos is None: strikerPos = self.striker.desiredPosition
		if self.puck.state == INACURATE:
			return Vector2(self.puck.position)
		if len(self.puck.trajectory) > 0:
			try:
				step = strikerPos - self.striker.position
				dist = step.magnitude()
				# Compute time, that will take striker to move to desired position
				a = self.getValueInXYdir(step.x, step.y, self.acceleration).magnitude()
				vm = self.getValueInXYdir(step.x, step.y, self.maxSpeed).magnitude()
				v0 = sign(self.striker.velocity.dot(step)) * (step * self.striker.velocity.dot(step) / step.dot(step)).magnitude() #self.striker.speedMagnitude * step.normalize()
				
				t1 = (vm - v0)/a	
				d1 = 1/2 * a * t1**2 + v0*t1
				if d1 > dist:
					time = max((-v0 + (v0**2 + 2*a*dist)**.5)/a, (-v0 - (v0**2 + 2*a*dist)**.5)/a)
				else:
					time = t1 + (dist - d1)/vm

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

	def calculateGradient(self, p1, p2):  
		# Ensure that the line is not vertical
		if (p1[0] != p2[0]):
			m = (p1[1] - p2[1]) / (p1[0] - p2[0])
			return m
		else:
			return None

	def calculateYAxisIntersect(self, p, m):
		if m is not None:
   			return  p[1] - (m * p[0])
		else:
			return None



	# Basic strategy functions used in Process method ---------------------------------------------

	def defendGoalDefault(self):
		if self.willBounce and self.puck.state == ACURATE and (self.puck.vector.x < -0.5 or (self.puck.vector.x < 0 and self.puck.trajectory[-1].end.x <= PUCK_RADIUS)) and not (self.puck.position.x > FIELD_WIDTH/2 and self.puck.speedMagnitude < 800):
			if self.puck.trajectory[-1].end.x > XLIMIT + STRIKER_RADIUS:
				fromPoint = self.puck.trajectory[-1].end
			else:
				fromPoint = self.puck.trajectory[-1].start
		else:
			fromPoint = self.puck.position

		a = Line(fromPoint, Vector2(0,0))
		b = Line(Vector2(DEFENSE_LINE, -FIELD_HEIGHT/2), Vector2(DEFENSE_LINE, FIELD_HEIGHT/2))

		desiredPosition = self.getIntersectPoint(a, b)

		self.debugLines.append(a)
		self.debugLines.append(b)
		self.debugString = "basic.defendGoalDefault"

		if desiredPosition is not None:
			self.setDesiredPosition(Vector2(desiredPosition))
	
	def defendGoalLastLine(self):
		if self.striker.position.x < self.puck.position.x - PUCK_RADIUS < self.striker.position.x + PUCK_RADIUS + STRIKER_RADIUS:
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
			self.setDesiredPosition(self.getIntersectPoint(self.puck.trajectory[0], Line(self.striker.position, secondPoint)))
	
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
				if self.getPointLineDist(self.striker.position, self.puck.trajectory[-1]) > PUCK_RADIUS:
					return True
		return False