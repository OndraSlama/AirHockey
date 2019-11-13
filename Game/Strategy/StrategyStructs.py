import pygame.math as gameMath

# Puck states
ACURATE = 1
INACURATE = 2
USELESS = 3

class StrategyStriker():
	def __init__(self):
		self.position = gameMath.Vector2(0, 0)
		self.velocity = gameMath.Vector2(0, 0)
		self.desiredPosition = gameMath.Vector2(0, 0)


class StrategyPuck():
	def __init__(self, state = USELESS, pos = gameMath.Vector2(0, 0)):
		self.position = pos
		self.velocity = gameMath.Vector2(0, 0)
		self.vector = gameMath.Vector2(0, 0)
		self.speedMagnitude = 0
		self.timeSinceCaptured = 0
		self.trajectory = []
		self.state = state

class Line():
	def __init__(self, startPos = gameMath.Vector2(0, 0), endPos = gameMath.Vector2(0, 0)):
		self.start = gameMath.Vector2(startPos)
		self.end = gameMath.Vector2(endPos)

	def copy(self):
		return Line(self.start, self.end)