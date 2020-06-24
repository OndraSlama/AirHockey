# ****************************************************************************** #
# Author: Ondrej Slama
# -------------------

# Zdrojovy kod vytvoreny v ramci projektu robotickeho vzdusneho hokeje - diplomova prace
#  na VUT FSI ustavu automatizace a informatiky v Brne.

# Source code created as a part of robotic air hockey table project - Diploma thesis
# at BUT FME institute of automation and computer sience.

# ****************************************************************************** #
from math import floor

# ----------- ENUM -------------
AI = 0
HUMAN = 1

# ------------- DIMENSIONS -------------
# Field dimensions in game units
FIELD_WIDTH = 1000
FIELD_HEIGHT = 600
GOAL_SPAN = 240
CHAMBER_SIZE = 30 # on both size - eg: 30 = 30mm x 30mm

# Objects sizes in game units
PUCK_RADIUS = 32
STRIKER_RADIUS = 50

# Limits
YLIMIT = 230
XLIMIT = 65
STRIKER_AREA_WIDTH = 446
CORNER_SAFEGUARD_X = XLIMIT + STRIKER_RADIUS * 2
CORNER_SAFEGUARD_Y = STRIKER_RADIUS + PUCK_RADIUS*2


# -------------- STRATEGY --------------
DEFENSE_LINE = STRIKER_RADIUS + PUCK_RADIUS
STOPPING_LINE = 200
CLOSE_DISTANCE = PUCK_RADIUS # what is considered to be "close enough"

# -------------- MOTORS --------------
# Striker limitations
MAX_ACCELERATION = 30000
MAX_DECELERATION = 100000
MAX_SPEED = 3000
KP_GAIN = MAX_DECELERATION/(MAX_SPEED*2)

# -------------- Data collector --------------
CLIP_LENGTH = 5 #seconds
CLIP_BEFORE_AFTER_RATIO = 8/10 # cant be zero
CLIP_FRAMERATE = 15


#----------------------------- ONLY FOR AIRHOCKEY SIMULATION -----------------------------
#  ||																				 ||
#  \/																				 \/


# ------------- SIMULATION -------------
MIN_STEP_TIME = 0.008#0.012
PUCK_MASS = 20
STRIKER_MASS = 700
BORDER_RESTITUTION = 0.7
STRIKER_RESTITUTION = 0.6
FRICTION_MAG = 100
VELOCITY_DAMP = 0.995

# ****************************************************************************** #
# Author: Ondrej Slama
# -------------------

# Zdrojovy kod vytvoreny v ramci projektu robotickeho vzdusneho hokeje - diplomova prace
#  na VUT FSI ustavu automatizace a informatiky v Brne.

# Source code created as a part of robotic air hockey table project - Diploma thesis
# at BUT FME institute of automation and computer sience.

# ****************************************************************************** #
# -------------- RULES --------------
GOAL_LIMIT = 3
TIME_LIMIT = 120 #seconds

# Data
MIN_SHOT_SPEED = 700
# MAX_X_VECTOR = 

# Fitness
WINNING_POINTS_PER_SEC = 1
POINTS_PER_GOAL = 1000
SHOT_POINT_MULTIPLIER = 1

# ------------- GRAPHICS -------------

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

