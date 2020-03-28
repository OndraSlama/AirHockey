# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
from HelperClasses import FPSCounter
from HelperClasses import Repeater
import cv2
 
class PiVideoStream:
	def __init__(self, resolution=(320, 240), framerate=60):
		# initialize the camera and stream
		self.camera = PiCamera()
		self.camera.resolution = resolution
		self.camera.framerate = framerate
		self.rawCapture = PiRGBArray(self.camera, size=resolution)
		self.stream = self.camera.capture_continuous(self.rawCapture,
			format="bgr", use_video_port=True)
		self.newFrame = False

		self.counter = FPSCounter(movingAverage=60).start()


		# initialize the frame and the variable used to indicate
		# if the thread should be stopped
		self.frame = None
		self.stopped = True

	def start(self):
		# start the thread to read frames from the video stream
		if self.stopped:
			self.stopped = False
			Thread(target=self.update, args=()).start()
			return self
 
	def update(self):
		# keep looping infinitely until the thread is stopped
		print("Camera is running.")
		for f in self.stream:
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			self.frame = f.array
			self.rawCapture.truncate(0)
			self.newFrame = True
			self.counter.tick()
 
			# if the thread indicator variable is set, stop the thread
			# and resource camera resources
			if self.stopped:
				self.stream.close()
				self.rawCapture.close()
				self.camera.close()
				print("Camera stopped.")
				return

	def read(self):
		# return the frame most recently read
		self.newFrame = False
		return self.frame
 
	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
		self.newFrame = False
		self.frame = None
		self.counter.stop()
		

if __name__ == "__main__":
	pass

	piVideo = PiVideoStream()
	piVideo.start()

	repeater = Repeater(piVideo.counter.print, 0.5).start()
