import pygame
import pygame.gfxdraw
import pygame.math as gameMath
from math import floor
from Constants import *
from Functions import *
from Game.Strategy.StrategyStructs import *



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

	
		
	# def drawAxes(self, redRot, redPos, blueRot, bluePos):
	#	 redAxisPositions = [80, 230, 530, 830]
	#	 blueAxisPositions = [1210 - 80, 1210 - 230, 1210 - 530, 1210 - 830]

	#	 dummyWidth = 21
	#	 dummyThickness = 12
	#	 dummiesOffset = [[0], [119, -119], [238, 119, 0, -119, -238], [208, 0, -208]]

	#	 for i in range(4):
	#		 # red axes
	#		 pygame.draw.line(self.window, RED, (u2pX(redAxisPositions[i]), u2pY(
	#			 -703/2)), (u2pX(redAxisPositions[i]), u2pY(703/2)), 1)
	#		 for dummy in dummiesOffset[i]:
	#			 rect = [u2pX(redAxisPositions[i] + redRot[i] - dummyThickness/2), u2pY(
	#				 redPos[i] + dummy - dummyWidth/2), dummyThickness, dummyWidth]
	#			 pygame.draw.rect(self.window, RED, rect)
	#		 # blue axes
	#		 pygame.draw.line(self.window, BLUE, (u2pX(blueAxisPositions[i]), u2pY(
	#			 -703/2)), (u2pX(blueAxisPositions[i]), u2pY(703/2)), 1)
	#		 for dummy in dummiesOffset[i]:
	#			 rect = [u2pX(blueAxisPositions[i] + blueRot[i] - dummyThickness/2),
	#					 u2pY(bluePos[i] + dummy - dummyWidth/2), dummyThickness, dummyWidth]
	#			 pygame.draw.rect(self.window, BLUE, rect)

	# def drawRealAxes(self, redRot, redPos, blueRot, bluePos):
	#	 redAxisPositions = [80, 230, 530, 830]
	#	 blueAxisPositions = [1210 - 80, 1210 - 230, 1210 - 530, 1210 - 830]

	#	 dummyWidth = 21
	#	 dummyThickness = 12
	#	 dummiesOffset = [[0], [119, -119],
	#					  [238, 119, 0, -119, -238], [208, 0, -208]]

	#	 for i in range(4):
	#		 # red axes
	#		 for dummy in dummiesOffset[i]:
	#			 rect = [u2pX(redAxisPositions[i] + redRot[i] - dummyThickness/2), u2pY(
	#				 redPos[i] + dummy - dummyWidth/2), dummyThickness, dummyWidth]
	#			 pygame.draw.rect(self.window, RED, rect, 1)
	#		 # blue axes
	#		 for dummy in dummiesOffset[i]:
	#			 rect = [u2pX(blueAxisPositions[i] + blueRot[i] - dummyThickness/2),
	#					 u2pY(bluePos[i] + dummy - dummyWidth/2), dummyThickness, dummyWidth]
	#			 pygame.draw.rect(self.window, BLUE, rect, 1)

	def drawCamera(self, pos):
		pygame.gfxdraw.aacircle(self.window, u2pX(pos.x), u2pY(pos.y), u2pDist(PUCK_RADIUS), RED)

	def drawHistory(self, history):
		for pos in history:
			self.drawCircle(pos, PUCK_RADIUS/10, YELLOW)

	def drawStrategy(self, strategy, color = GREEN):
		for puck in strategy.puckHistory:
			
			if puck.state == 3:
				historyColor = RED
			else:
				historyColor = GREEN
			self.drawCircle(puck.position, PUCK_RADIUS/10, historyColor)

		if strategy.puck.state == 1:
			for line in strategy.puck.trajectory:			
				self.drawLine(line.start, line.end, DIMMED_RED)

		# draw line to goal
		self.drawLine(strategy.lineToGoal.start, strategy.lineToGoal.end, DIMMED_RED)

		# draw desired position
		self.drawCircle(strategy.striker.desiredPosition, STRIKER_RADIUS/10, GREY)

		# DEBUG
		# if len(strategy.puck.trajectory) > 0:
		# 	trajectoryVector = strategy.puck.trajectory[-1].end - strategy.puck.trajectory[-1].start
		# 	vector = gameMath.Vector2(-trajectoryVector.y, trajectoryVector.x)
		# 	vector.scale_to_length(200)
		# 	secondPoint = strategy.striker.position + vector
		# 	line = Line(strategy.striker.position, secondPoint)
		# 	self.drawLine(line.start, line.end, DIMMED_RED)
		# 	point = strategy.getIntersectPoint(strategy.puck.trajectory[-1], line)
		# 	self.drawCircle(point, STRIKER_RADIUS/10, GREY)

		# line1 = Line(gameMath.Vector2(300, -200), gameMath.Vector2(700, 200))
		# line2 = Line(gameMath.Vector2(400, 200), gameMath.Vector2(600, -250))
		# point1 = strategy.getIntersectPoint(line1, line2)
		# self.drawLine(line1.start, line1.end, YELLOW)
		# self.drawLine(line2.start, line2.end, YELLOW)
		# self.drawCircle(point1, STRIKER_RADIUS/10, YELLOW)


	def drawPuck(self, pos):
		self.drawLine((0, pos.y), (FIELD_WIDTH, pos.y), DIMMED_RED)
		self.drawLine((pos.x, FIELD_HEIGHT/2), (pos.x, -FIELD_HEIGHT/2), DIMMED_RED)
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
		

	# def drawRealBall(self, pos):
	#	 pygame.gfxdraw.aacircle(self.window, u2pX(
	#		 pos.x), u2pY(pos.y), 18, YELLOW)

	# def drawHistory(self, positions):
	#	 for i in range(len(positions)):
	#		 # pygame.draw.circle(self.window, ORANGE, (u2pX(ballPos[0]), u2pY(ballPos[1])), 4, 0)
	#		 pygame.gfxdraw.aacircle(self.window, u2pX(
	#			 positions[i][0]), u2pY(positions[i][1]), 2, ORANGE)
	#		 pygame.gfxdraw.filled_circle(self.window, u2pX(
	#			 positions[i][0]), u2pY(positions[i][1]), 2, ORANGE)

	#		 if i < len(positions) - 1:
	#			 pygame.draw.aaline(self.window, ORANGE, (u2pX(positions[i][0]), u2pY(
	#				 positions[i][1])), (u2pX(positions[i + 1][0]), u2pY(positions[i + 1][1])))

	# def drawTrajectory(self, start, trajectory):
	#	 pygame.draw.aaline(self.window, RED, (u2pX(start[0]), u2pY(
	#		 start[1])), (u2pX(trajectory[0]), u2pY(trajectory[1])))

	# def drawStrategy(self, redIntersect, desiredIntercept):
	#	 redAxisPositions = [80, 230, 530, 830]

	#	 for i in range(4):
	#		 pygame.gfxdraw.filled_circle(self.window, u2pX(
	#			 redAxisPositions[i]), u2pY(desiredIntercept[i]), 3, RED)
	#		 pygame.gfxdraw.aacircle(self.window, u2pX(
	#			 redAxisPositions[i]), u2pY(desiredIntercept[i]), 3, RED)

	#		 pygame.gfxdraw.filled_circle(self.window, u2pX(
	#			 redAxisPositions[i]), u2pY(redIntersect[i]), 2, YELLOW)
	#		 pygame.gfxdraw.aacircle(self.window, u2pX(
	#			 redAxisPositions[i]), u2pY(redIntersect[i]), 2, YELLOW)

	# def drawSlider(self, portion):
	#	 rect = [u2pX(0), u2pY(703/2 + 10), 1210, 15]
	#	 pygame.draw.rect(self.window, CYAN, rect, 1)

	#	 rect = [u2pX(0), u2pY(703/2 + 10), 1210*portion, 15]
	#	 pygame.draw.rect(self.window, CYAN, rect, 0)
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

	# def fillColumn(self, string, size = TEXT_SIZE, color = WHITE, line = None, column = 0, alignment = "topleft")
	# 	if line is None: line = self.index	
	# 	x = self.textColumnPos[column] + round(COLUMN_SIZE/2)
	# 	y = self.textLinePos[line] + round(size/2)

	# 	self.index = line + 1	

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
