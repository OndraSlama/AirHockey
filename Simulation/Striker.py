from Simulation.Body import Body
from Constants import *
import pygame.math as gameMath

class Striker(Body):
	def __init__(self, sim, x, y, r, m=100):
		super().__init__(sim, x, y, r, m)
		self.desiredPosition = gameMath.Vector2(600, 300)

	def update(self):
		self.calculateMovement()
		# self.friction(FRICTION_MAG*50, self.simulation.stepTime)
		self.move(1, self.simulation.stepTime)
		self.bounce(BORDER_RESTITUTION, FIELD_HEIGHT/2, -FIELD_HEIGHT/2, 0, FIELD_WIDTH, GOAL_SPAN)

	def calculateMovement(self):
		gain = (MAX_ACCELERATION/600)
		vel =  gain*(self.desiredPosition - self.position)

		if vel.magnitude() > MAX_SPEED:
			vel.scale_to_length(MAX_SPEED)

		acc = (vel - self.velocity)/self.simulation.stepTime
		accMag = acc.magnitude()

		if accMag > MAX_ACCELERATION:
			acc.scale_to_length(MAX_ACCELERATION)
		
		if accMag < -MAX_ACCELERATION:
			acc.scale_to_length(MAX_ACCELERATION)		
		
		self.acceleration = acc
