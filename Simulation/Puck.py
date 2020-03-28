from Simulation.Body import Body
from Constants import *
from pygame.math import Vector2
from random import randrange
from numpy import sign
from HelperClasses import Line

class Puck(Body):
	def __init__(self, sim, x, y, r, m=20):
		super().__init__(sim, x, y, r, m)
		self.position.y = 0
		self.velocity.x = 0
		self.velocity.y = 0
		self.lastMovement = 0

	def update(self):

		# line = Line(Vector2(1000, GOAL_SPAN/2), Vector2(1000, 300))
		# if self.intersectsLine(line):
		# 	self.bounceFromLine(line)
		# print(self.intersectsLine(line))

		# print(line.getPointSegmentDist(self.position))
		
		# print(Line(Vector2(500, 300), Vector2(500, -300)).getPointSide(self.position))


		self.moveIfStuck()
		self.move(VELOCITY_DAMP**(self.simulation.stepTime/MIN_STEP_TIME), self.simulation.stepTime)
		# self.bounce(BORDER_RESTITUTION, FIELD_HEIGHT/2, -FIELD_HEIGHT/2, 0, FIELD_WIDTH, GOAL_SPAN)	

	def moveIfStuck(self):
		if abs(self.velocity.x) > 5 or abs(self.velocity.y) > 5:
			self.lastMovement = self.simulation.game.gameTime

		if self.simulation.game.gameTime - self.lastMovement > 2:
			direction = -sign(self.position.x - FIELD_WIDTH/2)
			if direction == 0: direction = 1
			self.applyForce(Vector2(direction*randrange(70000, 90000), randrange(-50000, 50000)))

	def goToPosition(self, pos):
		self.position = pos
		self.velocity = Vector2(0,0)
		self.acceleration = Vector2(0,0)
		self.lastMovement = self.simulation.game.gameTime

