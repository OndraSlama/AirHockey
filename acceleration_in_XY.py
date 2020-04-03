
from pygame.math import Vector2
def accel_in_XY_dir(dir_x, dir_y, max_accel):
	
	def map(val, in_min, in_max, out_min, out_max): # maps from interval to other interval
		return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

	"""
		dir_x = vektor rychlosti x
		dir_y = vektor rychlosti y
		% 
	"""
	dir_0 = -dir_x - dir_y
	dir_1 = dir_x - dir_y
	absdir_0 = abs(dir_0)
	absdir_1 = abs(dir_1)
	bigger = absdir_0 if absdir_0 > absdir_1 else absdir_1

	absdir_0 = map(absdir_0 , 0 , bigger, 0, max_accel/2)
	absdir_1 = map(absdir_1 , 0 , bigger, 0, max_accel/2)

	dir_0 = absdir_0 if dir_0>=0 else -absdir_0
	dir_1 = absdir_1 if dir_1>=0 else -absdir_1

	return [round(-dir_0 + dir_1), round(-dir_0 - dir_1)]



# Examples:
max_accel = 10; # [m/s] set by setaccel,133000
print("Set acceleration: " + str(max_accel))
print("H-bot construction holds property: |a_x| + |a_y| = max_accel\n")

print("Examples:")
[a_x , a_y] = accel_in_XY_dir(10,0, max_accel)
print("Max acceleratin in direction [10, 0] is [{}, {}], Magnitude: {:.0f}".format(a_x, a_y, Vector2(a_x, a_y).magnitude()))
[a_x , a_y] = accel_in_XY_dir(100,100, max_accel)
print("Max acceleratin in direction [100, 100] is [{}, {}], Magnitude: {:.0f}".format(a_x, a_y, Vector2(a_x, a_y).magnitude()))
[a_x , a_y] = accel_in_XY_dir(0,-50, max_accel)
print("Max acceleratin in direction [0, -50] is [{}, {}], Magnitude: {:.0f}".format(a_x, a_y, Vector2(a_x, a_y).magnitude()))
[a_x , a_y] = accel_in_XY_dir(.7,.5, max_accel)
print("Max acceleratin in direction [.7, .5] is [{}, {}], Magnitude: {:.0f}".format(a_x, a_y, Vector2(a_x, a_y).magnitude()))
