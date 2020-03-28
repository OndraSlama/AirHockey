from math import floor

# ------------- DIMENSIONS -------------
# Field dimensions in game units
FIELD_WIDTH = 1000
FIELD_HEIGHT = 600
GOAL_SPAN = 240
CHAMBER_SIZE = 30 # on both size - eg: 30 = 30mm x 30mm

# Limits
YLIMIT = 230
XLIMIT = 70
STRIKER_AREA_WIDTH = 450

# Objects sizes in game units
PUCK_RADIUS = 32
STRIKER_RADIUS = 50

# -------------- STRATEGY --------------
DEFENSE_LINE = STRIKER_RADIUS + PUCK_RADIUS
STOPPING_LINE = 200
CLOSE_DISTANCE = PUCK_RADIUS # what is considered to be "close enough"

# ------------- SIMULATION -------------
MIN_STEP_TIME = 0.012
PUCK_MASS = 20
STRIKER_MASS = 700
BORDER_RESTITUTION = 0.7
STRIKER_RESTITUTION = 0.6
FRICTION_MAG = 100
VELOCITY_DAMP = 0.995

# -------------- MOTORS --------------
# Striker limitations
MAX_ACCELERATION = 15000
MAX_SPEED = 3000
KP_GAIN = 5

# -------------- RULES --------------
GOAL_LIMIT = 3
TIME_LIMIT = 120 #seconds

# Fitness
WINNING_POINTS_PER_SEC = 1
POINTS_PER_GOAL = 1000
SHOT_POINT_MULTIPLIER = 1

# ------------- GRAPHICS -------------
# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
DIMMED_RED = (50,10,10)
YELLOW = (255, 255, 0)
DIMMED_YELLOW = (150, 150, 0)
GREEN = (0, 255, 50)
BLUE = (50, 50, 255)
GREY = (100, 100, 100)
ORANGE = (200, 100, 50)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
TRANS = (1, 1, 1)

# Scaling of the field in window
UNITS_TO_PIXELS_SCALE = 1.2
FIELD_PIXEL_WIDTH = round(FIELD_WIDTH * UNITS_TO_PIXELS_SCALE)
FIELD_PIXEL_HEIGHT = round(FIELD_HEIGHT * UNITS_TO_PIXELS_SCALE)

# Window size
WIDTH = FIELD_PIXEL_WIDTH + 400
HEIGHT = FIELD_PIXEL_HEIGHT + 40

# Field position in window
RIGHT_BORDER_FROM_EDGE = 20
TOP_BORDER_FROM_EDGE = 20

# Text alignment
TEXT_SIZE = 20
NO_OF_COLUMNS = 4
COLUMN_SIZE = 380

# Offsets for units to pixel calculation
X_OFF = WIDTH/2 - (FIELD_PIXEL_WIDTH/2 - (WIDTH - FIELD_PIXEL_WIDTH) / 2 + RIGHT_BORDER_FROM_EDGE)
Y_OFF = HEIGHT/2 - (HEIGHT - FIELD_PIXEL_HEIGHT)/2 + TOP_BORDER_FROM_EDGE

