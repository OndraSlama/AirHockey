from pygame.math import Vector2
import time
from threading import Thread

class Filter():
	def __init__(self, th, lg, hg):
		self.threshold = th
		self.lowGain = lg
		self.highGain = hg

		self.raw = Vector2(0, 0)
		self.diff = Vector2(0, 0)
		self.addition = Vector2(0, 0)
		self.prevFiltered = Vector2(0, 0)
		self.filtered = Vector2(0, 0)

	def filterData(self, data):
		if isinstance(data, Vector2):
			if data == data:
				self.raw = data		
				self.diff = self.raw - self.prevFiltered

				if self.diff.magnitude_squared() < self.threshold**2:
					self.addition = Vector2(0, 0)
					self.addition.x = (1/self.lowGain * abs(self.diff.x)/self.threshold) * self.diff.x			
					self.addition.y = (1/self.lowGain * abs(self.diff.y)/self.threshold) * self.diff.y			
					# print("Small")
				else:
					self.addition = Vector2(0, 0)
					self.addition.x = 1/self.highGain * self.diff.x
					self.addition.y = 1/self.highGain * self.diff.y
					# print("Big")

				if not isinstance(data, Vector2): self.prevFiltered = Vector2(0, 0)
				self.filtered = self.prevFiltered + self.addition
				self.prevFiltered = Vector2(self.filtered)
			
		else:
			if data == data:
				if self.prevFiltered != self.prevFiltered: self.prevFiltered = 0
				self.raw = data		
				self.diff = self.raw - self.prevFiltered				
				if abs(self.diff) < self.threshold:
					self.addition = (1/self.lowGain * abs(self.diff)/self.threshold) * self.diff			
				else:
					self.addition = 1/self.highGain * self.diff
				
			
				self.filtered = self.prevFiltered + self.addition		
				self.prevFiltered = self.filtered
			
		return self.filtered

class FPSCounter():
	def __init__(self, movingAverage = 10, updateEvery = 0.2):
		self.currentFps = 0
		self.movingAverageFps = 0
		self.averageFps = 0
		self.counter = Repeater(self.update, updateEvery)

		self.fpsHistory = []
		self.movingAverage = movingAverage

		self.ticks = 0
		self.reset = True

		self.startTime = None
		self.prevTime = 0
	
	def start(self):
		self.startTime = time.time()
		self.counter.start()

		return self

	def stop(self):
		self.counter.stop()

	def update(self):
		if len(self.fpsHistory) > 2:
			self.movingAverageFps = len(self.fpsHistory)/(time.time() - self.fpsHistory[0])
		self.averageFps = self.ticks / (time.time() - self.startTime)
		
		if time.time() - self.prevTime > 1:
			self.reset = True
			self.resetState()

	def resetState(self):
		self.ticks = 0
		self.startTime = time.time()
		self.prevTime = time.time()
		self.currentFps = 0
		self.movingAverageFps = 0
		self.averageFps = 0
		self.fpsHistory = []
					
	def tick(self):
		if self.reset:
			self.resetState()
			self.reset = False
		else:
			self.ticks += 1

			step = time.time() - self.prevTime
			self.prevTime = time.time()
			if step == 0:
				self.currentFps = 0
			else:
				self.currentFps = 1/step

			self.fpsHistory.append(time.time())
			while len(self.fpsHistory) > self.movingAverage:
				self.fpsHistory.pop(0)

			if len(self.fpsHistory) > 2:
				self.movingAverageFps = len(self.fpsHistory)/(time.time() - self.fpsHistory[0])
			self.averageFps = self.ticks / (time.time() - self.startTime)

	def print(self):
		print(self)
	
	def __repr__(self):
		# return ("Curr: " + str(round(self.currentFps, 2)) + "; Avg: " + str(round(self.averageFps, 2)) + "; Last " + self.movingAverage + ": " + str(round(self.movingAverageFps,2)))
		return ("Curr: {0:6} Avg: {1:6} Last {2:2}: {3:6}".format(str(round(self.currentFps, 2)), str(round(self.averageFps, 2)), self.movingAverage, str(round(self.movingAverageFps,2))))

class Repeater():
	def __init__(self, repeatFunction, every = 0.3):
		self.repeatFunction = repeatFunction
		self.repeatEvery = every
		self.stopped = True

	def repeate(self):
		while True:
			self.repeatFunction()
			time.sleep(self.repeatEvery)
			
			if self.stopped:
				print("Repeater stopped.")
				return

	def start(self):
		if self.stopped:
			self.stopped = False
			Thread(target=self.repeate, args=()).start()
			return self

	def stop(self):
		self.stopped = True


