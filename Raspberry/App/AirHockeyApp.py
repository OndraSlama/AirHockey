import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen

from Camera import Camera
from Game import Game

import numpy as np
import cv2
from datetime import datetime
from random import randint

Window.clearcolor = (1, 1, 1, 1)
Window.size = (1024, 600)
# Window.fullscreen = True
print(kivy.kivy_home_dir)


class RootWidget(BoxLayout):
	camera = Camera(resolution=(320,192), fps=30)
	game = Game(camera)

	setFieldCorners = ListProperty(camera.fieldCorners.tolist())

	# texture = ObjectProperty(None)

	def __init__(self, **kwarks):
		super(RootWidget, self).__init__(**kwarks)
		
		self.initializeCamera()
		
		self.changeScreen("cameraScreen") # Initial screen

		Clock.schedule_interval(self.updateStatusBar, .6)
		Clock.schedule_interval(self.updateColorTheme, 1)
		Clock.schedule_interval(self.updateCamera, 1/15)

	def initializeCamera(self):
		try:
			self.camera.startCamera()
			self.camera.startDetecting()
			self.cameraConnected = True		
		except:
			self.cameraConnected = False
			print("Camera not working, check if connected properly and try again.")

	def changeScreen(self, screenName):
		# Changing screen logic (animation, direction of the slide animation etc.)
		screens = ["playScreen", "settingsScreen", "cameraScreen", "infoScreen"]
		if screens.index(self.ids.screenManager.current) < screens.index(screenName):
			direction = "up"
		else:
			direction = "down"
		
		self.ids.screenManager.transition.direction = direction
		self.ids.screenManager.current = screenName
		for button in self.ids.navigationPanel.children:
			Animation.cancel_all(button, 'size_hint_y')
			anim = Animation(size_hint_y=1, duration=0.5, t="out_back")
			anim.start(button)

		anim = Animation(size_hint_y=1.3, duration=0.5, t="out_back")
		anim.start(self.ids[screenName + "Button"])

	def updateStatusBar(self, *args):
		# Update everything in status bar
		self.dateTimeString = datetime.now().strftime('%d.%m.%Y   %H:%M:%S')
		self.cameraFps = self.camera.counter.movingAverageFps 
		self.detectingFps = self.camera.detectingCounter.movingAverageFps 
		self.gameFrequency = self.game.frequencyCounter.movingAverageFps 

	def updateColorTheme(self, *args):
		# Update color theme of the app to mach currently detected color
		color = self.ids.cameraScreen.colorToDetect
		self.colorTheme = Color(color[0], 1, 1, mode='hsv').rgba
		

			
	def updateCamera(self, *args):

		def cv2kivy(point):
			return (image.x + point[0]/cs.cameraResolution[0] * image.width, image.y + point[1]/cs.cameraResolution[1] * image.height)
		
		# Update camera frame and everything camera can see in cameraScreen
		cs = self.ids.cameraScreen
		image = cs.ids.cameraStream

		if self.ids.screenManager.current == "cameraScreen":
			texture = self.imageToTexture(self.camera.frame)
			color = self.camera.colorToDetect.tolist()
			cs.colorToDetect = [color[0]/180,color[1]/255,color[2]/255 ]

			if texture is not None:
				cs.isConnected = True
				image.texture = texture
				cs.puckPos = cv2kivy(self.camera.pixelPuckPosition)

				kivyField = [cv2kivy(point) for point in self.setFieldCorners]				
				cs.fieldCorners = [item for sublist in kivyField for item in sublist]

				cs.cameraResolution = (self.camera.frame.shape[1], self.camera.frame.shape[0])				
			else:
				cs.isConnected = False
				image = Image(size=(192, 320), source="icons/no-video.png", allow_stretch = False)

	# Helper functions
	def imageToTexture(self, frame):
		# Convert numpy array frame to kivy texture
		texture = None
		if frame is not None:
			texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
			texture.blit_buffer(frame.flatten(), colorfmt='bgr', bufferfmt='ubyte')
		return texture

class AirHockeyApp(App):
	def build(self): 
		return RootWidget()


if __name__ == "__main__":
	AirHockeyApp().run()