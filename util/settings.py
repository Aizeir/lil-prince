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
MOBS = ("slime","rocket")

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