import pygame
from Graphics.Graphics import Graphics
from Constants import *
from Simulation import Simulation
from Game.Game import Game
# Init phase
pygame.init()
clock = pygame.time.Clock()
graphics = Graphics(WIDTH, HEIGHT)
game = Game()

# Loop variables
lastTextUpdate = 0
running = True
realTime = 0
leftMouseDown = False
middleMouseDown = False
rightMouseDown = False
gameSpeed = 1
while running:
	# ----------- TIME SYNCHRONIZATION ------------
	realTime = pygame.time.get_ticks()	
	currentFps = clock.get_fps()
	if not (currentFps == 0):
		stepTime = min(1/currentFps, 0.02)
	else:
		stepTime = 0.02

	if gameSpeed < 1:
		stepTime *= gameSpeed

	# ----------------- EVENTS --------------------
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		if event.type == pygame.MOUSEBUTTONDOWN:	

			if event.button == 1:
				leftMouseDown = True
			if event.button == 2:
				middleMouseDown = True
			if event.button == 3:
				rightMouseDown = True
			if event.button == 4:
				if gameSpeed < 1: 
					gameSpeed *= 1.2 
				else: 
					gameSpeed = round(gameSpeed) + 1
			if event.button == 5:
				if gameSpeed <= 1: 
					gameSpeed *= 1/1.2 
				else: 
					gameSpeed = round(gameSpeed) - 1

			if gameSpeed > 1:
				gameSpeed = round(gameSpeed)

		if event.type == pygame.MOUSEBUTTONUP:
			leftMouseDown = False
			middleMouseDown = False
			rightMouseDown = False

		if event.type == pygame.MOUSEMOTION:
			pass
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				pass

	keys = pygame.key.get_pressed()  # currently pressed keys

	if keys[pygame.K_LEFT]:
		pass

# --------------------- GAME --------------------------

	for i in range(max(1, gameSpeed)):
		if leftMouseDown: game.simulation.leftMouseDown(pygame.mouse.get_pos())
		if middleMouseDown: game.simulation.middleMouseDown(pygame.mouse.get_pos())
		if rightMouseDown: game.simulation.rightMouseDown(pygame.mouse.get_pos())
		game.update(stepTime)
	

# ------------------- GRAPHICS ------------------------
	graphics.drawBackgrond()

	# Draw game 
	graphics.drawField()
	graphics.drawPuck(game.simulation.puck.position)
	graphics.drawCamera(game.camera.puckPosition)
	graphics.drawHistory(game.camera.positionHistory)
	graphics.drawStrategy(game.leftStrategy)

	for striker in game.simulation.strikers:
		graphics.drawStriker(striker.position, GREY)
		

	# Render text
	if realTime - lastTextUpdate > 250:
		graphics.startCreatingTexts()
		graphics.createText("Air Hockey", size=40, alignment="center")
		graphics.createText("Game simulation", line=2, alignment="center")

		graphics.createText(str(game.score[0]) + ":" + str(game.score[1]), size=60, line=3, alignment="center")

		graphics.createText(".........................................", line=6, alignment="center")
		graphics.createText("FPS: " + str(round(currentFps, 2)), line=8)
		graphics.createText("Step time: " + str(round(game.simulation.stepTime, 4)))		
		roundDigit = max(min(round(.5/gameSpeed), 3), 1)
		graphics.createText("Game speed: " + str(round(gameSpeed, roundDigit)))
		graphics.createText("Real puck speed: " + str(round(game.simulation.puck.velocity.magnitude(), 2)))
		graphics.createText("Captured puck speed: " + str(round(game.leftStrategy.puck.speedMagnitude, 2)))
		graphics.createText("Dangerous puck: " + str(game.leftStrategy.isPuckDangerous()))
		lastTextUpdate = realTime
	
	# Update graphics (blit everything to screen)
	graphics.update()

	# Set fps
	clock.tick(200)

pygame.quit()
