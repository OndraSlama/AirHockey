from Constants import *
from Simulation.Puck import Puck
from Simulation.Striker import Striker
import pygame.math as gameMath
from Functions import *
from random import gauss, randrange

class Simulation():
	def __init__(self, game):
		self.game = game
		self.stepTime = MIN_STEP_TIME
		self.strikers = []
		self.puck = None
		self.strikers.append(Striker(self, 100,0, STRIKER_RADIUS, STRIKER_MASS))
		self.strikers.append(Striker(self, FIELD_WIDTH - 100, 0, STRIKER_RADIUS, STRIKER_MASS))
		self.spawnPuck()

	def step(self, stepTime):
		self.stepTime = stepTime

		# Handle collisions
		for striker in self.strikers:
			if self.puck.intersects(striker):
				self.puck.resolveCollision(STRIKER_RESTITUTION, striker)

		# Update movement
		self.puck.update()
		for striker in self.strikers:
			striker.update()
			

	def rightMouseDown(self, mousePos):		
		mouse = gameMath.Vector2((p2uX(mousePos[0]), p2uY(mousePos[1])))
		self.puck.followPos(mouse)

	def leftMouseDown(self, mousePos):
		mouse = gameMath.Vector2((p2uX(mousePos[0]), p2uY(mousePos[1])))
		self.strikers[1].desiredPosition = mouse
	
	def spawnPuck(self):
		self.puck = Puck(self, FIELD_WIDTH/2, -FIELD_HEIGHT/2, PUCK_RADIUS, PUCK_MASS)
		self.puck.velocity = gameMath.Vector2(randrange(-300, 300), randrange(300, 400))