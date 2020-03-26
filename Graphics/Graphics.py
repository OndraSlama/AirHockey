import pygame
import pygame.gfxdraw
from pygame.math import Vector2
from math import floor
from Constants import *
from Functions import *
from Strategy.StrategyStructs import *



class Graphics:
	def __init__(self, w, h):
		self.pixelWidth = w
		self.pixelHeight = h
		self.window = pygame.display.set_mode((self.pixelWidth, self.pixelHeight))
		self.blits = {}
		self.index = 0

		# Set text grid
		self.textLinePos = [i * TEXT_SIZE for i in range(floor(h/TEXT_SIZE))] 
		self.textColumnPos = [i * COLUMN_SIZE for i in range(NO_OF_COLUMNS)]

		pygame.display.set_caption('Air Hockey')

	def drawBackgrond(self):
		# Draw background
		self.window.fill(BLACK)

	def drawField(self):
		rect = [u2pX(0), u2pY(FIELD_HEIGHT/2), FIELD_PIXEL_WIDTH, FIELD_PIXEL_HEIGHT]
		pygame.draw.rect(self.window, GREY, rect, 4)

		leftGoalCoords = [u2pX(0), u2pY(GOAL_SPAN/2), u2pX(0), u2pY(-GOAL_SPAN/2)]
		pygame.draw.line(self.window, BLACK, (leftGoalCoords[0], leftGoalCoords[1]), (leftGoalCoords[2], leftGoalCoords[3]), 5)

		rightGoalCoords = [u2pX(FIELD_WIDTH), u2pY(GOAL_SPAN/2), u2pX(FIELD_WIDTH), u2pY(-GOAL_SPAN/2)]
		pygame.draw.line(self.window, BLACK, (rightGoalCoords[0], rightGoalCoords[1]), (rightGoalCoords[2], rightGoalCoords[3]), 5)

		pygame.gfxdraw.aacircle(self.window, u2pX(FIELD_WIDTH/2), u2pY(0), u2pDist(50), GREY)
		self.drawLine((STRIKER_AREA_WIDTH, FIELD_HEIGHT/2), (STRIKER_AREA_WIDTH, -FIELD_HEIGHT/2), GREY)
		self.drawLine((FIELD_WIDTH - STRIKER_AREA_WIDTH, FIELD_HEIGHT/2), (FIELD_WIDTH - STRIKER_AREA_WIDTH, -FIELD_HEIGHT/2), GREY)

	def drawCamera(self, pos):
		self.drawLine((0, pos.y), (FIELD_WIDTH, pos.y), DIMMED_RED)
		self.drawLine((pos.x, FIELD_HEIGHT/2), (pos.x, -FIELD_HEIGHT/2), DIMMED_RED)
		pygame.gfxdraw.aacircle(self.window, u2pX(pos.x), u2pY(pos.y), u2pDist(PUCK_RADIUS), RED)

	def drawHistory(self, history):
		for pos in history:
			self.drawCircle(pos, PUCK_RADIUS/10, YELLOW)

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
		
	def drawCircle(self, pos, rad, color):
		pygame.gfxdraw.aacircle(self.window, u2pX(pos.x), u2pY(pos.y), u2pDist(rad), color)
		pygame.gfxdraw.filled_circle(self.window, u2pX(pos.x), u2pY(pos.y), u2pDist(rad), color)
	def drawLine(self, startPos, endPos, color):
		pygame.draw.aaline(self.window, color, (u2pX(startPos[0]), u2pY(startPos[1])), (u2pX(endPos[0]), u2pY(endPos[1])))

	# --------------------------------- TEXT STUFF --------------------------------------
	def startCreatingTexts(self):
		self.blits = []
		self.index = 0

	def createText(self, string, size = TEXT_SIZE, color = WHITE, line = None, column = 0, x = None, y = None, alignment = "topleft"):
		if line is None: line = self.index	
		if alignment == "topleft":
			if x is None:  x = self.textColumnPos[column]
			if y is None:  y = self.textLinePos[line]
		elif alignment == "center":
			if x is None:  x = self.textColumnPos[column] + round(COLUMN_SIZE/2)
			if y is None:  y = self.textLinePos[line] + round(size/2)
		else:
			raise Exception("Wrong alignment specification")
			
		myfont = pygame.font.SysFont('Arial', size)
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
