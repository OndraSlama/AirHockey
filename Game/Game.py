from Constants import *
from Simulation.Simulation import Simulation
from Game.Camera import Camera
from Game.Strategy.StrategyA import StrategyA
from Game.Strategy.BaseStrategy import BaseStrategy
from pygame.math import Vector2

class Game():
	def __init__(self):
		self.simulation = Simulation(self)
		self.camera = Camera(self, 90)
		self.leftStrategy = StrategyA()
		self.rightStrategy = StrategyA()
		self.score = [0, 0]
		self.gameTime = 0

	def update(self, stepTime):
		self.gameTime += stepTime
		self.simulation.step(stepTime)
		self.camera.update()

		self.leftStrategy.striker.position = Vector2(self.simulation.strikers[0].position)
		self.rightStrategy.striker.position = Vector2(FIELD_WIDTH - self.simulation.strikers[1].position.x, -self.simulation.strikers[1].position.y)

		if self.camera.newData:
			self.leftStrategy.cameraInput(Vector2(self.camera.puckPosition))
			self.rightStrategy.cameraInput(Vector2(FIELD_WIDTH - self.camera.puckPosition.x, -self.camera.puckPosition.y))
			self.camera.newData = False

		self.leftStrategy.process(stepTime)
		self.rightStrategy.process(stepTime)

		self.simulation.strikers[0].desiredPosition = Vector2(self.leftStrategy.striker.desiredPosition)
		self.simulation.strikers[1].desiredPosition = Vector2(FIELD_WIDTH - self.rightStrategy.striker.desiredPosition.x, -self.rightStrategy.striker.desiredPosition.y)

		self.checkGoal()

	def checkGoal(self):
		if self.simulation.puck.position.x < 0:
			self.score[0] += 1
			self.simulation.spawnPuck()

		if self.simulation.puck.position.x > FIELD_WIDTH:
			self.score[1] += 1
			self.simulation.spawnPuck()