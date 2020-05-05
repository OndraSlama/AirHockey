from Constants import *
from Strategy import StrategyD
from UniTools import FPSCounter, Repeater
from pygame.math import Vector2
from threading import Thread
import time

class Game():
	def __init__(self, camera):
		self.camera = camera
		self.strategy = StrategyD.StrategyD()

		self.strikersPosition = [Vector2(0,0), Vector2(0,0)]
		self.puckPosition = Vector2(0,0)

		self.frequencyCounter = FPSCounter(60)
		self.infoRepeater = Repeater(self.printToConsole, 0.2)
		self.gameStartedAt = 0
		self.lastStepAt = 0
		self.stopped = True

		self.maxScore = 5
		self.maxTime = 3 * 60

		self.reset()

	def reset(self):
		self.gameTime = 0
		self.score = [0, 0]
		self.gameDone = False
		self.winner = -1

	def update(self):
		print("Game started.")
		while True:
			stepTime = time.time() - self.lastStepAt
			self.lastStepAt = time.time()

			self.step(stepTime)

			sleepTime = 1/MAX_FREQUENCY - (time.time() - self.lastStepAt)
			if sleepTime > 0:
				time.sleep(sleepTime)

			self.gameTime += time.time() - self.lastStepAt

			if self.stopped:
				print("Game stopped.")
				return

	def step(self, stepTime):
		if self.camera.newPosition:
			self.strategy.cameraInput(self.camera.getPuckPosition())

		self.strategy.process(stepTime)	
		self.camera._drawPoint(self.camera._unitsToPixels(self.strategy.striker.desiredPosition))
		self.frequencyCounter.tick()

	def goal(self, side):
		self.score[side] += 1

	def checkEnd(self):
		if max(self.score) >= self.maxScore or self.gameTime >= self.maxTime:
			self.gameDone = True
			if self.score[0] == self.score[1]:
				self.winner = 2
			else:
				self.winner = self.score.index(max(self.score))

	def start(self):
		if self.stopped:
			self.gameStartedAt = time.time()
			self.lastStepAt = time.time()
			self.frequencyCounter.start()
			# self.infoRepeater.start()
			self.stopped = False
			self.reset()
			Thread(target=self.update, args=()).start()
		return self
	
	def resume(self):
		if self.stopped:
			self.frequencyCounter.start()
			self.lastStepAt = time.time()
			# self.infoRepeater.start()
			self.stopped = False
			Thread(target=self.update, args=()).start()

	def pause(self):
		# self.infoRepeater.stop()
		self.stopped = True

	def stop(self):
		self.frequencyCounter.resetState()
		self.frequencyCounter.stop()
		self.pause()
		self.reset()

	def printToConsole(self):
		print("Frequency:")
		print(self.frequencyCounter)
		print("Desired position: " + str(self.strategy.striker.desiredPosition))
