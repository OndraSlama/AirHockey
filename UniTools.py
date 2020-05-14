import pygame
import pygame.gfxdraw
from pygame.math import Vector2
import time
from threading import Thread
from numpy import sign
import matplotlib
import matplotlib.pyplot as plt
from math import floor

#----------------------------- Gandalf's custom filter -----------------------------
class Filter():
	def __init__(self, th, lg, hg, isVector = True):
		self.threshold = th
		self.lowGain = lg
		self.highGain = hg

		if isVector:
			self.raw = Vector2(0, 0)
			self.diff = Vector2(0, 0)
			self.addition = Vector2(0, 0)
			self.prevFiltered = Vector2(0, 0)
			self.filtered = Vector2(0, 0)
		else:
			self.raw = 0
			self.diff = 0
			self.addition = 0
			self.prevFiltered = 0
			self.filtered = 0

	def filterData(self, data, cyclic = None):
		if isinstance(data, Vector2):
			if data == data: # NaN condition
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
			
		elif cyclic is not None:
			if data == data:
				if self.prevFiltered != self.prevFiltered: self.prevFiltered = 0

				flipped = None
				if abs(self.prevFiltered - data) >= cyclic/2:
					flipped = cyclic if self.prevFiltered > data else -1* cyclic
					data += flipped

				self.raw = data		
				self.diff = self.raw - self.prevFiltered				
				if abs(self.diff) < self.threshold:
					self.addition = (1/self.lowGain * abs(self.diff)/self.threshold) * self.diff			
				else:
					self.addition = 1/self.highGain * self.diff
				
			
				self.filtered = self.prevFiltered + self.addition		
				self.prevFiltered = self.filtered

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

#----------------------------- Gandalf's FPS counter -----------------------------
class FPSCounter():
	def __init__(self, movingAverage = 10, updateEvery = 0.2):
		self.currentFps = 0
		self.movingAverageFps = 0
		self.averageFps = 0
		self.counter = Repeater(self.update, updateEvery)
		self.printRepeater = None
		self.printTitle = None

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
		self.unschedulePrint()
		self.resetState()

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

	def schedulePrint(self, every, title = None):
		if self.printRepeater is None:
			self.printTitle = title
			self.printRepeater = Repeater(self.print, every).start()

	def unschedulePrint(self):
		if self.printRepeater is not None:
			self.printRepeater.stop()
			self.printRepeater = None
		

	def print(self):
		if self.printTitle is not None:
			print(self.printTitle)
		print(self)
	
	def __repr__(self):
		# return ("Curr: " + str(round(self.currentFps, 2)) + "; Avg: " + str(round(self.averageFps, 2)) + "; Last " + self.movingAverage + ": " + str(round(self.movingAverageFps,2)))
		return ("Curr: {0:6} Avg: {1:6} Last {2:2}: {3:6}".format(str(round(self.currentFps, 2)), str(round(self.averageFps, 2)), self.movingAverage, str(round(self.movingAverageFps,2))))

#----------------------------- Gandalf's function repeater -----------------------------
class Repeater():
	def __init__(self, repeatFunction, every = 0.3, passStepTime = False):
		self.repeatFunction = repeatFunction
		self.repeatEvery = every
		self.passStepTime = passStepTime
		self.stopped = True
		self.lastStepAt = time.time()
		self.runTime = 0

	def repeate(self):
		
		while True:
			stepTime = time.time() - self.lastStepAt
			self.runTime += time.time() - self.lastStepAt
			self.lastStepAt = time.time()

			if self.passStepTime:
				self.repeatFunction(stepTime)
			else:
				self.repeatFunction()


			sleepTime = self.repeatEvery - (time.time() - self.lastStepAt)
			if sleepTime > 0:
				time.sleep(sleepTime)

			if self.stopped:
				return

	def start(self):
		if self.stopped:
			self.stopped = False
			self.lastStepAt = time.time()
			self.runTime = 0
			Thread(target=self.repeate, args=()).start()
			return self
		else:
			print("Repeater alredy running.")

	
	def stop(self):
		self.stopped = True

#----------------------------- Gandalf's Line math class -----------------------------
class Line():
	def __init__(self, startPos = Vector2(0, 0), endPos = Vector2(0, 0)):
		self.start = Vector2(startPos)
		self.end = Vector2(endPos)

	def copy(self):
		return Line(self.start, self.end)

	def isOnSegment(self, point):
		if point.x < min(self.start.x, self.end.x) or point.x > max(self.start.x, self.end.x):
			return False
		if point.y < min(self.start.y, self.end.y) or point.y > max(self.start.y, self.end.y):
			return False
		return True


	def getVector(self):
		return Vector2(self.end - self.start)

	def getNormalVector(self):
		vector = self.getVector()
		return Vector2(vector.y, -vector.x).normalize()

	def getNormalVectorToPoint(self, point):
		return (point - self.getPerpendicularPoint(point)).normalize()

	def getIntersectPoint(self, line):

		p1 = (self.start.x, self.start.y)
		p2 = (self.end.x, self.end.y)
		p3 = (line.start.x, line.start.y)
		p4 = (line.end.x, line.end.y)
		m1 = self.calculateGradient(p1, p2)
		m2 = self.calculateGradient(p3, p4)
		
		# See if the the lines are parallel
		if (m1 != m2):
			# Not parallel
			
			# See if either line is vertical
			if (m1 is not None and m2 is not None):
				# Neither line vertical
				b1 = self.calculateYAxisIntersect(p1, m1)
				b2 = self.calculateYAxisIntersect(p3, m2)
				x = (b2 - b1) / (m1 - m2)
				y = (m1 * x) + b1
			else:
				# Line 1 is vertical so use line 2's values
				if (m1 is None):
					b2 = self.calculateYAxisIntersect(p3, m2)
					x = p1[0]
					y = (m2 * x) + b2
				# Line 2 is vertical so use line 1's values
				elif (m2 is None):
					b1 = self.calculateYAxisIntersect(p1, m1)
					x = p3[0]
					y = (m1 * x) + b1
				else:
					assert False
					
			return Vector2(x,y)
		else:
			# Parallel lines with same 'b' value must be the same line so they intersect
			# everywhere in this case we return the start and end points of both lines
			# the calculateIntersectPoint method will sort out which of these points
			# lays on both line segments
			b1, b2 = None, None # vertical lines have no b value
			if m1 is not None:
				b1 = self.calculateYAxisIntersect(p1, m1)
			
			if m2 is not None:
				b2 = self.calculateYAxisIntersect(p3, m2)
			
			# If these parallel lines lay on one another   
			if b1 == b2:
				return None # p1,p2,p3,p4
			else:
				return None
	
	def getPointSegmentDist(self, point):
		if self.isOnSegment(self.getPerpendicularPoint(point)):
			return self.getPointLineDist(point)
		else:
			return min(self.start.distance_squared_to(point), self.end.distance_squared_to(point))**0.5
	
	def getClosestSegmentEnd(self, point):
		return Vector2(self.start) if self.start.distance_squared_to(point) < self.end.distance_squared_to(point) else Vector2(self.end)

	def getPointSide(self, point):
		stepFromLine = point - self.getPerpendicularPoint(point)
		return sign(stepFromLine.dot(self.getNormalVector()))


	def getPointLineDist(self, point):
		m = self.calculateGradient(self.start, self.end)
		k = self.calculateYAxisIntersect(self.start, m)

		if m is not None:
			return abs(k + m*point.x - point.y) / (1 + m**2)**0.5
		else:
			return abs(self.start.x - point.x)

	def getBothCoordinates(self, y=None, x = None):
		a = self.calculateGradient(self.start, self.end)
		b = self.calculateYAxisIntersect(self.start, a)

		if a is not None:
			if y is not None:
				if not a==0:
					x = (y - b)/a				
			elif x is not None:
				y = a*x + b
		elif y is not None:
			x = self.start.x
		return Vector2(x, y)

	def getPerpendicularPoint(self, pos):
		vector = self.end - self.start
		perpendiculatVector = Vector2(-vector.y, vector.x)
		# secondPoint = pos + perpendiculatVector

		return self.getIntersectPoint(Line(pos - perpendiculatVector, pos + perpendiculatVector))
	
	def calculateGradient(self, p1, p2):  
		# Ensure that the line is not vertical
		if (p1[0] != p2[0]):
			m = (p1[1] - p2[1]) / (p1[0] - p2[0])
			return m
		else:
			return None

	def calculateYAxisIntersect(self, p, m):
		if m is not None:
   			return  p[1] - (m * p[0])
		else:
			return None

ACTIVATE_PLOTTER = 0
class Plotter():
	def __init__(self, linesNum = 1, lastSeconds = 3):
		self.history = lastSeconds
		self.linesNum = linesNum
		self.repeater = Repeater(self.update, 1/10)		
		self.plotStarted = False
		self.startTime = time.time()		

		self.lines = []
		self.xData = []
		self.yData = []
		self.timestamps = []

		self.prevTimestamps = []

		for i in range(self.linesNum):
			self.xData.append([])
			self.yData.append([])
			self.timestamps.append([])
			self.prevTimestamps.append([])

		if ACTIVATE_PLOTTER:
			self.repeater.start()

		# plt.show()
		# plt.show()

	def addData(self, data):
		for i in range(len(data)):
			if data[i] is not None and i < len(self.lines):
				self.yData[i].append(data[i])
				self.xData[i].append(time.time() - self.startTime)
				self.timestamps[i].append(time.time() - self.startTime)
				
		for i in range(self.linesNum):
			try:
				while self.timestamps[i][0] < self.timestamps[i][-1] - self.history:
					self.yData[i].pop(0)
					self.xData[i].pop(0)
					self.timestamps[i].pop(0)
			except: pass

	def update(self):
		if not self.plotStarted:
			self.fig, self.ax = plt.subplots()
			plt.pause(0.0001)
			plt.ion()	
			plt.xlabel('Time [s]')
			plt.ylabel('Value')	
			plt.grid()	

			for i in range(self.linesNum):
				line, = self.ax.plot([])
				self.lines.append(line)

			self.plotStarted = True
		else:
			for i in range(len(self.lines)):	
				self.lines[i].set_xdata(self.xData[i])		
				self.lines[i].set_ydata(self.yData[i])
			
			try:
				minY = None
				maxY = None
				minX = None
				maxX = None
				changed = False

				for i in range(len(self.lines)):
					minY = min(self.yData[i]) if minY is None or min(self.yData[i]) < minY else minY
					maxY = max(self.yData[i]) if maxY is None or max(self.yData[i]) > maxY else maxY
					minX = min(self.xData[i]) if minX is None or min(self.xData[i]) < minX else minX
					maxX = max(self.xData[i]) if maxX is None or max(self.xData[i]) > maxX else maxX

					if not (self.timestamps[i] == self.prevTimestamps[i]):
						self.prevTimestamps[i] = self.timestamps[i].copy()
						changed = True


				if changed:
					plt.ylim(minY*1.1, maxY*1.1)
					plt.xlim(minX, maxX)
			except:
				pass


			plt.draw()
			plt.pause(0.0001)


#----------------------------- Gandalf's pygame graphics wrapper -----------------------------
# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
DIMMED_RED = (120,60,60)
YELLOW = (255, 255, 0)
DIMMED_YELLOW = (150, 150, 0)
GREEN = (0, 255, 50)
BLUE = (50, 50, 255)
GREY = (100, 100, 100)
ORANGE = (200, 100, 50)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
TRANS = (1, 1, 1)

class Graphics():
	def __init__(self, title, w, h):
		self.pixelWidth = w
		self.pixelHeight = h
		self.window = pygame.display.set_mode((self.pixelWidth, self.pixelHeight))
		pygame.display.set_caption(title)

	def drawBackgrond(self, color=WHITE):
		# Draw background
		self.window.fill(color)
	
	#----------------------------- Low level function -----------------------------
	def drawSlider(self, portion, rect = [0, 0, 100, 10]):		
		pygame.draw.rect(self.window, RED, rect , 1)
		pygame.draw.rect(self.window, RED, [rect[0], rect[1], rect[2]*portion, rect[3]] , 0)

	def drawRect(self, _rect, color, thickness = None):
		if thickness is None:
			pygame.draw.rect(self.window, color, _rect)
		else:
			pygame.draw.rect(self.window, color, _rect, thickness)


	def drawCircle(self, _pos, rad, color, thickness = None):
		pos = toList(_pos)
		if thickness is None:
			pygame.gfxdraw.aacircle(self.window, *pos, rad, color)
			pygame.gfxdraw.filled_circle(self.window, *pos, rad, color)
		elif thickness == 1:
			pygame.gfxdraw.aacircle(self.window, *pos, rad, color)
		else:
			pygame.draw.circle(self.window, color, pos, rad, thickness)

	def drawPolygon(self, _vertices, color):
		pygame.draw.polygon(self.window, color, _vertices)	

	def drawLine(self, startPos, endPos, color, thickness = 1):
		if thickness == 1:
			pygame.draw.aaline(self.window, color, toTuple(startPos), toTuple(endPos))
		else:
			pygame.draw.line(self.window, color, toTuple(startPos), toTuple(endPos), 5)

	# --------------------------------- TEXT STUFF --------------------------------------
	def startCreatingTexts(self, textSize = 10, font = "Arial", color = BLACK, x=0, y=0, lineSize = 10, columnSize = 100, margin = [0,0,0,0]):
		self.blits = []
		self.index = 0

		# Set text grid
		self.textColor = color
		self.textFont = font
		self.x = x
		self.y = y
		self.textSize = textSize
		self.lineSize = lineSize
		self.columnSize = columnSize
		self.margin = margin

	def createText(self, string, size = None, color = None, line = None, column = 0, x = None, y = None, alignment = "topleft"):
		if size is None: size = self.textSize
		if color is None: color = self.textColor
		if line is None: line = self.index	
		if alignment == "topleft":
			if x is None:  x = self.x + self.margin[0] + self.columnSize * column
			if y is None:  y = self.y + self.margin[1] + self.lineSize * line
		elif alignment == "center":
			if x is None:  x = self.x + self.margin[0] + self.columnSize * column + round((self.columnSize - self.margin[0] - self.margin[2])/2)
			if y is None:  y = self.y + self.margin[1] + self.lineSize * line + round((self.lineSize - self.margin[1] - self.margin[3])/2)
		else:
			raise Exception("Wrong alignment specification")
			
		myfont = pygame.font.SysFont(self.textFont, size)
		textsurface = myfont.render(string, False, color)
		textRect = eval("textsurface.get_rect(" + alignment + "=(x, y))")		
		self.blits.append(Text(textsurface, textRect))
		self.index = line + 1	

	def update(self):
		self.drawBlits()
		pygame.display.update()

	def drawBlits(self):
		for blit in self.blits:
			self.window.blit(blit.surface, blit.rect)


class Text():
	def __init__(self, sur, rect):
		self.surface = sur
		self.rect = rect



#----------------------------- Gandalf's Helper Functions -----------------------------
def oppositeSigns(x, y): 
	if x == 0 or y == 0:
		return False
	return x > 0 if y < 0 else x < 0   

def toList(vector, roundDigit = 0):
	if isinstance(vector, Vector2):
		return [round(vector.x, roundDigit), round(vector.y, roundDigit)]
	else:
		return [round(vector[0], roundDigit), round(vector[1], roundDigit)]

def toTuple(vector, roundDigit = 0):
	if isinstance(vector, Vector2):
		return (round(vector.x, roundDigit), round(vector.y, roundDigit))
	else:
		return (round(vector[0], roundDigit), round(vector[1], roundDigit))

def toVector(vector, roundDigit = 0):
	if isinstance(vector, Vector2):
		return Vector2(round(vector.x, roundDigit), round(vector.y, roundDigit))
	else:
		return Vector2(round(vector[0], roundDigit), round(vector[1], roundDigit))

if __name__ == "__main__":
	plotter = Plotter(linesNum=2)
	time.sleep(.4)
	plotter.addData([1, .5])
	plotter.addData([1, 1])
	time.sleep(.4)
	plotter.addData([1, .4])
	time.sleep(.4)
	plotter.addData([1, 2])
	time.sleep(.01)
	plotter.addData([1, -1])
	time.sleep(.01)
	plotter.addData([1, .5])
	plotter.addData([1, 1])
	time.sleep(.01)
	plotter.addData([1, .01])
	time.sleep(.01)
	plotter.addData([1, 2])
	for i in range(100):
		time.sleep(.01)
		plotter.addData([i/10])
	for i in range(100):
		time.sleep(.01)
		plotter.addData([-i/10])
	print(plotter.xData)
