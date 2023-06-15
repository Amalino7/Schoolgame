import tkinter as tk
SCREEN_TITLE = "Clumsy Magus"
# How big are our image tiles?
SPRITE_IMAGE_SIZE = 128

# Scale sprites up or down
SPRITE_SCALING_PLAYER = 1
SPRITE_SCALING_TILES = 1/2

# Scaled sprite size for tiles
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

# Size of screen to show, in pixels
root = tk.Tk()
SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight() 

# --- Physics forces. Higher number, faster accelerating.


# Damping - Amount of speed lost per second
DEFAULT_DAMPING = 0.1
PLAYER_DAMPING = 0.2

# Friction between objects
# PLAYER_FRICTION = 1.0
# WALL_FRICTION = 0.7
# DYNAMIC_ITEM_FRICTION = 0.6

# Mass (defaults to 1)
PLAYER_MASS = 2.0

# Keep player from going too fast
PLAYER_MAX_HORIZONTAL_SPEED = 1950
PLAYER_MAX_VERTICAL_SPEED = 1950

# Force applied while on the ground
PLAYER_MOVE_FORCE_ON_GROUND = 1800

# Close enough to not-moving to have the animation go to idle.
DEAD_ZONE = 0.1

#Facing
RIGHT_FACING = 0
LEFT_FACING = 1
FRONT_FACING=2
BACK_FACING=3

# How many pixels to move before we change the texture in the walking animation
DISTANCE_TO_CHANGE_TEXTURE = 50

#size of tile
TILE_SIZE = 64

# How much force to put on the bullet
BULLET_MOVE_FORCE = 4500

# Mass of the bullet
BULLET_MASS = 0.1

DIST_UNTIL_BACKFIRE = 1000
DIST_UNTIL_DISAPPEAR = 10000
ENEMY_SPEED = 10
FOLLOW_SPEED = 3
FORCE_FOR_MOVEMENT= 100


# Navigation speed
SPRITE_SPEED = 3

# Key offset
KEY_OFSET = 18
FIRST_KEY_ID = 20

# Laser speed
LASER_SPEED = 5

# Reflector ID
REFL_DL = 16
REFL_DR = REFL_DL + 1
REFL_UR = REFL_DL + 2
REFL_UL = REFL_DL + 3

# Emitter constant
EMIT_OFSET = 7

# Collector constant
COLL_OFSET = 3

TIME_TO_SEE = 1

BULLET_MOVE_TICK = 15

FORCE_MULTIPLR = 10

ATTACK_COOLDOWN_TIME = 0.1
