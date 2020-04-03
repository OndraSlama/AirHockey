from Simulation.Body import Body
from Constants import *
from pygame.math import Vector2
from Functions import getValueInXYdir

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

		
		vel =  Vector2(self.desiredVelocity)
		if self.mode == "AI":
			maxSpeed = getValueInXYdir(self.desiredVelocity.x, self.desiredVelocity.y, MAX_SPEED).magnitude()
		else:
			maxSpeed = getValueInXYdir(self.desiredVelocity.x, self.desiredVelocity.y, MAX_SPEED).magnitude()

		if vel.magnitude() > maxSpeed:
			vel.scale_to_length(maxSpeed)

		acc = (vel - self.velocity)/self.simulation.stepTime
		
		if self.mode == "AI":
			maxAcc = getValueInXYdir(acc.x, acc.y, MAX_ACCELERATION).magnitude()
		else:
			maxAcc = getValueInXYdir(acc.x, acc.y, MAX_ACCELERATION).magnitude()

		
		if acc.magnitude() > maxAcc:
			if maxAcc == 0:
				acc = Vector2(0,0)
			else:
				acc.scale_to_length(maxAcc)
		
		self.acceleration = acc

