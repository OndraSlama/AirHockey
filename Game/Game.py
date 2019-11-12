from Constants import *
from Simulation.Simulation import Simulation
from Game.Camera import Camera
from Game.Strategy.BaseStrategy import BaseStrategy
from pygame.math import Vector2

class Game():
	def __init__(self):
		self.simulation = Simulation()
		self.camera = Camera(self, 90)
		self.leftStrategy = BaseStrategy()
		self.rightStrategy = BaseStrategy()

	def update(self, stepTime):
		self.simulation.step(stepTime)
		self.camera.update()

		if self.camera.newData:
			self.leftStrategy.cameraInput(Vector2(self.camera.puckPosition))
			self.camera.newData = False

		self.leftStrategy.process(stepTime)

		self.simulation.strikers[0].desiredPos = self.leftStrategy.striker.desiredPosition