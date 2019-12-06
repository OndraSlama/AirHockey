from pygame.math import Vector2
from Constants import *

class Player():
	def __init__(self, game, strategy, side):
		self.game = game
		self.strategy = strategy
		self.opponent = None
		self.side = side
		self.goals = 0
		self.score = 0
		self.fitness = 0
		self.hitQuality = 0
		self.lastHitIn = 0
		self.newHit = False

		# if self.side == "left":
		# 	self.game.simulation.strikers[0].contactListener = self.checkHits
		# else:
		# 	self.game.simulation.strikers[1].contactListener = self.checkHits

	def update(self, stepTime):
		self.strategy.process(stepTime)
		self.calculateScore()

		if self.newHit and self.game.gameTime > self.lastHitIn + self.game.stepTime * 3:
			self.newHit = False
			self.hitQuality = 10 

		# if self.game.simulation.puck.position.x TODO

	def updatePosition(self, pos):
		if self.side == "left":
			self.strategy.striker.position = Vector2(pos)
		else:
			self.strategy.striker.position = Vector2(FIELD_WIDTH - pos.x, -pos.y)

	def cameraInput(self, pos):
		if self.side == "left":
			self.strategy.cameraInput(Vector2(pos))
		else:
			self.strategy.cameraInput(Vector2(FIELD_WIDTH - pos.x, -pos.y))

	def getDesiredPosition(self):
		if self.side == "left":
			return Vector2(self.strategy.striker.desiredPosition)
		else:
			return Vector2(FIELD_WIDTH - self.strategy.striker.desiredPosition.x, -self.strategy.striker.desiredPosition.y)

	def checkHits(self, my, other):
		self.lastHitIn = self.game.gameTime
		self.newHit = True

	def calculateScore(self):
		if self.score > self.opponent.score:
			self.score += self.game.stepTime * WINNING_POINTS_PER_SEC


	
