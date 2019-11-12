from Constants import *
from Simulation.Puck import Puck
from Simulation.Striker import Striker
import pygame.math as gameMath
from Functions import *

class Simulation():
	def __init__(self):
		self.stepTime = MIN_STEP_TIME
		self.puck = Puck(self, 0, 0, PUCK_RADIUS, PUCK_MASS)
		self.strikers = []
		self.strikers.append(Striker(self, 100,0, STRIKER_RADIUS, STRIKER_MASS))
		self.strikers.append(Striker(self, FIELD_WIDTH - 100, 0, STRIKER_RADIUS, STRIKER_MASS))

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
		self.strikers[1].desiredPos = mouse
	