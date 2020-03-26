from Constants import *
from Simulation.Simulation import Simulation
from Game.Player import Player
from Game.Camera import Camera
from Strategy import StrategyA, StrategyB, StrategyC, StrategyD, NN_StrategyA
from Strategy.BaseStrategy import BaseStrategy
from pygame.math import Vector2

class Game():
	def __init__(self, mode):
		self.simulation = Simulation(self, mode)
		self.camera = Camera(self, 70)
		self.mode = mode
		# Players
		self.players = []
		if mode == "NE" or mode == "vsNN":
			self.players.append(Player(self, NN_StrategyA.NN_StrategyA(), "left"))			
		else:
			self.players.append(Player(self, StrategyD.StrategyD(), "left"))

		if mode == "vsAI" or mode == "vsNN":
			self.players.append(Player(self, BaseStrategy(), "right"))
		elif mode == "NE":
			self.players.append(Player(self, NN_StrategyA.NN_StrategyA(), "right"))
		else:
			self.players.append(Player(self, StrategyD.StrategyD(), "right"))

		self.players[0].opponent = self.players[1]
		self.players[1].opponent = self.players[0]
		
		# States
		self.gameDone = False
		self.gameTime = 0
		self.gameSpeed = 1
		self.scoreChangeAt = 0
		self.prevScore = [0, 0]		

		self.bestScorePlayer = -1
		self.winner = -1

		self.stepTime = MIN_STEP_TIME
		self.mousePosition = None
		self.leftMouseDown = False
		self.middleMouseDown = False
		self.rightMouseDown = False

	def update(self):
		stepTime = self.stepTime
		mousePos = self.mousePosition
		self.gameTime += stepTime

		if not self.gameDone:
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

				self.simulation.strikers[i].desiredVelocity = self.players[i].getDesiredVelocity()

			self.camera.newData = False

			self.checkGoal()
			self.checkEnd()

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

	def checkEnd(self):
		goals = [self.players[0].goals, self.players[1].goals]
		score = [self.players[0].score, self.players[1].score]
		
		if not(score == self.prevScore) and self.mode == "NE":
			self.scoreChangeAt = self.gameTime
			self.prevScore = score
		
		if self.mode == "NE" and self.gameTime - self.scoreChangeAt > 20:
			self.gameDone = True

		if self.mode == "NE" and self.gameTime >= TIME_LIMIT:
			self.gameDone = True			

		for player in self.players:
			if player.goals >= GOAL_LIMIT:
				self.gameDone = True

		if self.gameDone:
			goals = [self.players[0].goals, self.players[1].goals]
			score = [self.players[0].score, self.players[1].score]
			
			if goals[0] == goals[1]:
				self.winner = 2
			else:
				self.winner = goals.index(max(goals))

			self.bestScorePlayer = score.index(max(score))
				