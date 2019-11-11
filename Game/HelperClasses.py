import pygame.math as gameMath

# class strategyBall {
#	 constructor(){
#		 self.radius = BALL_RADIUS
#		 self.position = createVector(0, 0)
#		 self.velocity = createVector(0, 0)
#		 self.vector = createVector(0,0)
#		 self.state = UNKNOWN
#		 self.trajectory = []
#		 self.timeSinceCaptured = b2.timeStep
#	 }
# }

# class Line{
#	 constructor(pos1, pos2){
#		 self.x1 = pos1.x
#		 self.y1 = pos1.y
#		 self.x2 = pos2.x
#		 self.y2 = pos2.y
#	 }

#	 copy(){
#		 return new Line(createVector(self.x1, self.y1), createVector(self.x2, self.y2))
#	 }
# }

# class strategyAxis{
#	 constructor(axis){
#		 self.axis = axis
#		 self.x = axis.relativeX
#		 self.xDisplacement = 0
#		 self.yDisplacement = axis.relativeY
#		 self.desiredIntercept = 0
#		 self.trajectoryIntercept = 0
#		 self.desiredPosition = 0
#		 self.desiredAngle = 0
#		 self.power = 80
#		 self.mode = 0
#	 }	  
# }

class Filter():
	def __init__(self, th, lg, hg):
		self.threshold = th
		self.lowGain = lg
		self.highGain = hg

		self.raw = 0
		self.diff = 0
		self.addition = 0
		self.prevFiltered = 0
		self.filtered = 0

	def filterData(self, data):
		if isinstance(data, pygame.math.Vector2):
			if data == data:
				self.raw = data		
				self.diff = self.raw - self.prevFiltered				
				if abs(self.diff.x) < self.threshold and abs(self.diff.y) < self.threshold:
					self.addition = gameMath.Vector2(0, 0)
					self.addition.x = (1/self.lowGain * abs(self.diff.x)/self.threshold) * self.diff.x			
					self.addition.y = (1/self.lowGain * abs(self.diff.y)/self.threshold) * self.diff.y			
				else:
					self.addition = gameMath.Vector2(0, 0)
					self.addition.x = 1/self.highGain * self.diff.x
					self.addition.y = 1/self.highGain * self.diff.y

				if not isinstance(data, pygame.math.Vector2): self.prevFiltered = gameMath.Vector2(0, 0)
				self.filtered = self.prevFiltered + self.addition
				self.prevFiltered = gameMath.Vector2(self.filtered)
			
		else:
			if data == data:
				if self.prevFiltered != self.prevFiltered: self.prevFiltered = 0
				self.raw = data		
				self.diff = self.raw - self.prevFiltered				
				if abs(self.diff) < self.threshold:
					self.addition = (1/self.lowGain * abs(self.diff)/self.threshold) * self.diff			
				else:
					self.addition = 1/self.highGain * self.diff
				
			
				self.filtered = self.prevFiltered + self.addition		
				self.prevFiltered = self.filtered
			

		return self.filtered
