from Constants import *

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