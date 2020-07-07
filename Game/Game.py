# ****************************************************************************** #
# Author: Ondrej Slama
# -------------------

# Zdrojovy kod vytvoreny v ramci projektu robotickeho vzdusneho hokeje - diplomova prace
#  na VUT FSI ustavu automatizace a informatiky v Brne.

# Source code created as a part of robotic air hockey table project - Diploma thesis
# at BUT FME institute of automation and computer sience.

# ****************************************************************************** #
from Constants import *
from Functions import *
from Simulation.Simulation import Simulation
from Game.Player import Player
from Game.Camera import Camera
from Strategy import StrategyA, StrategyB, StrategyC, StrategyD, NN_StrategyA, MovementTest
from Strategy.BaseStrategy import BaseStrategy
from pygame.math import Vector2
from UniTools import Scheduler

class Game():
	def __init__(self, mode, playground):
		self.simulation = Simulation(self, mode, playground)
		self.camera = Camera(self, 70)
		self.mode = mode
		self.playground = playground
		# Players
		#----------------------------- 1st player -----------------------------
		self.players = []
		if mode == "NE" or mode == "vsNN":
			self.players.append(Player(self, NN_StrategyA.NN_StrategyA(), "left"))			
		else:
			self.players.append(Player(self, StrategyC.StrategyC(), "left"))
			# self.players.append(Player(self, MovementTest.MovementTest(), "left"))


		#----------------------------- 2nd player -----------------------------
		if not playground:
			if mode == "vsAI" or mode == "vsNN":
				self.players.append(Player(self, StrategyD.StrategyD(), "right"))
				# self.players.append(Player(self, MovementTest.MovementTest(), "right"))

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

		# Statistic data
		self.onSide = 0
		self.maxShotSpeed = [0, 0]
		self.puckControl = [0, 0]
		self.shotOnGoals = [0, 0]
		self.lostPucks = [0, 0]

	def update(self):
		stepTime = self.stepTime
		mousePos = self.mousePosition
		self.gameTime += stepTime

		if not self.gameDone:
			if self.middleMouseDown: self.simulation.middleMouseDown(mousePos)
			if self.rightMouseDown: self.simulation.rightMouseDown(mousePos)

			self.simulation.step(stepTime)
			self.camera.update()

			for i in range(len(self.players)):
				self.players[i].updatePosition(self.simulation.strikers[i].position)
				if self.camera.newData:
					self.players[i].cameraInput(self.camera.puckPosition)

				self.players[i].update(stepTime)

				if self.leftMouseDown: 
					player = not self.playground
					mouseVec = self.players[player].getRelativePos(Vector2((p2uX(mousePos[0]), p2uY(mousePos[1]))))
					self.players[player].strategy.setDesiredPosition(mouseVec)

				self.simulation.strikers[i].desiredVelocity = self.players[i].getDesiredVelocity()

			self.camera.newData = False



			self.checkData(stepTime)
			self.checkGoal()
			# self.checkEnd()

		return self

	def checkData(self, stepTime):	
		puck = self.players[0].strategy.puck
		puckPos = puck.position
		if puckPos.x > FIELD_WIDTH - (STRIKER_AREA_WIDTH) and not self.onSide == 1:
			self.onSide = 1
			self.checkShot(-1)
			self.lostPucks[0] += 1
			print(self.lostPucks)
			
		elif puckPos.x < STRIKER_AREA_WIDTH and not self.onSide == -1:
			self.onSide = -1
			self.checkShot(1)
			self.lostPucks[1] += 1
		elif abs(puckPos.x - FIELD_WIDTH/2) < (FIELD_WIDTH - 2*(STRIKER_AREA_WIDTH))/2:
			self.onSide = 0

		if not self.onSide == 0:
			self.puckControl[max(0, self.onSide)] += stepTime


		
		

	def checkShot(self, dir):
		print("Puck Control:", self.puckControl)

		puck = self.players[0].strategy.puck
		if puck.speedMagnitude > 700 and abs(puck.vector.y) < .9:
			# print("good shot, dir:", dir)
			if len(puck.trajectory) > 0 and abs(puck.trajectory[-1].end.y) < GOAL_SPAN/2 * .9:
				self.shotOnGoals[max(0, dir)] += 1
				print("Shots on goal: ", self.shotOnGoals)
			if self.maxShotSpeed[max(0, dir)] < puck.speedMagnitude < 10000 :
				self.maxShotSpeed[max(0, dir)] = puck.speedMagnitude
				# print("Max shot speed:", self.maxShotSpeed)

	def checkGoal(self):
		if not self.playground:
			if self.simulation.puck.position.x < 0:
				self.players[1].goals += 1
				self.players[1].score += POINTS_PER_GOAL
				self.simulation.spawnPuck()
				# Scheduler().schedule(self.simulation.spawnPuck, 1)
			if self.simulation.puck.position.x > FIELD_WIDTH:
				self.players[0].goals += 1
				self.players[0].score += POINTS_PER_GOAL
				self.simulation.spawnPuck()
				# Scheduler().schedule(self.simulation.spawnPuck, 1)

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
				