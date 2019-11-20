from pygame.math import Vector2

class Filter():
	def __init__(self, th, lg, hg):
		self.threshold = th
		self.lowGain = lg
		self.highGain = hg

		self.raw = Vector2(0, 0)
		self.diff = Vector2(0, 0)
		self.addition = Vector2(0, 0)
		self.prevFiltered = Vector2(0, 0)
		self.filtered = Vector2(0, 0)

	def filterData(self, data):
		if isinstance(data, Vector2):
			if data == data:
				self.raw = data		
				self.diff = self.raw - self.prevFiltered

				if self.diff.magnitude_squared() < self.threshold**2:
					self.addition = Vector2(0, 0)
					self.addition.x = (1/self.lowGain * abs(self.diff.x)/self.threshold) * self.diff.x			
					self.addition.y = (1/self.lowGain * abs(self.diff.y)/self.threshold) * self.diff.y			
					# print("Small")
				else:
					self.addition = Vector2(0, 0)
					self.addition.x = 1/self.highGain * self.diff.x
					self.addition.y = 1/self.highGain * self.diff.y
					# print("Big")

				if not isinstance(data, Vector2): self.prevFiltered = Vector2(0, 0)
				self.filtered = self.prevFiltered + self.addition
				self.prevFiltered = Vector2(self.filtered)
			
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
