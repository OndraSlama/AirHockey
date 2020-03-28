import cv2
import numpy as np
from threading import Thread
from picamera.array import PiRGBArray
from picamera import PiCamera
from PiVideoStream import PiVideoStream
from HelperClasses import Filter, FPSCounter, Repeater
from pygame.math import Vector2
from Constants import *
import imutils
import time
import random

MAX_PERFORMANCE = 1

PUCK_RADIUS = 20
RESOLUTION_SCALE = 1
DETECT_PUCK = 1
HSV_TRACKBARS = 0
WHITEBALANCE_TRACKBARS = 0
ENABLE_BLURRING = 0

SHOW_DETECTION = 1
SHOW_FPS = 1
SHOW_CAPTURE_INFO = 0
SHOW_MOUSE_HSV = 1
SHOW_MASK = 0
SHOW_FILTERED_MASK = 1


class Camera():

	def __init__(self, resolution = (RESOLUTION_SCALE*320, RESOLUTION_SCALE*192), fps = 65): # 320, 192
		self.piVideo = None
		self.camera = None

		self.detectionStopped = True
		self.analyzingStopped = True
		self.findingFieldStopped = True
		self.lockingAwbStopped = True

		self.resolution = resolution # (X, 0.6*X)
		self.fps = fps # full fov - 40fps, # max around 75 fps

		self.counter = FPSCounter(movingAverage=60).start()
		self.detectingCounter = FPSCounter(movingAverage=60)

		self.frame = None
		self.cursorPosition = None
		self.frameCount = 0

		self.colorToDetect = np.uint8([0, 255, 120])
		self._determineColorIntervals()

		self.fieldCorners = np.float32([[0, 0], [resolution[0], 0], [resolution[0], resolution[1]], [0, resolution[1]]])
		self.p2uTranformMatrix = None
		self.u2pTranformMatrix = None
		self._createTransformMatrices(self.fieldCorners)

		self.newPosition = False
		self.pixelPuckPosition = Vector2(int(0), int(0))
		self.unitPuckPosition = Vector2(0, 0)
		self.unitFilteredPuckPosition = Vector2(0, 0)

		self.filter = Filter(8, 2.2, 1.2)
	
	def lockCameraAwb(self):
		print("Calibrating...")

		# Get auto-set values
		prevAwb_mode = self.camera.awb_mode
		self.camera.awb_mode = "off"
		rg, bg = self.camera.awb_gains
		prevGains = (rg, bg)

		frameCount = 0
		# cv2.namedWindow("Calibrating")
		# cv2.waitKey(1)
		while frameCount < 300:
			if self.piVideo.newFrame:
				self.frame = self.piVideo.read()				
				frameCount += 1

				greenPart = np.repeat(self.frame[:,:,1], 3).reshape(self.frame.shape)
				diffToWhite = (self.frame.astype("int16") - greenPart.astype("int16"))

				if frameCount == 1:

					# Get reference pixels
					vectorized = diffToWhite.reshape((-1,3)).astype("float32")
					K = 8
					attempts = 10
					criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
					ret,label,center=cv2.kmeans(vectorized,K,None,criteria,attempts,cv2.KMEANS_PP_CENTERS)

					labels = label.flatten()
					mostFrequentLabel = np.argmax(np.bincount(labels))
					referenceIndexes = [random.choice(np.argwhere(labels==mostFrequentLabel))[0] for x in range(10)]

					result_mask = (labels == mostFrequentLabel).reshape(self.frame.shape[0], self.frame.shape[1]).astype("uint8")

				# Get reference pixel for current iteration
				referencePixel = diffToWhite.reshape((-1,3))[random.choice(referenceIndexes)] 
				if abs(referencePixel[0]) < 7 and abs(referencePixel[2]) < 7:
					break # If good enough -> break

				# Set white balance iterably
				rg -= referencePixel[2]/500
				bg -= referencePixel[0]/500

				self.camera.awb_gains = (max(min(rg, 8), 0), max(min(bg, 8), 0))

				result_image = cv2.bitwise_and(self.frame, self.frame, mask=result_mask)

				# cv2.imshow("Calibrating", result_image)
				cv2.waitKey(1)
				time.sleep(0.2)

		rg, bg = self.camera.awb_gains
		if rg < 0.1 or bg < 0.1:
			print("Failed to find sufficient gains. Continuing with default ones...")
			self.camera.awb_gains = prevGains
			self.lockingAwbStopped = True
			return

		# cv2.destroyWindow("Calibrating")
		# cv2.waitKey(1)

		print("Set white balance:")
		print([(round(float(rg),1), round(float(bg),1))])
		print("Done.")
		self.lockingAwbStopped = True

	def findField(self):
		# TODO
		self.fieldCorners = self.fieldCorners
		self._calibrateField()
		self.findingFieldStopped = True

	def analyzeColor(self):	
		started = time.time()
		secondLeft = 3
		print("Analyzing most domiant color...")
		print("Saving in: " + str(secondLeft))
		secondLeft -= 1
		while True:
			if self.piVideo.newFrame:
				self.frame = self.piVideo.read()		
				frame = self.frame[round(self.resolution[1]*0.2):round(self.resolution[1]*0.8), round(self.resolution[0]*0.2):round(self.resolution[0]*0.8)]
				frame = cv2.GaussianBlur(frame, (11, 11), 0)
				# cv2.imshow("Analyzing", frame)
				
				if time.time() - started > 1:
					print(secondLeft)
					secondLeft -= 1
					started = time.time()	

				vectorized = frame.reshape((-1,3)).astype("float32")
				K = 3
				attempts = 10
				criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
				ret,label,center = cv2.kmeans(vectorized,K,None,criteria,attempts,cv2.KMEANS_PP_CENTERS)

				labels = label.flatten()
				mostFrequentLabel = np.argmax(np.bincount(labels))

				self.colorToDetect = detectedColor = cv2.cvtColor(np.uint8([[center[mostFrequentLabel]]]),cv2.COLOR_BGR2HSV)[0,0,:]

				# Create a blank 300x300 black image
				foundColorFrame = np.zeros((100, 100 , 3), np.uint8)
				# Fill image with red color(set each pixel to red)
				foundColorFrame[:] = np.uint8([[center[mostFrequentLabel]]])[0,0,:]
				# cv2.imshow("FoundColor", foundColorFrame)

				cv2.waitKey(1)

				if secondLeft == 0:
					print("Saving found color...")
					self._determineColorIntervals()
					break

		# cv2.destroyWindow("Analyzing")
		# cv2.destroyWindow("FoundColor")
		# cv2.waitKey(1)

		print("Found color:")
		print(detectedColor)
		print("Set limits:")
		print(self.lowerLimit, self.upperLimit)

		self.analyzingStopped = True
		print("Done.")

	
	def detectPuck(self):
		if not MAX_PERFORMANCE:
			cv2.namedWindow('Frame')

			if HSV_TRACKBARS:
				cv2.setMouseCallback('Frame', self._mouseHSV)
				cv2.namedWindow("Trackbars")	
				cv2.createTrackbar("Hl", "Trackbars", 0, 179, self._nothing)
				cv2.createTrackbar("Hh", "Trackbars", 0, 179, self._nothing)
				cv2.setTrackbarPos("Hl", "Trackbars", self.lowerLimit[0])
				cv2.setTrackbarPos("Hh", "Trackbars", self.upperLimit[0])
			
			if WHITEBALANCE_TRACKBARS:
				cv2.namedWindow("White balance")	
				cv2.createTrackbar("Red", "White balance", 0, 80, self._nothing)
				cv2.createTrackbar("Blue", "White balance", 0, 80, self._nothing)

		print("Detecting...")
		while True:
			if self.piVideo.newFrame:
				self.frame = self.piVideo.read()
				self.frameCount += 1
				self.counter.tick()

				if ENABLE_BLURRING and not MAX_PERFORMANCE:
					blurred = cv2.GaussianBlur(self.frame, (11, 11), 0)
					frameHSV = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) # not worth
				else:
					frameHSV = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

				if HSV_TRACKBARS and not MAX_PERFORMANCE:
					self.lowerLimit[0] = cv2.getTrackbarPos("Hl", "Trackbars")
					self.upperLimit[0] = cv2.getTrackbarPos("Hh", "Trackbars")

				if DETECT_PUCK:
					if self.lowerLimit[0] > self.upperLimit[0]:
						lowerLimit1 = np.uint8(self.lowerLimit)
						higherLimit1 = np.uint8([179, self.upperLimit[1], self.upperLimit[2]])
						lowerLimit2 = np.uint8([0, self.lowerLimit[1], self.lowerLimit[2]])
						higherLimit2 = np.uint8(self.upperLimit)

						mask1 = cv2.inRange(frameHSV, lowerLimit1, higherLimit1)
						mask2 = cv2.inRange(frameHSV, lowerLimit2, higherLimit2)

						mask = cv2.bitwise_or(mask1, mask2)
					else:
						mask = cv2.inRange(frameHSV, self.lowerLimit, self.upperLimit)

					# perform a series of dilations and erosions to remove any small blobs left in the mask
					filteredMask = cv2.erode(mask, None, iterations=2)
					filteredMask = cv2.dilate(filteredMask, None, iterations=2)
					filtered = cv2.bitwise_and(self.frame, self.frame, mask=filteredMask)
					
					cnts = cv2.findContours(filteredMask.copy(), cv2.RETR_EXTERNAL,
					cv2.CHAIN_APPROX_SIMPLE)
					cnts = imutils.grab_contours(cnts)
					center = None

					# only proceed if at least one contour was found
					if len(cnts) > 0:
						# find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
						c = max(cnts, key=cv2.contourArea)
						((x, y), radius) = cv2.minEnclosingCircle(c)						

						# only proceed if the radius meets a minimum size
						if radius > PUCK_RADIUS / 2 :
							self.detectingCounter.tick()
							self.pixelPuckPosition = Vector2(int(x), int(y))	
							self.unitPuckPosition = self._pixelsToUnits(self.pixelPuckPosition)
							self.unitFilteredPuckPosition = self.filter.filterData(Vector2(self.unitPuckPosition[0], self.unitPuckPosition[1]))							
							self.newPosition = True
				
				if not MAX_PERFORMANCE:
					if SHOW_DETECTION:
						self._drawField(self.fieldCorners)
						self._drawPuck(self.pixelPuckPosition)
						filteredPixelPos = self._unitsToPixels(self.unitFilteredPuckPosition)
						self._drawPuck(filteredPixelPos, color=(0,255,0))
						# self._writeText(str(self.unitPuckPosition), (self.pixelPuckPosition[0] + 10, self.pixelPuckPosition[1] + 10), fontScale=0.5)
						self._writeText(str(self.unitFilteredPuckPosition), (filteredPixelPos[0] + 10, filteredPixelPos[1] + 10), fontScale=0.5)

						# min enclosing circle
						try:
							cv2.circle(self.frame, self.pixelPuckPosition, int(radius), (0, 255, 255), 2)
						except:
							pass

					# Write info to frame
					if SHOW_MOUSE_HSV:
						try:
							self._writeText("HSV: " + str(frameHSV[self.cursorPosition.y, self.cursorPosition.x]))
						except:
							pass			

					if SHOW_FPS:
						self._writeText("FPS: " + str(round(self.counter.movingAverageFps)), position=(10, 60), fontScale=0.6)
					if SHOW_CAPTURE_INFO:
						self._writeText("Exposure: " + str(self.piVideo.camera.exposure_speed), position=(10, 80), fontScale=0.6)
						r,g = self.camera.awb_gains
						self._writeText("AWB Gains: " + str((round(float(r),1), round(float(g),1))), position=(10, 100), fontScale=0.6)
						self._writeText("a/d Gains: " + str((round(float(self.camera.analog_gain),1), round(float(self.camera.digital_gain), 1))), position=(10, 120), fontScale=0.6)

					# Show image
					if SHOW_MASK and DETECT_PUCK:
						cv2.imshow("Mask", mask)

					if SHOW_FILTERED_MASK and DETECT_PUCK:
						cv2.imshow("Filtered mask", filteredMask)

					cv2.imshow("Frame", self.frame)

					if WHITEBALANCE_TRACKBARS:
						rg = cv2.getTrackbarPos("Red", "White balance")/10
						bg = cv2.getTrackbarPos("Blue", "White balance")/10
						self.camera.awb_gains = (rg, bg)

			key = cv2.waitKey(5)	

			if self.detectionStopped:
				print("Detecting stopped.")
				return

		self.piVideo.stop()
		cv2.destroyAllWindows()

	def startCamera(self):
		if self.piVideo is None:
			self.piVideo = PiVideoStream(self.resolution, self.fps)
			self.camera = self.piVideo.camera

		self.piVideo.start()
		print("Warming up...")
		time.sleep(1.0)
		print("Done")

	def stopCamera(self):
		self.detectionStopped = True
		self.analyzingStopped = True
		self.findingFieldStopped = True
		self.lockingAwbStopped = True
		time.sleep(.1)
		
		self.piVideo.stop()
		self.piVideo = None
		self.camera = None

	def startDetecting(self):
		if self.detectionStopped:
			self.detectionStopped = False
			self.detectingCounter.start()
			Thread(target=self.detectPuck, args=()).start()
		else:
			print("Detecting thread already running.")

	def stopDetecting(self):
		self.detectingCounter.stop()
		self.detectionStopped = True	

	def startAnalyzing(self):
		if self.analyzingStopped:
			self.analyzingStopped = False
			Thread(target=self.analyzeColor, args=()).start()
		else:
			print("Analyzing thread already running.")

	def stopAnalyzing(self):
		self.analyzingStopped = True

	def startFindingField(self):
		if self.findingFieldStopped:
			self.findingFieldStopped = False
			Thread(target=self.findField, args=()).start()
		else:
			print("Finding field thread already running.")

	def stopFindingField(self):
		self.findingFieldStopped = True

	def startLockingAwb(self):
		if self.lockingAwbStopped:
			self.lockingAwbStopped = False
			Thread(target=self.lockCameraAwb, args=()).start()
		else:
			print("Locking AWB thread already running.")

	def stopLockingAwb(self):
		self.lockingAwbStopped = True

	def getPuckPosition(self):
		self.newPosition = False
		return self.unitFilteredPuckPosition
	
	def _calibrateField(self):
		# TODO: find the field

		self._createTransformMatrices(self.fieldCorners)		

	def _determineColorIntervals(self):
		hueInterval = 30
		othersInterval = 150

		Hl = self.colorToDetect[0] - hueInterval/2
		if Hl < 0: Hl += 179

		Hh = self.colorToDetect[0] + hueInterval/2
		if Hh > 179: Hh -= 179

		self.lowerLimit = np.uint8([Hl, max(5, self.colorToDetect[1] - othersInterval/2), max(5, self.colorToDetect[2] - othersInterval/2)])
		self.upperLimit = np.uint8([Hh, min(255, self.colorToDetect[1] + othersInterval/2), min(255, self.colorToDetect[2] + othersInterval/2)])

	def _nothing(self, x):
		pass

	def _pixelsToUnits(self, srcPos):	
		srcPos = self._toVector(srcPos)
		src = np.float32([[srcPos.x, srcPos.y]])	
		src = np.array([src])

		out = cv2.perspectiveTransform(src, self.p2uTranformMatrix)
		return Vector2(int(out[0][0][0]), int(out[0][0][1]))

	def _unitsToPixels(self, srcPos):	
		srcPos = self._toVector(srcPos)
		src = np.float32([[srcPos.x, srcPos.y]])	
		src = np.array([src])

		out = cv2.perspectiveTransform(src, self.u2pTranformMatrix)
		return Vector2(int(out[0][0][0]), int(out[0][0][1]))

	def _toTuple(self, vector):
		if isinstance(vector, Vector2):
			return (int(vector.x), int(vector.y))
		else:
			return (int(vector[0]), int(vector[1]))
	
	def _toVector(self, vector):
		if isinstance(vector, Vector2):
			return Vector2(int(vector.x), int(vector.y))
		else:
			return Vector2(int(vector[0]), int(vector[1]))	
		
	def _createTransformMatrices(self, source):
		dst = np.float32([[0, FIELD_HEIGHT/2], [FIELD_WIDTH, FIELD_HEIGHT/2], [FIELD_WIDTH, -FIELD_HEIGHT/2], [0, -FIELD_HEIGHT/2]])
		dst = np.array([dst])

		self.p2uTranformMatrix = cv2.getPerspectiveTransform(source, dst)
		self.u2pTranformMatrix = cv2.getPerspectiveTransform(dst, source)

	def _writeText(self, text, position=(10, 30), fontScale=1, fontColor = (255,255,255)):
		font 		= cv2.FONT_HERSHEY_SIMPLEX
		lineType 	= 2

		cv2.putText(self.frame, text,
			self._toTuple(position), 
			font, 
			fontScale,
			fontColor,
			lineType)
	
	def _drawLine(self, startPoint = (0,10), endPoint = (250, 10), color = (0, 255, 0),  thickness = 2):		
		self.frame = cv2.line(self.frame, self._toTuple(startPoint), self._toTuple(endPoint), color, thickness)

	def _lineHalf(self, startPoint, endPoint):
		x = round((startPoint[0] + endPoint[0])/2)
		y = round((startPoint[1] + endPoint[1])/2)
		return (x, y)

	def _drawPoint(self, center, color = (0, 255, 255), size = 5):
		center = self._toTuple(center)
		cv2.circle(self.frame, center, size, color, -1)
	
	def _drawPuck(self, center, color = (0, 0, 255)):
		center = self._toTuple(center)
		cv2.circle(self.frame, center, PUCK_RADIUS, color, 1)
		cv2.circle(self.frame, center, 2, color, -1)

	def _drawField(self, npPoints, color = (0, 255, 0),  thickness = 3):
		points = [self._toTuple(p) for p in npPoints]

		for i in range(len(points)-1):
			self._drawLine(points[i], points[i + 1])

		self._drawLine(points[3], points[0])

		# Draw field center 
		self._drawLine(self._lineHalf(points[0], points[1]), self._lineHalf(points[2], points[3]), thickness=1)
		self._drawLine(self._lineHalf(points[1], points[2]), self._lineHalf(points[3], points[0]), thickness=1)

	def _mouseHSV(self, event,x,y,flags,param):
		self.cursorPosition = Vector2(x,y)




# piVideo.camera.awb_mode = 'off' # should see green picture.. instead seeing black. First should auto fing the gain vaules and then lock them.
# piVideo.camera.iso = 800 # still dont know
# piVideo.camera.shutter_speed = 567160     # Assign shutter speed to non-zero first. Looks like max is 1/fps * 100000 - makes sense.
# piVideo.camera.exposure_mode = 'off'    # Lock gains and disable auto exposure. if off, way blacker frame :/

if __name__ == "__main__":
	camera = Camera()
	camera.startCamera()

	camera.startLockingAwb()
	while not camera.lockingAwbDone:
		time.sleep(.5)
	
	camera.startFindingField()
	
	while not camera.findingFieldDone:
		time.sleep(.5)
	
	camera.startAnalyzing()

	while not camera.analyzingDone:
		time.sleep(.5)
	
	repeater = Repeater(camera.detectingCounter.print).start()
	camera.startDetecting()
