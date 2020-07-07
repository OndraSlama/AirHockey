# ****************************************************************************** #
# Author: Ondrej Slama
# -------------------

# Zdrojovy kod vytvoreny v ramci projektu robotickeho vzdusneho hokeje - diplomova prace
#  na VUT FSI ustavu automatizace a informatiky v Brne.

# Source code created as a part of robotic air hockey table project - Diploma thesis
# at BUT FME institute of automation and computer sience.

# ****************************************************************************** #
import pygame
from pygame.math import Vector2
import math
import numpy as np
from Graphics.Graphics import AHGraphics
from Constants import *
from Functions import *
import pickle
import json
import pickle
import warnings
from datetime import datetime
import cv2

warnings.simplefilter('error')



def main():	 # Main ----------------------------------------------------------------

	#----------------------------- Init -----------------------------
	pygame.init()	
	clock = pygame.time.Clock()
	graphics = AHGraphics('Air Hockey', WIDTH, HEIGHT)

	#----------------------------- Load data -----------------------------
	with open('Recordings/Recording_2020-07-01_18-05-40.obj', 'rb') as f:
		data = pickle.load(f)

	#----------------------------- Frames -----------------------------
	surfaces = []
	for row in data:

		temp = row["frame"]		
		# frame = cv2.perspectiveTransform(row["frame"], row["p2u"])
		if temp is not None:		
			temp = pygame.surfarray.make_surface(temp)
			temp = pygame.transform.rotate(temp, 90)			
			temp = pygame.transform.scale(temp, (FIELD_PIXEL_WIDTH + 100, FIELD_PIXEL_HEIGHT))
		
		surfaces.append(temp)

	#----------------------------- Time fix -----------------------------
	startTime = data[0]["time"]
	for i in range(len(data)):
		data[i]["time"] = data[i]["time"] - startTime
	# 	#----------------------------- Temp data alocation -----------------------------
	# 	time = [row[0] for row in data]
	# 	gameTime = [row[1] for row in data]
	# 	puckPos = [row[2] for row in data]
	# 	puckVel = [row[3] for row in data]
	# 	strikerPos = [row[4] for row in data]
	# 	strikerVel = [row[5] for row in data]
	# 	desiredPos = [row[6] for row in data]
	# 	predictedPos = [row[7] for row in data]
		

	#----------------------------- Loop -----------------------------
	animationSpeed = 1
	historyLength = 40

	frame = 0
	timeReference = 0
	absoluteTime = 0
	lastTextUpdate = 0

	paused = False
	mouseDown = False
	referenceMousePos = [0,0]
	referenceFrame = 0
	running = True
	while running: 
		# ----------------- EVENTS ------------------------
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False   

			if event.type == pygame.MOUSEBUTTONDOWN:
				paused = True
				mouseDown = True
				referenceFrame = frame
				referenceMousePos = pygame.mouse.get_pos()

				if event.button == 4: animationSpeed *= 1.2
				if event.button == 5: animationSpeed *= 1/1.2

				timeReference = absoluteTime - data[frame]["time"]/animationSpeed
				#     pass

			if event.type == pygame.MOUSEBUTTONUP:
				paused = False
				mouseDown = False

			if event.type == pygame.MOUSEMOTION:
				if mouseDown:
					mousePos = pygame.mouse.get_pos()
					frame = referenceFrame + round((mousePos[0] - referenceMousePos[0]) / 1210 * len(data))
					if frame >= len(data): frame = len(data) - 1
					if frame < 0: frame = 0

					timeReference = absoluteTime - data[frame]["time"]/animationSpeed


			if event.type == pygame.KEYDOWN:   
				paused = True

				if event.key == pygame.K_LEFT: 	
					frame -= 1		     
                       
				if event.key == pygame.K_RIGHT: 
					frame += 1	   
					
				if frame >= len(data): frame = len(data) - 1
				if frame < 0: frame = 0  

		keys = pygame.key.get_pressed()  # currently pressed keys
			
		if keys[pygame.K_LEFT]:
			pass
		
	# -------------- Synchronization ---------------------
		realTime = pygame.time.get_ticks()	
		currentFps = clock.get_fps()
		absoluteTime = pygame.time.get_ticks()/1000
		relativeTime = absoluteTime - timeReference
		while relativeTime * animationSpeed > data[frame]["time"]:
			if not paused: 
				frame += 1
			else:
				timeReference = absoluteTime - data[frame]["time"]/animationSpeed
				break     
		
			if frame >= len(data): 
				frame = 0
				timeReference = absoluteTime
				break
		

	# ------------------- GRAPHICS ------------------------
		graphics.drawBackgrond()		

		# Draw game 
		graphics.drawField()

		#----------------------------- Camera -----------------------------
		if surfaces[frame] is not None:
			graphics.window.blit(surfaces[frame], (320, 5))

		graphics.drawPuck(data[frame]["puckPos"])
		# graphics.drawCamera(game.camera.puckPosition)
		graphics.drawHistory([row["puckPos"] for row in data[max(frame - historyLength, 0):frame]])

		# for striker in game.simulation.strikers:
		graphics.drawStriker(data[frame]["strikerPos"], GREY)

		# draw desired position
		graphics.drawCircle(data[frame]["desiredPos"], STRIKER_RADIUS/10, GREEN)
		graphics.drawLine(data[frame]["strikerPos"], data[frame]["desiredPos"], GREEN)
		
		# draw predicted
		graphics.drawCircle(data[frame]["predictedPos"], STRIKER_RADIUS/10, YELLOW)
		graphics.drawLine(data[frame]["puckPos"], data[frame]["predictedPos"], YELLOW)

		# draw line to goal
		graphics.drawLine(data[frame]["puckPos"], [0,0], ORANGE)
		
		# draw trajectory
		for line in data[frame]["trajectory"]:
			graphics.drawLine(line.start, line.end, RED)
		


		graphics.drawSlider(frame/len(data), [10, 720, 360, 15])
			
		# graphics.drawStrategy(game.players[0].strategy)



		# Render text
		if realTime - lastTextUpdate > 250:
			graphics.startCreatingTexts(margin=[10,0,10,0], y=20)
			graphics.createText("Air Hockey", size=40, alignment="center")
			graphics.createText("Game recording visualisation", line=2, alignment="center")
		# 	if PLAYGROUND:
		# 		graphics.createText(str(game.players[0].goals) + ":0", size=60, line=3, alignment="center")
		# 	else:
		# 		graphics.createText(str(game.players[0].goals) + ":" + str(game.players[1].goals), size=60, line=3, alignment="center")

			graphics.createText("·" * 50, alignment="center")
			graphics.createText("FPS: " + str(round(currentFps, 2)))
			graphics.createText("Paused" if paused else "Running")
			roundDigit = max(min(round(.5/animationSpeed), 3), 1)
			graphics.createText("Animation speed: " + str(round(animationSpeed, roundDigit)))

			# graphics.createText("Game time: " + str(round(data[frame]["gameTime"], 2)))
			graphics.createText("Recording time: " + str(round(data[frame]["time"], 2)))
			graphics.createText("")
			graphics.createText("Puck:")
			graphics.createText("Position: " + "x: {:3.0f} y: {:3.0f}".format(*data[frame]["puckPos"]))
			graphics.createText("Speed: " + "x: {:3.0f} y: {:3.0f}".format(*data[frame]["puckVel"]))
			graphics.createText("Speed magnitude: " + "{:3.0f}".format(Vector2(data[frame]["puckVel"]).magnitude()))
			graphics.createText("Predicted position: " + "x: {:3.0f} y: {:3.0f}".format(*data[frame]["predictedPos"]))

			graphics.createText("Frame: " + "{:4.0f} / {:4.0f}".format(frame, len(data)))
		# 	# graphics.createText("Puck speed: " + str(round(game.players[0].strategy.puck.speedMagnitude, 2)))
		# 	graphics.createText("Camera FPS: " + str(game.camera.frameRate))
		# 	graphics.createText("Showing game: " + str(currentGame + 1) + "/"+ str(NUMBER_OF_GAMES))

		# 	graphics.createText(" ")
		# 	graphics.createText("Left player:")
		# 	graphics.createText("‾‾‾‾‾‾‾‾‾‾")
		# 	graphics.createText("Score: " + str(round(game.players[0].score, 2)))
			
		# 	graphics.createText(" ")
		# 	if not PLAYGROUND:
		# 		graphics.createText("Right player:")
		# 		graphics.createText("‾‾‾‾‾‾‾‾‾‾‾‾")
		# 		graphics.createText("Score: " + str(round(game.players[1].score, 2)))

		# 	graphics.createText(" ")
		# 	graphics.createText("Strategy:")
		# 	graphics.createText("‾‾‾‾‾‾‾")
		# 	graphics.createText(game.players[0].strategy.debugString)
		# 	graphics.createText("Goal line intersetion: {}".format(game.players[0].strategy.goalLineIntersection))
		# 	graphics.createText("Puck speed: " + str(round(game.players[0].strategy.puck.speedMagnitude, 2)))
		# 	graphics.createText("Puck vector: {:1.2f}, {:1.2f}".format(game.players[0].strategy.puck.vector.x, game.players[0].strategy.puck.vector.y))
		# 	graphics.createText("Puck angle: {:3.1f}".format(game.players[0].strategy.puck.angle))
		# 	graphics.createText("Dangerous puck: {}".format(game.players[0].strategy.isPuckDangerous()))
		# 	graphics.createText("Puck Behind: {}".format(game.players[0].strategy.isPuckBehingStriker()))
		# 	graphics.createText(" ")
		# 	# graphics.createText("Striker in good position: {}".format(game.players[0].strategy.isInGoodPosition(game.players[0].strategy.lineToGoal)))
		# 	graphics.createText("Striker position: {:3.0f}, {:3.0f}".format(*game.players[0].strategy.striker.position))
		# 	# graphics.createText("Striker velocity: {:3.0f}, {:3.0f}".format(*game.players[0].strategy.striker.velocity))
		# 	# graphics.createText("Striker velocity: {:3.0f}, {:3.0f}".format(*game.players[1].strategy.striker.velocity))
		# 	graphics.createText("Striker speed: {:5.0f}".format(game.players[0].strategy.striker.velocity.magnitude()))
		# 	# graphics.createText("Striker speed: {:3.0f}, {:3.0f}".format(*game.players[0].strategy.opponentStriker.position))


		# 	if MODE == "NE":
		# 		graphics.createText(" ")
		# 		graphics.createText("Neuroevolution:")
		# 		graphics.createText("‾‾‾‾‾‾‾‾‾‾‾‾‾‾")
		# 		graphics.createText("Generation: " + str(population.generation))
		# 		if population.globalBestMember is not None:
		# 			graphics.createText("Best fitness: " + str(population.globalBestMember.absoluteFitness))
		# 		graphics.createText("Brain size: " + str(game.players[0].strategy.brain.size))

		# 	if game.gameDone:
		# 		graphics.createText("Game finished", line=15, column=2, size=100, alignment="center")
		# 	# graphics.createText("Dangerous puck: " + str(game.players[0].strategy.isPuckDangerous()))
			

			# lastTextUpdate = realTime			
		
		# Update graphics (blit everything to screen)
		graphics.update()

		# Set fps
		clock.tick(60)


	pygame.quit()

if __name__ == "__main__":	
	main()
	
