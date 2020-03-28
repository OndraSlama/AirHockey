from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2

class KivyCV(Image):
	def __init__(self, capture, fps, **kwargs):
		Image.__init__(self, **kwargs)
		self.capture = capture
		Clock.schedule_interval(self.update, 1.0 / fps)

	def update(self, dt):
		ret, frame = self.capture.read()
		if ret:
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			faceCascade = cv2.CascadeClassifier("lbpcascade_frontalface.xml")
			faces = faceCascade.detectMultiScale(
				gray,
				scaleFactor=1.1,
				minNeighbors=5,
				minSize=(30, 30),
				flags = cv2.CASCADE_SCALE_IMAGE
			)

			for (x, y, w, h) in faces:
				cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

			buf = cv2.flip(frame, 0).tostring()
			image_texture = Texture.create(
				size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
			image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
			cv2.imshow('Frame', frame)

			cv2.waitkey(1)
			# display image from the texture
			self.texture = image_texture


class OpenCVApp(App):
	def build(self):
		self.capture = cv2.VideoCapture("bandicam 2018-05-29 20-49-22-964.mp4")
		my_camera = KivyCV(capture=self.capture, fps=60)
		return my_camera

	def on_stop(self):
		self.capture.release()


if __name__ == '__main__':
	OpenCVApp().run()