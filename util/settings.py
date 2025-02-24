from pygame.math import Vector2 as vec2, Vector3 as vec3
from util.keybinds import *

# General
W, H = 1280, 720
ANIM_SPEED = 6
MUSIC_END = pg.USEREVENT+1
SCALE = 3

# Gravity
PLAYER_MASS = 80
VECTOR = vec2(0,-1)

# Misc
INTERACT_RANGE = 150
MOBS = ("slime","rocket","shooter")
PARTICLE_COLORS = {
    "slime": ((190,38,51),(224,111,139)),
    "rocket": ((164,100,34),(235,137,49)),
    "shooter": ((0,87,132),(49,162,242)),
    "player": ((157,157,157),(255,255,255))
}
MAX_MOBS = 400
POWERUP_NAMES = [
    "twin shoot",
    "firing rate +",
    "ball speed +",
    "damage +",
    "levitation",
    "penetration",
    "(shift) pole teleport",
    "(right click) implode"
]

FIRE_RATE = [200, 150, 100, 75]
BALLSPEED = [1, 1.25, 1.5, 1.75, 2]
DAMAGE = [1, 1.5, 2, 3]
GRAVITY = [1, .8, .65, .5]
IMPLODE_RANGE = [300,400,500]
IMPLODE_RELOAD = [4,3,2]
POWERUP_NUM = [1,len(FIRE_RATE)-1,len(BALLSPEED)-1,len(DAMAGE)-1,1,1,1,len(IMPLODE_RANGE)]
HEAL_NUM = [20,5]

PLANETS = ['red','green','brown']

# Images
TOPLEFT, CENTER = range(2)

# UI
UI_SCALE = 4
TYPE_TIME = 80

UI = {}
WHITE =  UI['white']  = (250, 250, 250)
LIGHT1 = UI['light1'] = (212, 216, 224)
LIGHT2 = UI['light2'] = (172, 172, 172)
LIGHT3 = UI['light3'] = (145, 139, 140)
GRAY =   UI['gray']   = (107, 97, 94)
DARK1 =  UI['dark1']  = (59, 52, 46)
DARK2 =  UI['dark2']  = (36, 33, 26)
DARK3 =  UI['dark3']  = (14, 13, 10)
BLACK =  UI['black']  = (3, 2, 1)