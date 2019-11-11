from Simulation.Body import Body
from Constants import *

class Puck(Body):
	def __init__(self, sim, x, y, r, m=20):
		super().__init__(sim, x, y, r, m)
		self.position.y = 200
		self.velocity.x = 1000
		self.velocity.y = 800

	def update(self):
		self.friction(FRICTION_MAG, self.simulation.stepTime)
		self.move(VELOCITY_DAMP**(self.simulation.stepTime/0.02), self.simulation.stepTime)
		self.bounce(BORDER_RESTITUTION, FIELD_HEIGHT/2, -FIELD_HEIGHT/2, 0, FIELD_WIDTH, GOAL_SPAN)	