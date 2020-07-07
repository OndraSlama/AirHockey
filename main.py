# ****************************************************************************** #
# Author: Ondrej Slama
# -------------------

# Zdrojovy kod vytvoreny v ramci projektu robotickeho vzdusneho hokeje - diplomova prace
#  na VUT FSI ustavu automatizace a informatiky v Brne.

# Source code created as a part of robotic air hockey table project - Diploma thesis
# at BUT FME institute of automation and computer sience.

# ****************************************************************************** #
import pygame
from Graphics.Graphics import AHGraphics
from Constants import *
from Simulation import Simulation
from Game.Game import Game
from multiprocessing import Pool
from Neuroevolution.Population import Population
from UniTools import *
from numpy import sign
import pickle
import warnings

warnings.simplefilter('error')

# Basic settings. For more, see: Constants.py --------------------

# NE = Neuroevoluting Neural network
# AI = 2 hardcoded strategies againts each other
# vsNN = Learned Neural network vs player
# vsAI = Hardcoded strategy vs player
MODE = "vsAI"

PLAYGROUND = 0
MULTIPROCESS = 0
NUMBER_OF_GAMES = 35
INVARIANT_SIMULATION = 0
LOAD_POPULATION_FROM_FILE = 0

populationsFolder = "Populations/"	
populationToLoad = "games_5-gen_5-score_5970.obj"


def main():	 # Main ----------------------------------------------------------------
	global NUMBER_OF_GAMES

	# Init phase
	if MODE == "vsNN" or MODE == "vsAI": NUMBER_OF_GAMES = 1 
	if MODE == "NE": 
		POPULATION_SIZE = NUMBER_OF_GAMES * 2 
		population = Population(surRatio=1)

	pygame.init()	
	clock = pygame.time.Clock()
	graphics = AHGraphics('Air Hockey', WIDTH, HEIGHT)
	games = [Game(MODE, PLAYGROUND) for i in range(NUMBER_OF_GAMES)]
	# plotter = Plotter(linesNum=2, lastSeconds=20)

	if LOAD_POPULATION_FROM_FILE and MODE == "NE":
		with open(populationsFolder + populationToLoad, 'rb') as file_nn:
			population = pickle.load(file_nn)

		games = createGames(population)
		NUMBER_OF_GAMES = len(games)
	
	if MULTIPROCESS: pool = Pool()

	# Loop variables
	running = True
	paused = False
	lastTextUpdate = 0
	realTime = 0
	leftMouseDown = False
	middleMouseDown = False
	rightMouseDown = False
	if MULTIPROCESS:
		gameSpeed = 200
	else:
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
			#----------------------------- Mouse buttons -----------------------------
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

			#----------------------------- Mouse motion -----------------------------
			if event.type == pygame.MOUSEMOTION:
				pass

			#----------------------------- Key strokes -----------------------------
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					currentGame -= 1
					if currentGame < 0: currentGame = NUMBER_OF_GAMES - 1

				if event.key == pygame.K_RIGHT:
					currentGame += 1
					if currentGame >= NUMBER_OF_GAMES: currentGame = 0

				if event.key == pygame.K_SPACE:
					paused = not paused

		keys = pygame.key.get_pressed()  # currently pressed keys

		if keys[pygame.K_LEFT]:
			pass

	# --------------------- GAME --------------------------
		if not paused:
			mousePos = pygame.mouse.get_pos()

			games[currentGame].leftMouseDown = leftMouseDown
			games[currentGame].middleMouseDown = middleMouseDown
			games[currentGame].rightMouseDown = rightMouseDown

			for game in games:
				game.stepTime = stepTime
				game.gameSpeed = gameSpeed
				game.mousePosition = mousePos
			
			if MULTIPROCESS:
				games = pool.map(work, games)
			else:
				for game in games:
					for i in range(max(1, game.gameSpeed)):
						game.update()

			if MODE == "NE":
				if allGamesFinished(games):
					winnerBrains = [g.players[g.bestScorePlayer] for g in games]
					population.createGeneration(winnerBrains, POPULATION_SIZE)
					population.geneticCycle()

					if population.generation % 100 == 0 and population.generation != 0:
						with open(populationsFolder + 'games_'+ str(round(population.popSize/2)) +'-gen_'+ str(population.generation) + '-score_' + str(round(population.globalBestMember.gameEntity.score)) + '.obj', 'wb') as file_nn:
							pickle.dump(population, file_nn)

					games = createGames(population)

			#----------------------------- Plotter -----------------------------
			# desired = games[currentGame].simulation.strikers[0].desiredVelocity.x
			# plotter.addData([games[currentGame].simulation.strikers[0].velocity.x, sign(desired)* min(abs(desired), MAX_SPEED*2)])
			# plotter.addData([games[currentGame].simulation.strikers[0].acceleration.x, games[currentGame].simulation.strikers[0].acceleration.y])

	# ------------------- GRAPHICS ------------------------
		graphics.drawBackgrond()

		# Draw game 
		game = games[currentGame]
		graphics.drawField()
		graphics.drawPuck(game.simulation.puck.position)
		graphics.drawCamera(game.camera.puckPosition)
		graphics.drawHistory(game.camera.positionHistory)

		for striker in game.simulation.strikers:
			graphics.drawStriker(striker.position, GREY)
			
		graphics.drawStrategy(game.players[0].strategy)

		# Render text
		if realTime - lastTextUpdate > 250:
			graphics.startCreatingTexts(margin=[10,10,10,0])
			graphics.createText("Air Hockey", size=40, alignment="center")
			graphics.createText("Game simulation", line=2, alignment="center")
			if PLAYGROUND:
				graphics.createText(str(game.players[0].goals) + ":0", size=60, line=4, alignment="center")
			else:
				graphics.createText(str(game.players[0].goals) + ":" + str(game.players[1].goals), size=60, line=4, alignment="center")

			graphics.createText("·" * 50, line=6, alignment="center")
			graphics.createText("FPS: " + str(round(currentFps, 2)))
			graphics.createText("Step time: " + str(round(game.simulation.stepTime, 4)))		
			roundDigit = max(min(round(.5/gameSpeed), 3), 1)
			graphics.createText("Game steps per frame: " + str(round(max(gameSpeed, 1), roundDigit)))
			graphics.createText("Game speed: " + str(round((max(gameSpeed, 1)*stepTime) * currentFps, roundDigit)))
			graphics.createText("Game time: " + str(round(game.gameTime, 2)))
			graphics.createText("Puck speed: " + str(round(game.simulation.puck.velocity.magnitude(), 2)))
			# graphics.createText("Puck speed: " + str(round(game.players[0].strategy.puck.speedMagnitude, 2)))
			graphics.createText("Camera FPS: " + str(game.camera.frameRate))
			graphics.createText("Showing game: " + str(currentGame + 1) + "/"+ str(NUMBER_OF_GAMES))

			graphics.createText(" ")
			graphics.createText("Left player:")
			graphics.createText("‾‾‾‾‾‾‾‾‾‾")
			graphics.createText("Score: " + str(round(game.players[0].score, 2)))
			
			graphics.createText(" ")
			if not PLAYGROUND:
				graphics.createText("Right player:")
				graphics.createText("‾‾‾‾‾‾‾‾‾‾‾‾")
				graphics.createText("Score: " + str(round(game.players[1].score, 2)))

			graphics.createText(" ")
			graphics.createText("Strategy:")
			graphics.createText("‾‾‾‾‾‾‾")
			graphics.createText(game.players[0].strategy.debugString)
			graphics.createText("Goal line intersetion: {}".format(game.players[0].strategy.goalLineIntersection))
			graphics.createText("Puck speed: " + str(round(game.players[0].strategy.puck.speedMagnitude, 2)))
			graphics.createText("Puck vector: {:1.2f}, {:1.2f}".format(game.players[0].strategy.puck.vector.x, game.players[0].strategy.puck.vector.y))
			graphics.createText("Puck angle: {:3.1f}".format(game.players[0].strategy.puck.angle))
			graphics.createText("Dangerous puck: {}".format(game.players[0].strategy.isPuckDangerous()))
			graphics.createText("Puck Behind: {}".format(game.players[0].strategy.isPuckBehingStriker()))
			graphics.createText(" ")
			# graphics.createText("Striker in good position: {}".format(game.players[0].strategy.isInGoodPosition(game.players[0].strategy.lineToGoal)))
			graphics.createText("Striker position: {:3.0f}, {:3.0f}".format(*game.players[0].strategy.striker.position))
			# graphics.createText("Striker velocity: {:3.0f}, {:3.0f}".format(*game.players[0].strategy.striker.velocity))
			# graphics.createText("Striker velocity: {:3.0f}, {:3.0f}".format(*game.players[1].strategy.striker.velocity))
			graphics.createText("Striker speed: {:5.0f}".format(game.players[0].strategy.striker.velocity.magnitude()))
			# graphics.createText("Striker speed: {:3.0f}, {:3.0f}".format(*game.players[0].strategy.opponentStriker.position))


			if MODE == "NE":
				graphics.createText(" ")
				graphics.createText("Neuroevolution:")
				graphics.createText("‾‾‾‾‾‾‾‾‾‾‾‾‾‾")
				graphics.createText("Generation: " + str(population.generation))
				if population.globalBestMember is not None:
					graphics.createText("Best fitness: " + str(population.globalBestMember.absoluteFitness))
				graphics.createText("Brain size: " + str(game.players[0].strategy.brain.size))

			if game.gameDone:
				graphics.createText("Game finished", line=15, column=2, size=100, alignment="center")
			# graphics.createText("Dangerous puck: " + str(game.players[0].strategy.isPuckDangerous()))
			

			lastTextUpdate = realTime
		
		# Update graphics (blit everything to screen)
		graphics.update()

		# Set fps
		clock.tick(desiredFps*1.05)

	if MULTIPROCESS:
		pool.close()
		pool.join()

	pygame.quit()

def allGamesFinished(games):
	for game in games:
		if not game.gameDone: return False

	return True

def createGames(population):
	games = []
	for i in range(NUMBER_OF_GAMES):
		games.append(Game(MODE))
		for player in games[i].players:
			player.strategy.brain = population.getDistinctGenom()

	return games

def work(game):
	for i in range(max(1, game.gameSpeed)):
		game.update()	

	return game

if __name__ == "__main__":	
	main()
	
