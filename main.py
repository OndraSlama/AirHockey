import pygame
from Graphics import Graphics
from Constants import *
from Simulation import Simulation
# Init phase
pygame.init()
clock = pygame.time.Clock()
graphics = Graphics.Graphics(WIDTH, HEIGHT)
sim = Simulation.Simulation()

# Loop variables
lastTextUpdate = 0
running = True
realTime = 0
leftMouseDown = False
rightMouseDown = False
gameSpeed = 1
while running:
	# ----------- TIME SYNCHRONIZATION ------------
	realTime = pygame.time.get_ticks()	
	currentFps = clock.get_fps()
	if not (currentFps == 0):
		sim.stepTime = min(1/currentFps, 0.02)
	else:
		sim.stepTime = 0.02

	if gameSpeed < 1:
		sim.stepTime *= gameSpeed

	# ----------------- EVENTS --------------------
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		if event.type == pygame.MOUSEBUTTONDOWN:	

			if event.button == 1:
				leftMouseDown = True
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
		if leftMouseDown: sim.leftMouseDown(pygame.mouse.get_pos())
		if rightMouseDown: sim.rightMouseDown(pygame.mouse.get_pos())
		sim.step()
	

# ------------------- GRAPHICS ------------------------
	graphics.drawBackgrond()

	# Draw game 
	graphics.drawField()
	graphics.drawPuck([sim.puck.position.x, sim.puck.position.y])
	for striker in sim.strikers:
		graphics.drawStriker([striker.position.x, striker.position.y], GREY)
		

	# Render text
	if realTime - lastTextUpdate > 250:
		graphics.startCreatingTexts()
		graphics.createText("Air Hockey", size=40, alignment="center")
		graphics.createText("Game simulation", line=2, alignment="center")

		graphics.createText("11:4", size=60, line=3, alignment="center")

		graphics.createText(".........................................", line=6, alignment="center")
		graphics.createText("FPS: " + str(round(currentFps, 2)), line=8)
		graphics.createText("Step time: " + str(round(sim.stepTime, 4)))		
		roundDigit = max(min(round(.5/gameSpeed), 3), 1)
		graphics.createText("Game speed: " + str(round(gameSpeed, roundDigit)))
		lastTextUpdate = realTime
	
	# Update graphics (blit everything to screen)
	graphics.update()

	# Set fps
	clock.tick(200)

pygame.quit()
