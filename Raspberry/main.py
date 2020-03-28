from Constants import *
from Strategy import StrategyD
from HelperClasses import FPSCounter, Repeater
import time
from App.AirHockeyApp import AirHockeyApp

def main():
	## Initialize objects -------------
	# camera = Camera()
	# game = Game(camera)
	app = AirHockeyApp()

	## Initialize camera --------------
	# camera.startCamera()
	# camera.lockCameraAwb()
	# camera.calibrateField()
	# camera.analyzeColor()
	# camera.startDetecting()

	# game.start()
	app.run()

	# input("Press Enter to quit...")
	# game.stop()
	# camera.stopDetecting()
	# camera.stopCamera()
	# print("Main program stopped.")



if __name__ == "__main__":
	main()

