import pygame
import pygame.gfxdraw
from pygame.math import Vector2
from math import floor
from Constants import *
from Functions import *
from UniTools import *
from Strategy.StrategyStructs import *

class AHGraphics(Graphics):
	def __init__(self, title = "Air Hockey", w = 100, h = 100):
		super().__init__(title, w, h)

	def startCreatingTexts(self, textSize = TEXT_SIZE, font = "Arial", color = BLACK, x=0, y=0, lineSize = TEXT_SIZE, columnSize = COLUMN_SIZE, margin = [0,0,0,0]):
		super().startCreatingTexts(textSize, font, color, x, y, lineSize, columnSize, margin)

	def drawField(self):
		rect = [0, FIELD_HEIGHT/2, FIELD_WIDTH, FIELD_HEIGHT]
		self.drawRect(rect, [el * 1.8 for el in GREY])
		self.drawRect(rect, GREY, 4)

		# leftGoalCoords = [u2pX(0), u2pY(GOAL_SPAN/2), u2pX(0), u2pY(-GOAL_SPAN/2)]
		# pygame.draw.line(self.window, WHITE, (leftGoalCoords[0], leftGoalCoords[1]), (leftGoalCoords[2], leftGoalCoords[3]), 5)
		self.drawLine((0, GOAL_SPAN/2), (0, -GOAL_SPAN/2), WHITE,  5)

		# rightGoalCoords = [u2pX(FIELD_WIDTH), u2pY(GOAL_SPAN/2), u2pX(FIELD_WIDTH), u2pY(-GOAL_SPAN/2)]
		self.drawLine((FIELD_WIDTH, GOAL_SPAN/2), (FIELD_WIDTH, -GOAL_SPAN/2), WHITE,  5)

		# pygame.gfxdraw.aacircle(self.window, u2pX(FIELD_WIDTH/2), u2pY(0), u2pDist(50), GREY)
		self.drawCircle((FIELD_WIDTH/2, 0), 50, GREY, 1)
		self.drawLine((STRIKER_AREA_WIDTH, FIELD_HEIGHT/2), (STRIKER_AREA_WIDTH, -FIELD_HEIGHT/2), GREY)
		self.drawLine((FIELD_WIDTH - STRIKER_AREA_WIDTH, FIELD_HEIGHT/2), (FIELD_WIDTH - STRIKER_AREA_WIDTH, -FIELD_HEIGHT/2), GREY)

		# Field chamber
		self.drawPolygon(((0, FIELD_HEIGHT/2), (0, FIELD_HEIGHT/2 - CHAMBER_SIZE), (CHAMBER_SIZE, FIELD_HEIGHT/2)),                                      GREY)
		self.drawPolygon(((0, -FIELD_HEIGHT/2), (0, -FIELD_HEIGHT/2 + CHAMBER_SIZE), (CHAMBER_SIZE, -FIELD_HEIGHT/2)),                                   GREY)
		self.drawPolygon(((FIELD_WIDTH, FIELD_HEIGHT/2), (FIELD_WIDTH, FIELD_HEIGHT/2 - CHAMBER_SIZE), (FIELD_WIDTH - CHAMBER_SIZE, FIELD_HEIGHT/2)),    GREY)
		self.drawPolygon(((FIELD_WIDTH, -FIELD_HEIGHT/2), (FIELD_WIDTH, -FIELD_HEIGHT/2 + CHAMBER_SIZE), (FIELD_WIDTH - CHAMBER_SIZE, -FIELD_HEIGHT/2)), GREY)
	

	def drawCamera(self, pos):
		self.drawLine((0, pos.y), (FIELD_WIDTH, pos.y), DIMMED_RED)
		self.drawLine((pos.x, FIELD_HEIGHT/2), (pos.x, -FIELD_HEIGHT/2), DIMMED_RED)
		self.drawCircle((pos.x, pos.y), PUCK_RADIUS, RED, 1)
		# pygame.gfxdraw.aacircle(self.window, u2pX(pos.x), u2pY(pos.y), u2pDist(PUCK_RADIUS), RED)

	def drawHistory(self, history):
		for pos in history:
			self.drawCircle(pos, PUCK_RADIUS/10, RED)

	def drawStrategy(self, strategy, color = GREEN):
		try:		
			for puck in strategy.puckHistory:
				
				if puck.state == 3:
					historyColor = RED
				else:
					historyColor = GREEN
				self.drawCircle(puck.position, PUCK_RADIUS/10, historyColor)

			if strategy.puck.state == 1:
				for line in strategy.puck.trajectory:	
						self.drawLine(line.start, line.end, RED)
			# draw desired position
			self.drawCircle(strategy.striker.desiredPosition, STRIKER_RADIUS/10, GREEN)
			self.drawLine(strategy.striker.position, strategy.striker.desiredPosition, GREEN)
			# draw predicted
			self.drawCircle(strategy.predictedPosition, STRIKER_RADIUS/10, YELLOW)
			self.drawLine(strategy.puck.position, strategy.predictedPosition, YELLOW)

		except Exception as e:
			print("Could not draw strategy. Error: " + str(e))

		try:
			# DEBUG
			for line in strategy.debugLines:
				self.drawLine(line.start, line.end, DIMMED_YELLOW)	

			for point in strategy.debugPoints:
				if point is None or abs(point.x) > 1000 or abs(point.y) > 1000 :
					pass
				else:
					self.drawCircle(point, 5, DIMMED_YELLOW)
		except:
			pass

	
		
		# if len(strategy.puck.trajectory) > 0:
		# 	dist = strategy.getPointLineDist(strategy.striker.position, strategy.puck.trajectory[0])
		# 	dist = strategy.striker.position.distance_to(strategy.striker.desiredPosition)
		# 	time = dist/MAX_SPEED
		# 	vector = Vector2(strategy.puck.vector) * (strategy.puck.speedMagnitude * time)
		# 	desired = strategy.puck.position + vector * 1
		# 	self.drawCircle(desired, STRIKER_RADIUS/10, YELLOW)


		# # draw line to goal
		# self.drawLine(strategy.lineToGoal.start, strategy.lineToGoal.end, DIMMED_RED)
		# if len(strategy.puck.trajectory) > 0:
		# 	trajectoryVector = strategy.puck.trajectory[-1].end - strategy.puck.trajectory[-1].start
		# 	vector = Vector2(-trajectoryVector.y, trajectoryVector.x)
		# 	vector.scale_to_length(200)
		# 	secondPoint = strategy.striker.position + vector
		# 	line = Line(strategy.striker.position, secondPoint)
		# 	self.drawLine(line.start, line.end, DIMMED_RED)
		# 	point = strategy.getIntersectPoint(strategy.puck.trajectory[-1], line)
		# 	self.drawCircle(point, STRIKER_RADIUS/10, GREY)

		# line1 = Line(Vector2(300, -200), Vector2(700, 200))
		# line2 = Line(Vector2(400, 200), Vector2(600, -250))
		# point1 = strategy.getIntersectPoint(line1, line2)
		# self.drawLine(line1.start, line1.end, YELLOW)
		# self.drawLine(line2.start, line2.end, YELLOW)
		# self.drawCircle(point1, STRIKER_RADIUS/10, YELLOW)

		# line1 = Line(Vector2(600, 0), Vector2(600, 200))
		# point1 = strategy.getBothCoordinates(line1, y = FIELD_HEIGHT/2)
		# self.drawLine(line1.start, line1.end, YELLOW)
		# self.drawCircle(point1, STRIKER_RADIUS/10, YELLOW)	


	#----------------------------- Basic function -----------------------------
	def drawPuck(self, pos):
		self.drawCircle(pos, PUCK_RADIUS, RED)
		self.drawCircle(pos, PUCK_RADIUS * 0.8, DIMMED_RED)
		self.drawCircle(pos, PUCK_RADIUS * 0.7, RED)
		


	def drawStriker(self, pos, robot=False, color=GREY):
		# if robot:
		# 	pygame.draw.line(self.window, [el * 0.6 for el in color], (u2pX(pos.x), u2pY(FIELD_HEIGHT/2)), (u2pX(pos.x), u2pY(-FIELD_HEIGHT/2)), 3)
		self.drawCircle(pos, STRIKER_RADIUS, color)
		self.drawCircle(pos, STRIKER_RADIUS * 0.9,  [el * 0.4 for el in color])
		self.drawCircle(pos, STRIKER_RADIUS * 0.85,  color)
		self.drawCircle(pos, STRIKER_RADIUS * 0.45,  [el * 0.4 for el in color])
		self.drawCircle(pos, STRIKER_RADIUS * 0.4,  color)

	
	#----------------------------- Low level function -----------------------------
	def drawRect(self, _rect, color, thickness = None):
		super().drawRect([u2pX(_rect[0]), u2pY(_rect[1]), u2pDist(_rect[2]), u2pDist(_rect[3])], color, thickness)

	def drawCircle(self, _pos, rad, color, thickness = None):
		super().drawCircle(u2pXY(toList(_pos)), u2pDist(rad), color, thickness)

	def drawPolygon(self, _vertices, color):
		vertices = [u2pXY(point) for point in _vertices]
		super().drawPolygon(vertices, color)	

	def drawLine(self, startPos, endPos, color, thickness = 1):
		super().drawLine(u2pXY(toList(startPos)), u2pXY(toList(endPos)), color, thickness)
		

