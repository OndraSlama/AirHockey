from Constants import *
from Simulation.Simulation import Simulation
from Game.Player import Player
from Game.Camera import Camera
from Game.Strategy import StrategyA, StrategyB, StrategyC, StrategyD 
from Game.Strategy.BaseStrategy import BaseStrategy
from pygame.math import Vector2

class Game():
	def __init__(self, mode):
		self.simulation = Simulation(self, mode)
		self.camera = Camera(self, 66)
		
		# Players
		self.players = []
		self.players.append(Player(self, StrategyD.StrategyD(), "left"))
		if mode == "vsAI" or mode == "vsNN":
			self.players.append(Player(self, BaseStrategy(), "right"))
		else:
			self.players.append(Player(self, StrategyD.StrategyD(), "right"))

		self.players[0].opponent = self.players[1]
		self.players[1].opponent = self.players[0]

		# States
		self.gameTime = 0
		self.gameSpeed = 1
		self.stepTime = MIN_STEP_TIME
		self.mousePosition = None
		self.leftMouseDown = False
		self.middleMouseDown = False
		self.rightMouseDown = False

	def update(self):
		stepTime = self.stepTime
		mousePos = self.mousePosition
		self.gameTime += stepTime
		# print(stepTime)

		if self.leftMouseDown: self.simulation.leftMouseDown(mousePos)
		if self.middleMouseDown: self.simulation.middleMouseDown(mousePos)
		if self.rightMouseDown: self.simulation.rightMouseDown(mousePos)

		self.simulation.step(stepTime)
		self.camera.update()

		for i in range(len(self.players)):
			self.players[i].updatePosition(self.simulation.strikers[i].position)
			if self.camera.newData:
				self.players[i].cameraInput(self.camera.puckPosition)

			self.players[i].update(stepTime)

			self.simulation.strikers[i].desiredPosition = self.players[i].getDesiredPosition()

		self.camera.newData = False		
		self.checkGoal()

		return self

	def checkGoal(self):
		if self.simulation.puck.position.x < 0:
			self.players[1].goals += 1
			self.players[1].score += POINTS_PER_GOAL
			self.simulation.spawnPuck()

		if self.simulation.puck.position.x > FIELD_WIDTH:
			self.players[0].goals += 1
			self.players[0].score += POINTS_PER_GOAL
			self.simulation.spawnPuck()