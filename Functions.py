from Constants import *
from pygame.math import Vector2
from UniTools import *
from numpy import sign

def u2pX(x):
		return round(u2pDist(x) + X_OFF)

def u2pY(y):
	try:
		return round(u2pDist(-y) + Y_OFF)
	except:
		print('NaN!')
		return 0

def u2pXY(pos):
	pos = toList(pos)
	return (u2pX(pos[0]), u2pY(pos[1]))

def u2pDist(distance):
	return round(distance * UNITS_TO_PIXELS_SCALE)

def p2uX(x):
		return p2uDist(x - X_OFF)

def p2uY(y):
	return p2uDist(-(y - Y_OFF))

def p2uXY(pos):
	pos = toList(pos)
	return (p2uX(pos[0]), p2uY(pos[1]))

def p2uDist(distance):
	return distance / UNITS_TO_PIXELS_SCALE

#----------------------------- Airhockey Motor simulation functions -----------------------------

def getAccelInXYdir(vx_desired, vy_desired, vx_real, vy_real, accel, decel):
    # dir_x = x-component of vector
    # dir_y = y-component of vector
    # returns: x and y components limited by max_values

	def pickAccels(vx_desired, vy_desired, vx_real, vy_real):
		v0_desired, v1_desired = xy2motor(vx_desired, vy_desired)
		v0_real, v1_real = xy2motor(vx_real, vy_real)
		isDecelerating = [isMotorDecelerating(v0_desired, v0_real), isMotorDecelerating(v1_desired, v1_real)]
		return map(lambda isDecel: decel if isDecel else accel, isDecelerating)

	def isMotorDecelerating(vm_desired, vm_real):
		#if (abs(v_desired) < FLUCTUATION_DEVIATION):# due to fluctuation of regulator (tuhle podminku asi nebudes potrebovat, ale ja ji tam musim mit, tak to kdyztak smaz)
		#    return True
		if oppositeSigns(vm_real, vm_desired):        # desired speed has opposite direction
			return True
		elif abs(vm_desired) < abs(vm_real):     # desired speed has same sign as real but is lower
			return True

		return False

	max_value_0, max_value_1 = pickAccels(vx_desired, vy_desired, vx_real, vy_real)
	v0_diff, v1_diff = xy2motor(vx_desired - vx_real, vy_desired - vy_real)
	acc0, acc1 = scaleToMaxMotorValues(v0_diff, v1_diff, max_value_0, max_value_1)
	accx, accy = motor2xy(acc0, acc1)
	return Vector2(accx, accy)

def getSpeedInXYdir(vx, vy, max_speed):
    v0, v1 = xy2motor(vx, vy)
    maxv0, maxv1 = scaleToMaxMotorValues(v0, v1, max_speed)
    maxvx, maxvy = motor2xy(maxv0, maxv1)
    return Vector2(maxvx, maxvy)

def scaleToMaxMotorValues(v0_diff, v1_diff, max_value_0, max_value_1= None):
    if max_value_1 is None:
        max_value_1 = max_value_0

    try:
        multiplier0 = max_value_0 / abs(v0_diff)
        multiplier1 = max_value_1 / abs(v1_diff)
        multiplier = min(multiplier0, multiplier1)  # pick smaller multiplier
        acc0, acc1 = v0_diff * multiplier, v1_diff * multiplier  # converts speed diff to acceleration in interval (-max_value, +max_value) respecting ratios
    except:
        acc0 = sign(v0_diff) * max_value_0 if v0_diff != 0 else 0
        acc1 = sign(v1_diff) * max_value_1 if v1_diff != 0 else 0
        #print(f"one of motors has zero speed diff, returning {acc0} , {acc1}")

    return acc0,acc1

def xy2motor(v_x, v_y):
    v0 = -v_x - v_y
    v1 =  v_x - v_y
    return v0, v1

def motor2xy(v0, v1):
    vx = 0.5*(-v0 + v1)
    vy = 0.5*(-v0 - v1)
    return vx, vy



# def getValueInXYdir(dir_x, dir_y, value):
# 	if dir_x == 0 and dir_y == 0:
# 		return Vector2([value/2, value/2])

# 	def map(val, in_min, in_max, out_min, out_max): # maps from interval to other interval
# 		return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
# 	# dir_x = vektor rychlosti x
# 	# dir_y = vektor rychlosti y
# 	dir_0 = -dir_x - dir_y
# 	dir_1 = dir_x - dir_y
# 	absdir_0 = abs(dir_0)
# 	absdir_1 = abs(dir_1)
# 	bigger = absdir_0 if absdir_0 > absdir_1 else absdir_1

# 	absdir_0 = map(absdir_0 , 0 , bigger, 0, value/2)
# 	absdir_1 = map(absdir_1 , 0 , bigger, 0, value/2)

# 	dir_0 = absdir_0 if dir_0>=0 else -absdir_0
# 	dir_1 = absdir_1 if dir_1>=0 else -absdir_1

# 	return Vector2([round(-dir_0 + dir_1, 1), round(-dir_0 - dir_1, 1)])


def isDecelerating(vx_real,vy_real, vx_desired,vy_desired): # returns true if both motors are decelerating
	FLUCTUATION_DEVIATION = 1

	def motorDecelerating(v_real, v_desired):		

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

