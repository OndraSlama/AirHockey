from Simulation.Body import Body
from Constants import *
from pygame.math import Vector2

class Striker(Body):
	def __init__(self, sim, x, y, r, m=100, mode = "AI"):
		super().__init__(sim, x, y, r, m)

		self.desiredVelocity = Vector2(0, 0)
		self.mode = mode

	def update(self):


		self.calculateMovement()
		# self.friction(FRICTION_MAG*50, self.simulation.stepTime)
		self.move(1, self.simulation.stepTime)
		# fieldCorners = []
		# self.bounce(BORDER_RESTITUTION, FIELD_HEIGHT/2, -FIELD_HEIGHT/2, 0, FIELD_WIDTH, GOAL_SPAN)

	def calculateVelocity(self, desiredPos):
		self.desiredVelocity = KP_GAIN*(desiredPos - self.position)

	def calculateMovement(self):	

		if self.mode == "AI":
			maxSpeed = self.getValueInXYdir(self.desiredVelocity.x, self.desiredVelocity.y, MAX_SPEED).magnitude()
			maxAcc = self.getValueInXYdir(self.desiredVelocity.x, self.desiredVelocity.y, MAX_ACCELERATION).magnitude()
		else:
			maxSpeed = self.getValueInXYdir(self.desiredVelocity.x, self.desiredVelocity.y, MAX_SPEED).magnitude()
			maxAcc = self.getValueInXYdir(self.desiredVelocity.x, self.desiredVelocity.y, MAX_ACCELERATION).magnitude()
		
		vel =  Vector2(self.desiredVelocity)

		if vel.magnitude() > maxSpeed:
			vel.scale_to_length(maxSpeed)

		acc = (vel - self.velocity)/self.simulation.stepTime
		
		if acc.magnitude() > maxAcc:
			acc.scale_to_length(maxAcc)
		
		self.acceleration = acc

	def getValueInXYdir(self, dir_x, dir_y, value):
		if dir_x == 0 and dir_y == 0:
			return Vector2([value/2,value/2])
		def map(val, in_min, in_max, out_min, out_max): # maps from interval to other interval
			return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
		# dir_x = vektor rychlosti x
		# dir_y = vektor rychlosti y
		dir_0 = -dir_x - dir_y
		dir_1 = dir_x - dir_y
		absdir_0 = abs(dir_0)
		absdir_1 = abs(dir_1)
		bigger = absdir_0 if absdir_0 > absdir_1 else absdir_1

		absdir_0 = map(absdir_0 , 0 , bigger, 0, value/2)
		absdir_1 = map(absdir_1 , 0 , bigger, 0, value/2)

		dir_0 = absdir_0 if dir_0>=0 else -absdir_0
		dir_1 = absdir_1 if dir_1>=0 else -absdir_1

		return Vector2([round(-dir_0 + dir_1), round(-dir_0 - dir_1)])
