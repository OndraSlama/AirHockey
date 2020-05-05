# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from UniTools import Repeater, FPSCounter
import time
import cv2
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (320, 192)
camera.framerate = 60
rawCapture = PiRGBArray(camera, size=(320, 192))
# allow the camera to warmup
time.sleep(0.1)

counter = FPSCounter(movingAverage=60).start()
repeater = Repeater(counter.print, 0.5).start()



# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
	# show the frame
	cv2.imshow("Frame", image)
	counter.tick()

	key = cv2.waitKey(1) & 0xFF
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break