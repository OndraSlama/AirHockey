import pygame
from Graphics.Graphics import Graphics
from Constants import *
from Simulation import Simulation
from Game.Game import Game
from multiprocessing import Pool

def main():

	# Basic settings. For more, see: Constants.py --------------------

	# NE = Neuroevoluting Neural network
	# AI = 2 hardcoded strategies againts each other
	# vsNN = Learned Neural network vs player
	# vsAI = Hardcoded strategy vs player
	MODE = "AI"

	MULTIPROCESS = False
	NUMBER_OF_GAMES = POPULATION_SIZE
	NUMBER_OF_GAMES = 1
	INVARIANT_SIMULATION = True
	# ----------------------------------------------------------------

	# Init phase
	if MODE == "vsNN" or MODE == "vsAI": NUMBER_OF_GAMES = 1 

	pygame.init()	
	clock = pygame.time.Clock()
	graphics = Graphics(WIDTH, HEIGHT)
	games = [Game(MODE) for i in range(NUMBER_OF_GAMES)]
	
	if MULTIPROCESS: pool = Pool()

	# Loop variables
	running = True
	lastTextUpdate = 0
	realTime = 0
	leftMouseDown = False
	middleMouseDown = False
	rightMouseDown = False
	gameSpeed = 1
	currentGame = 0
	mousePos = None
	while running:
		# ----------- TIME SYNCHRONIZATION ------------
		realTime = pygame.time.get_ticks()	
		currentFps = clock.get_fps()

		if INVARIANT_SIMULATION:
			desiredFps = min(round(1/MIN_STEP_TIME * gameSpeed), 1/MIN_STEP_TIME)
			stepTime = MIN_STEP_TIME
		else:
			desiredFps = 200
			if not (currentFps == 0):				
				stepTime = min(1/currentFps, MIN_STEP_TIME)
			else:
				stepTime = MIN_STEP_TIME

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
					currentGame -= 1
					if currentGame < 0: currentGame = NUMBER_OF_GAMES - 1

				if event.key == pygame.K_RIGHT:
					currentGame += 1
					if currentGame >= NUMBER_OF_GAMES: currentGame = 0

		keys = pygame.key.get_pressed()  # currently pressed keys

		if keys[pygame.K_LEFT]:
			pass

	# --------------------- GAME --------------------------
		mousePos = pygame.mouse.get_pos()

		for game in games:
			game.leftMouseDown = leftMouseDown
			game.middleMouseDown = middleMouseDown
			game.rightMouseDown = rightMouseDown
			game.stepTime = stepTime
			game.gameSpeed = gameSpeed
			game.mousePosition = mousePos
		
		if MULTIPROCESS:
			games = pool.map(work, games)
		else:
			for game in games:
				for i in range(max(1, game.gameSpeed)):
					game.update()
		

	# ------------------- GRAPHICS ------------------------
		graphics.drawBackgrond()

		# Draw game 
		game = games[currentGame]
		graphics.drawField()
		graphics.drawPuck(game.simulation.puck.position)
		graphics.drawCamera(game.camera.puckPosition)
		graphics.drawHistory(game.camera.positionHistory)
		graphics.drawStrategy(game.players[0].strategy)

		for striker in game.simulation.strikers:
			graphics.drawStriker(striker.position, GREY)
			

		# Render text
		if realTime - lastTextUpdate > 250:
			graphics.startCreatingTexts()
			graphics.createText("Air Hockey", size=40, alignment="center")
			graphics.createText("Game simulation", line=2, alignment="center")

			graphics.createText(str(game.players[0].goals) + ":" + str(game.players[1].goals), size=60, line=3, alignment="center")

			graphics.createText("·" * 50, line=6, alignment="center")
			graphics.createText("FPS: " + str(round(currentFps, 2)))
			graphics.createText("Step time: " + str(round(game.simulation.stepTime, 4)))		
			roundDigit = max(min(round(.5/gameSpeed), 3), 1)
			graphics.createText("Game steps per frame: " + str(round(gameSpeed, roundDigit)))
			graphics.createText("Game speed: " + str(round((gameSpeed*stepTime) * currentFps, roundDigit)))
			graphics.createText("Game time: " + str(round(game.gameTime)))
			graphics.createText("Real puck speed: " + str(round(game.simulation.puck.velocity.magnitude(), 2)))
			graphics.createText("Captured puck speed: " + str(round(game.players[0].strategy.puck.speedMagnitude, 2)))
			graphics.createText("Showing game: " + str(currentGame + 1) + "/"+ str(NUMBER_OF_GAMES))

			graphics.createText(" ")
			graphics.createText("Left player:")
			graphics.createText("‾‾‾‾‾‾‾‾‾‾")
			graphics.createText("Score: " + str(round(game.players[0].score, 2)))
			
			graphics.createText(" ")
			graphics.createText("Right player:")
			graphics.createText("‾‾‾‾‾‾‾‾‾‾‾‾")
			graphics.createText("Score: " + str(round(game.players[1].score, 2)))
			# graphics.createText("Dangerous puck: " + str(game.players[0].strategy.isPuckDangerous()))
			

			lastTextUpdate = realTime
		
		# Update graphics (blit everything to screen)
		graphics.update()

		# Set fps
		clock.tick(desiredFps)

	if MULTIPROCESS:
		pool.close()
		pool.join()

	pygame.quit()

def work(game):
	for i in range(max(1, game.gameSpeed)):
		game.update()	

	return game

if __name__ == "__main__":	
	main()
	
