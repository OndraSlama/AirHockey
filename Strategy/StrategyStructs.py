# ****************************************************************************** #
# Author: Ondrej Slama
# -------------------

# Zdrojovy kod vytvoreny v ramci projektu robotickeho vzdusneho hokeje - diplomova prace
#  na VUT FSI ustavu automatizace a informatiky v Brne.

# Source code created as a part of robotic air hockey table project - Diploma thesis
# at BUT FME institute of automation and computer science.

# ****************************************************************************** #
from pygame.math import Vector2

# Puck states
ACURATE = 1
INACURATE = 2
USELESS = 3

class StrategyStriker():
	def __init__(self):
		self.position = Vector2(0, 0)
		self.velocity = Vector2(0, 0)
		self.desiredPosition = Vector2(0, 0)
		self.desiredVelocity = Vector2(0, 0)


class StrategyPuck():
	def __init__(self, state = USELESS, pos = Vector2(0, 0)):
		self.position = pos
		self.velocity = Vector2(0, 0)
		self.vector = Vector2(0, 0)
		self.speedMagnitude = 0
		self.angle = 0
		self.timeSinceCaptured = 0
		self.trajectory = []
		self.state = state

class Line():
	def __init__(self, startPos = Vector2(0, 0), endPos = Vector2(0, 0)):
		self.start = Vector2(startPos)
		self.end = Vector2(endPos)

	def copy(self):
		return Line(self.start, self.end)