from Simulation.Body import Body
from Constants import *
from pygame.math import Vector2

class Striker(Body):
	def __init__(self, sim, x, y, r, m=100, mode = "AI"):
		super().__init__(sim, x, y, r, m)
		self.desiredPosition = Vector2(600, 300)
		self.mode = mode

	def update(self):
		self.calculateMovement()
		# self.friction(FRICTION_MAG*50, self.simulation.stepTime)
		self.move(1, self.simulation.stepTime)
		self.bounce(BORDER_RESTITUTION, FIELD_HEIGHT/2, -FIELD_HEIGHT/2, 0, FIELD_WIDTH, GOAL_SPAN)

	def calculateMovement(self):	

		gain = (MAX_ACCELERATION/600)
		vel =  gain*(self.desiredPosition - self.position)

		if self.mode == "AI":
			maxSpeed = MAX_SPEED
			maxAcc = MAX_ACCELERATION
		else:
			maxSpeed = MAX_SPEED*50
			maxAcc = MAX_ACCELERATION*500

		if vel.magnitude() > maxSpeed:
			vel.scale_to_length(maxSpeed)

		acc = (vel - self.velocity)/self.simulation.stepTime
		accMag = acc.magnitude()

		if accMag > maxAcc:
			acc.scale_to_length(maxAcc)
		
		if accMag < -maxAcc:
			acc.scale_to_length(maxAcc)		
		
		self.acceleration = acc
