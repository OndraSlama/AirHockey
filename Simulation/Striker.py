from Simulation.Body import Body
from Constants import *
from pygame.math import Vector2
from Functions import getValueInXYdir, isDecelerating
# from numpy import sign

class Striker(Body):
	def __init__(self, sim, x, y, r, m=100, mode = "AI"):
		super().__init__(sim, x, y, r, m)

		self.desiredVelocity = Vector2(0, 0)
		self.mode = mode

	def update(self):

		self.calculateMovement()
		# self.friction(FRICTION_MAG*50, self.simulation.stepTime)
		self.move(1, self.simulation.stepTime)
		# fieldCorners = []
		# self.bounce(BORDER_RESTITUTION, FIELD_HEIGHT/2, -FIELD_HEIGHT/2, 0, FIELD_WIDTH, GOAL_SPAN)

	def calculateVelocity(self, desiredPos):
		self.desiredVelocity = KP_GAIN*(desiredPos - self.position)

	def calculateMovement(self):	

		#----------------------------- limit desired velocity -----------------------------
		vel =  Vector2(self.desiredVelocity)
		# if self.mode == "AI":
		[xMaxSpeed, yMaxSpeed] = getValueInXYdir(vel.x, vel.y, MAX_SPEED)
		# else:
		# 	maxSpeed = getValueInXYdir(self.desiredVelocity.x, self.desiredVelocity.y, MAX_SPEED).magnitude()

		if abs(vel.x) > abs(xMaxSpeed):
			vel.x = xMaxSpeed

		if abs(vel.y) > abs(yMaxSpeed):
			vel.y = yMaxSpeed

		# if vel.magnitude() > maxSpeed:
		# 	vel.scale_to_length(maxSpeed)

		#----------------------------- limit acceleration to desired velocity -----------------------------
		acc = (vel - self.velocity)/self.simulation.stepTime
		
		# if self.mode == "AI":
		[xMaxAcc, yMaxAcc] = getValueInXYdir(acc.x, acc.y, MAX_DECELERATION if isDecelerating(*self.velocity, *vel) else MAX_ACCELERATION)
		# else:
		# 	maxAcc = getValueInXYdir(acc.x, acc.y, MAX_ACCELERATION).magnitude()

		if abs(acc.x) > abs(xMaxAcc):
			acc.x = xMaxAcc

		if abs(acc.y) > abs(yMaxAcc):
			acc.y = yMaxAcc
		
		# if acc.magnitude() > maxAcc:
		# 	if maxAcc == 0:
		# 		acc = Vector2(0,0)
		# 	else:
		# 		acc.scale_to_length(maxAcc)
		
		self.acceleration = acc

