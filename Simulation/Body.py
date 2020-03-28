from pygame.math import Vector2
from Constants import *
from HelperClasses import Line

class Body():
	def __init__(self, sim, x, y, r, m=20): # m = 0 -> m=infinity
		self.simulation = sim
		self.position = Vector2(x, y)
		self.lastPosition = Vector2(x, y)
		self.velocity = Vector2(0, 0)
		self.acceleration = Vector2(0, 0)
		self.force = Vector2(0, 0)
		self.radius = r
		self.mass = m
		self.postContact = self.postContactInit
		if m == 0:
			self.invMass = 0
		else:
			self.invMass = 1/m

	def applyForce(self, force):
		self.force += force

	def resetForce(self):			
		self.force.x = 0
		self.force.y = 0

	def friction(self, magnitude, timeStep):
		# Friction
		velMag = self.velocity.magnitude()
		if not (velMag == 0):
			slope = magnitude/10
			scale = MIN_STEP_TIME / timeStep
			force = self.velocity.normalize() * (velMag * -slope) * scale
			if force.magnitude() > magnitude:
				force.scale_to_length(magnitude)
			self.applyForce(force)

	def move(self, velDamp, timeStep):
		self.lastPosition = Vector2(self.position)
		self.position += self.velocity * timeStep
		self.velocity += self.acceleration * timeStep
		self.velocity *= velDamp
		if not (self.mass == 0):
			self.acceleration = self.force / self.mass
		self.resetForce()		
		
		self.friction(FRICTION_MAG, self.simulation.stepTime)
		self.bounce(0.8, self.simulation.boundaries)

	def followPos(self, position):
		vel = 20*(position - self.position)

		if vel.magnitude() > 10000:
			vel.scale_to_length(10000)

		acc = (vel - self.velocity)/self.simulation.stepTime	
		self.acceleration = acc

	def intersectsLine(self, line):
		if line.getPointLineDist(self.position) < self.radius:
			if line.getPointSegmentDist(self.position) < self.radius:
				return True
		return False

	def bounceFromLine(self, line, damp = 1):
		# print("------")
		# print(self.position)
		# print(self.velocity)
		# print("-->")
		if self.velocity == Vector2(0,0): return
		if line.getNormalVectorToPoint(self.position).dot(self.velocity) >= 0: return		
		overlap = self.radius - line.getPointSegmentDist(self.position)
		prevPos = Vector2(self.position)
		prevSide = line.getPointSide(self.lastPosition)
		while overlap > 0:
			step = Vector2(-self.velocity)
			step.scale_to_length(self.radius/10)
			self.position += step
			overlap = self.radius - line.getPointSegmentDist(self.position)		

		if line.isOnSegment(line.getPerpendicularPoint(self.position)):			
			self.velocity.reflect_ip(line.getNormalVector())
			self.velocity *= damp
		else:
			self.position = prevPos
			point = line.getClosestSegmentEnd(self.position)
			self.resolveCollision(STRIKER_RESTITUTION, Body(self.simulation, point.x, point.y, self.radius/100, 0))
			# print(self.position)
			# print(self.velocity)
		
		
	def bounce(self, damp, boundaries):
		# Define bounce lines
		bounceLines = []
		for i in range(len(boundaries) - 1):
			bounceLines.append(Line(boundaries[i], boundaries[i+1]))
		bounceLines.append(Line(boundaries[-1], boundaries[0]))

		# Bounce from them
		for line in bounceLines:
			if self.intersectsLine(line):
				self.bounceFromLine(line, damp)


		# ----------- Position corection -----------            
		percent = 0.8 # usually 20% to 80%
		slop = 0.03 # usually 0.01 to 0.1

		# Top
		if self.position.y + self.radius > FIELD_HEIGHT/2: 
			if self.velocity.y > 0:
				self.velocity.y = -self.velocity.y * damp				
			penetration = max(self.position.y - (FIELD_HEIGHT/2 - self.radius), 0)
			correctionMag = max(penetration - slop*self.radius, 0) * percent
			self.position.y -= correctionMag

		# Bottom
		if self.position.y - self.radius < -FIELD_HEIGHT/2:
			if self.velocity.y < 0:
				self.velocity.y = -self.velocity.y * damp
			penetration = max(-(self.position.y - self.radius - -FIELD_HEIGHT/2), 0)
			correctionMag = max(penetration - slop*self.radius, 0) * percent
			self.position.y += correctionMag

		# Left
		if (self.position.x < 0 + self.radius) and abs(self.position.y) > GOAL_SPAN/2:
			if (self.velocity.x < 0):
				self.velocity.x = -self.velocity.x * damp
			penetration = max(self.radius - self.position.x, 0)
			correctionMag = max(penetration - slop*self.radius, 0) * percent
			self.position.x += correctionMag

		# Right
		if self.position.x > FIELD_WIDTH - self.radius and abs(self.position.y) > GOAL_SPAN/2:
			if (self.velocity.x > 0):
				self.velocity.x = -self.velocity.x * damp
			penetration = max(self.position.x - (FIELD_WIDTH - self.radius), 0)
			correctionMag = max(penetration - slop*self.radius, 0) * percent
			self.position.x -= correctionMag

		

		# # Handle goals
		# if self.position.x > right or (self.position.x < 0):
		# 	# Goal top limit
		# 	if self.position.y + self.radius > goalSpan/2: 
		# 		if self.velocity.y > 0:
		# 			self.velocity.y = -self.velocity.y * damp

		# 	# Goal bottom limit
		# 	if self.position.y - self.radius < -goalSpan/2:
		# 		if self.velocity.y < 0:
		# 			self.velocity.y = -self.velocity.y * damp


	def intersects(self, other):
		d = self.position.distance_squared_to(other.position)
		return (d < ((self.radius + other.radius))**2)

	def resolveCollision(self, restitution, other):
		if self is not other:			
			d = self.position.distance_to(other.position)			
			maxDistanceToOverlap = (self.radius + other.radius)


			#------------ IMPACT --------------     
			# Calculate relative velocity
			rv = other.velocity - self.velocity
			normal = (other.position - self.position).normalize()

			# Calculate relative velocity in terms of the normal direction
			velAlongNormal = rv.dot(normal)

			# Do not resolve if velocities are separating
			if velAlongNormal > 0: return

			# Calculate restitution
			e = restitution

			# Calculate impulse scalar
			j = -(1 + e) * velAlongNormal
			j /= self.invMass + other.invMass

			# Apply impulse
			impulse = normal * j
			self.velocity -= impulse * self.invMass
			other.velocity += impulse * other.invMass

			#------------ FRICTION --------------# 
			# TO DO

			if (d < maxDistanceToOverlap) and (d != 0):
				#------------ POSITION CORECTION --------------#             
				percent = 0.7 # usually 20% to 80%
				slop = 0.02 # usually 0.01 to 0.1
				penetration = maxDistanceToOverlap - d
				correctionMag = max(penetration - slop * maxDistanceToOverlap, 0) / (self.invMass + other.invMass) * percent
				correction = normal * correctionMag

				self.position -= correction * self.invMass
				other.position += correction * other.invMass

			self.postContact(self, other)
			other.postContact(other, self)

	def postContactInit(self, x, y):
		pass
