from Simulation.Body import Body
from Constants import *
from pygame.math import Vector2
from random import randrange
from numpy import sign

class Puck(Body):
	def __init__(self, sim, x, y, r, m=20):
		super().__init__(sim, x, y, r, m)
		self.position.y = 200
		self.velocity.x = 1000
		self.velocity.y = 800
		self.lastMovement = 0

	def update(self):
		self.friction(FRICTION_MAG, self.simulation.stepTime)
		self.moveIfStuck()
		self.move(VELOCITY_DAMP**(self.simulation.stepTime/0.02), self.simulation.stepTime)
		self.bounce(BORDER_RESTITUTION, FIELD_HEIGHT/2, -FIELD_HEIGHT/2, 0, FIELD_WIDTH, GOAL_SPAN)	

	def moveIfStuck(self):
		if self.velocity.x > 10 or self.velocity.y > 10:
			self.lastMovement = self.simulation.game.gameTime

		if self.simulation.game.gameTime - self.lastMovement > 2:
			self.applyForce(Vector2(sign(self.position.x - FIELD_WIDTH/2)*randrange(500000, 800000), randrange(-300000, 300000)))

