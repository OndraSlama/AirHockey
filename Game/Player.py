# ****************************************************************************** #
# Author: Ondrej Slama
# -------------------

# Zdrojovy kod vytvoreny v ramci projektu robotickeho vzdusneho hokeje - diplomova prace
#  na VUT FSI ustavu automatizace a informatiky v Brne.

# Source code created as a part of robotic air hockey table project - Diploma thesis
# at BUT FME institute of automation and computer sience.

# ****************************************************************************** #
from pygame.math import Vector2
from Constants import *

from UniTools import Line


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
		self.lastHit = False
		self.puckInArea = False

		if self.side == "left":
			self.game.simulation.strikers[0].postContact = self.checkHits
		else:
			if not self.game.playground:
				self.game.simulation.strikers[1].postContact = self.checkHits

	def update(self, stepTime):
		self.strategy.process(stepTime)
		self.calculateScore()

		# if self.newHit and self.game.gameTime > self.lastHitIn + self.game.stepTime * 3:
		# 	self.newHit = False
		# 	self.hitQuality = 10 

		# if self.game.simulation.puck.position.x TODO

	def updatePosition(self, pos):
		self.strategy.setStriker(Vector2(self.getRelativePos(pos)))

	def cameraInput(self, pos):
		self.strategy.cameraInput(self.getRelativePos(pos))

	def getDesiredPosition(self):
		return self.getRelativePos(self.strategy.striker.desiredPosition)

	def getDesiredVelocity(self):
		return self.getRelativeVector(self.strategy.striker.desiredVelocity)

	def markShot(self, puck):
		puckPos = self.getRelativePos(puck.position)
		puckVel = self.getRelativeVector(puck.velocity)

		if puckVel.x < 0:
			return 0

		shotLine = Line(puckPos, puckPos + puckVel)
		goalLine = Line(Vector2(FIELD_WIDTH, 0), Vector2(FIELD_WIDTH, 1))
		intersection = shotLine.getIntersectPoint(goalLine)

		if intersection is None:
			return 0

		distFromCenter = abs(intersection.y)
		bounces = 0

		afterBounceDist = distFromCenter
		while afterBounceDist > FIELD_HEIGHT/2:
			bounces += 1
			afterBounceDist -= FIELD_HEIGHT

		afterBounceDist = abs(afterBounceDist)

		if bounces > 3:
			return 0
		
		if afterBounceDist > GOAL_SPAN/2:
			accuracy = min(1, ((GOAL_SPAN/2) / afterBounceDist) ** 2)
		else:
			accuracy = 1

		return round(puck.velocity.magnitude_squared()/100000 * accuracy)

	def checkHits(self, me, puck):
		pass
		# puckPos = self.getRelativePos(puck.position)
		# puckVel = self.getRelativeVector(puck.velocity)
		# self.hitQuality = 0

		# if puckVel.x < 0:
		# 	return

		# shotLine = Line(puckPos, puckPos + puckVel)
		# goalLine = Line(Vector2(FIELD_WIDTH, 0), Vector2(FIELD_WIDTH, 1))
		# intersection = self.strategy.getIntersectPoint(shotLine, goalLine)
		# distFromCenter = abs(intersection.y)
		# bounces = floor(distFromCenter / (FIELD_HEIGHT/2))
		# if bounces > 3:
		# 	return

		# if bounces == 0:
		# 	certainity = 2
		# else:
		# 	certainity = 1

		# afterBounceDist = abs(distFromCenter % (FIELD_HEIGHT/2) - bounces * FIELD_HEIGHT/2)
		
		# if afterBounceDist > GOAL_SPAN/2:
		# 	accuracy = min(1, ((GOAL_SPAN/2) / afterBounceDist) ** certainity)
		# else:
		# 	accuracy = 1

		# print(accuracy)


		# self.hitQuality = round(puck.velocity.magnitude_squared()/100000)


		# print(self.hitQuality)

	def calculateScore(self):
		puckPos = self.getRelativePos(self.game.simulation.puck.position)

		if puckPos.x > STRIKER_AREA_WIDTH + PUCK_RADIUS + STRIKER_RADIUS and self.puckInArea:
			self.puckInArea = False
			self.score += self.markShot(self.game.simulation.puck) * SHOT_POINT_MULTIPLIER
			self.hitQuality = 0
		elif puckPos.x < STRIKER_AREA_WIDTH + PUCK_RADIUS + STRIKER_RADIUS:
			self.puckInArea = True
		if not self.game.playground:
			if self.goals > self.opponent.goals + 1:
				self.score += self.game.stepTime * WINNING_POINTS_PER_SEC
		
	def getRelativePos(self, pos):
		if self.side == "left":
			return Vector2(pos)
		else:
			return Vector2(FIELD_WIDTH - pos.x, -pos.y)

	def getRelativeVector(self, vector):
		if self.side == "left":
			return Vector2(vector)
		else:
			return Vector2(-vector.x, -vector.y)


	
