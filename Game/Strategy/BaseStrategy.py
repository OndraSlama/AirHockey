from Game.Strategy.StrategyStructs import *
from Game.HelperClasses import Filter
from Constants import *
from numpy import sign
import pygame.math as gameMath

class BaseStrategy():
	def __init__(self):

		# Striker
		self.striker = StrategyStriker()
		self.opponentStriker = StrategyStriker()

		# Puck
		self.puck = StrategyPuck()
		self.puckHistory = []
		self.puckHistory.append(self.puck)

		# Trajectory info
		self.goalLineIntersection = 0

		# Parameters
		self.historySize = 50
		self.noOfBounces = 1
		self.minSpeedLimit = 30
		self.angletolerance = 70
		self.lowAngletolerance = 8
		self.positionTolerance = 100
		self.capturesWithBadAngle = 0

		# States
		self.timeSinceLastCameraInput = 0
		self.sameCameraInputsInRow = 0
		self.previousErrorSide = 0
		self.firstUsefull = 1

		# Filter
		self.velocityFilter = Filter(3, 2, 1.5)

		# Init
		for i in range(self.historySize - 1):
			self.puckHistory.append(StrategyPuck())
	
	def cameraInput(self, pos):
		if pos == self.puck.position: return
		self.initialCheck(pos)
		self.setPuck(pos)
		self.checkState()
		self.calculateTrajectory()	

	def stepTick(self, stepTime):
		for puck in self.puckHistory:
			puck.timeSinceCaptured += stepTime

	def initialCheck(self, pos):
		self.puck.state = ACURATE

		currentStepVector = pos - self.puck.position
		# currentVelocity = currentStepVector / self.puck.timeSinceCaptured
		# currentPosition = gameMath.Vector2(pos)
		errorAngle = currentStepVector.angle_to(self.puck.velocity)
		if abs(errorAngle) > 180: errorAngle -= sign(errorAngle) * 360

		# Low angle condition
		if abs(errorAngle) > self.lowAngletolerance and sign(errorAngle) == self.previousErrorSide:
			self.capturesWithBadAngle += 1
			if(self.capturesWithBadAngle > 4):
				# print("Low angle condition.. 4 states -> useless")
				for i in range(4):
					self.puckHistory[self.firstUsefull].state = USELESS
					if self.firstUsefull > 1: self.firstUsefull -= 1
		else:
			self.capturesWithBadAngle = 0

		self.previousErrorSide = sign(errorAngle)

		# Angle condition
		if(abs(errorAngle) > self.angletolerance):
			self.capturesWithBadAngle = 0					 
			# print("Angle condition: " + str(errorAngle))
			for puck in self.puckHistory:
				puck.state = USELESS

		# Quick acceleration - does nothing for now
		# i = self.firstUsefull - 1
		# while self.puckHistory[firstUsefull].position.distance_squared_to(self.puckHistory[i].position) < positionTolerance**2:
		# 	if i <= 1: break
		# 	i -= 1
		
		
	def setPuck(self, pos):
		self.puck = StrategyPuck(self.puck.state, pos)
		self.puckHistory.pop(-1)
		self.puckHistory.insert(0, self.puck)

		self.firstUsefull = len(self.puckHistory) - 1
		while(self.puckHistory[self.firstUsefull].state == USELESS):
			self.firstUsefull -= 1
			if self.firstUsefull == 1: break
		
		if not self.puckHistory[self.firstUsefull].timeSinceCaptured == 0:
			stepVector = pos - self.puckHistory[self.firstUsefull].position
			self.puck.velocity = stepVector / self.puckHistory[self.firstUsefull].timeSinceCaptured

			# Filter velocity and normal vector
			self.puck.velocity = self.velocityFilter.filterData(self.puck.velocity)

			self.puck.vector = self.puck.velocity.normalize()
			self.puck.speedMagnitude = self.puck.velocity.magnitude()		
			self.puck.timeSinceCaptured = 0
	
	def checkState(self):
		# Check for inacurate
		if abs(self.puck.speedMagnitude < self.minSpeedLimit):
			self.puck.state = INACURATE

		if abs(self.puck.vector.y) > 0.9:
			self.puck.state = INACURATE

		if self.firstUsefull < round(self.historySize/20):
			self.puck.state = INACURATE

	def process(self, stepTime):
		pass	

	def calculateTrajectory(self):		
		
		self.puck.trajectory = []		
		yBound = (FIELD_HEIGHT / 2 - PUCK_RADIUS)
		myLine = Line(self.puck.position, self.puck.position)
		tempVector = gameMath.Vector2(self.puck.vector)

		
		self.goalLineIntersection = -10000

		for i in range(self.noOfBounces + 1):
			a = tempVector.y / tempVector.x
			b = myLine.start.y - a * myLine.start.x

			if tempVector.x == 0:
				myLine.end.y = sign(tempVector.y) * yBound				
				tempVector.y *= -1   
			else:
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
			if abs(myLine.end.y) < GOAL_SPAN/2: break  
			myLine.start.x = myLine.end.x
			myLine.start.y = myLine.end.y 
		
	

	# draw():
	# 	if(self.player.color == "red"):
	# 		# Speed vector
	# 		pos = b2.u2p(self.ball.position)
	# 		# stroke(0, 255, 0, 100)	  
	# 		# strokeWeight(4)
	# 		# line(pos.x, pos.y, pos.x + self.ball.velocity.x, pos.y)
	# 		# line(pos.x, pos.y, pos.x, pos.y - self.ball.velocity.y)   

	# 		# Trajectory		
	# 		strokeWeight(1)
	# 		for (myLine of self.ball.trajectory):
	# 			pos = b2.u2p(myLine.start.x, myLine.start.y)
	# 			pos2 = b2.u2p(myLine.end.x, myLine.end.y)
	# 			stroke(255, 0, 0, 100)
	# 			line(pos.x, pos.y, pos2.x, pos2.y)
			
		
	# 		# Ball history   
	# 		noFill()		
	# 		for(i = 0 i < self.balls.length i += 1):	 
	# 			pos = b2.u2p(self.balls[i].position)
	# 			nextPos = b2.u2p(self.balls[min(i + 1, self.balls.length - 1)].position)
	# 			if (self.balls[i].state == UNKNOWN):
	# 				stroke(255, 0, 0, 150)
	# 			else:
	# 				stroke(0, 255, 0, 150)
				
	# 			ellipse(pos.x, pos.y, 4)
	# 			line(pos.x, pos.y, nextPos.x, nextPos.y)						
			
		

	# 	# Desired pos
	# 	desired = createVector()
	# 	for (axis of self.playerAxes):				
			
	# 		if (self.player.color == "blue"):
	# 			desired = b2.u2p(FIELD_WIDTH - axis.x, -axis.desiredIntercept)
	# 		else:
	# 			desired = b2.u2p(axis.x, axis.desiredIntercept)
					
	# 		stroke("black")
	# 		fill("black")
	# 		ellipse(desired.x, desired.y, 4)
		
	



# class strategyAxis:
#	 constructor():
#		 self.position
#		 self.velocity
#		 self.trajectory
#	 
# 
