from Constants import *
from Simulation.Puck import Puck
from Simulation.Striker import Striker
from pygame.math import Vector2
from Functions import *
from random import gauss, randrange

class Simulation():
	def __init__(self, game, mode):
		self.game = game
		self.stepTime = MIN_STEP_TIME
		self.strikers = []
		self.puck = None
		self.strikers.append(Striker(self, 100,0, STRIKER_RADIUS, STRIKER_MASS, mode="AI"))
		if mode == "vsAI" or mode == "vsNN":
			self.strikers.append(Striker(self, FIELD_WIDTH - 100, 0, STRIKER_RADIUS, STRIKER_MASS, mode="PLAYER"))
		else:
			self.strikers.append(Striker(self, FIELD_WIDTH - 100, 0, STRIKER_RADIUS, STRIKER_MASS, mode="AI"))

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
		mouse = Vector2((p2uX(mousePos[0]), p2uY(mousePos[1])))
		self.puck.followPos(mouse)

	def leftMouseDown(self, mousePos):
		mouse = Vector2((p2uX(mousePos[0]), p2uY(mousePos[1])))
		self.strikers[1].desiredPosition = mouse
		if self.strikers[1].desiredPosition.x < FIELD_WIDTH/2:
			self.strikers[1].desiredPosition.x = FIELD_WIDTH/2

	def middleMouseDown(self, mousePos):
		mouse = Vector2((p2uX(mousePos[0]), p2uY(mousePos[1])))
		self.puck.goToPosition(mouse)
	
	def spawnPuck(self):
		self.puck = Puck(self, FIELD_WIDTH/2, -FIELD_HEIGHT/2, PUCK_RADIUS, PUCK_MASS)
		self.puck.velocity = Vector2(randrange(-300, 300), randrange(300, 400))