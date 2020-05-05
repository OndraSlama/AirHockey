from Constants import *
from pygame.math import Vector2

def u2pX(x):
		return round(u2pDist(x) + X_OFF)

def u2pY(y):
	try:
		return round(u2pDist(-y) + Y_OFF)
	except:
		print('NaN!')
		return 0

def u2pDist(distance):
	return round(distance * UNITS_TO_PIXELS_SCALE)

def p2uX(x):
		return p2uDist(x - X_OFF)

def p2uY(y):
	return p2uDist(-(y - Y_OFF))

def p2uDist(distance):
	return distance / UNITS_TO_PIXELS_SCALE

#----------------------------- Airhockey Motor simulation functions -----------------------------
def getValueInXYdir(dir_x, dir_y, value):
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

	return Vector2([round(-dir_0 + dir_1, 1), round(-dir_0 - dir_1, 1)])


def isDecelerating(vx_real,vy_real, vx_desired,vy_desired): # returns true if both motors are decelerating
	FLUCTUATION_DEVIATION = 1

	def motorDecelerating(v_real, v_desired):

		def oppositeSigns(x, y): 
			return ((int(x) ^ int(y)) < 0)

		if (abs(v_desired) < FLUCTUATION_DEVIATION):# due to fluctuation of regulator (tuhle podminku asi nebudes potrebovat, ale ja ji tam musim mit, tak to kdyztak smaz)        
			return True
		if oppositeSigns(v_real, v_desired):        # desired speed has opposite direction
			return True
		elif (abs(v_desired) < abs(v_real)):     # desired speed has same sign as real but is lower
			return True

		return False

	def xy2motor(vx, vy):
		v0 = -vx - vy
		v1 =  vx - vy
		return v0, v1

    # motor speeds
	v0_real, v1_real = xy2motor(vx_real,vy_real)
	v0_desired, v1_desired = xy2motor(vx_desired,vy_desired)
	if (motorDecelerating(v0_real, v0_desired) and motorDecelerating(v1_real, v1_desired)):
		return True
	else:
		return False

