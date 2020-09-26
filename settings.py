import pygame as pg
vec = pg.math.Vector2
from random import choice

# Colors
WHITE     = (255, 255, 255)
BLACK     = (0  , 0  , 0  )
DARKGREY  = (40 , 40 , 40 )
LIGHTGREY = (100, 100, 100)
GREEN     = (20 , 255, 20 )
RED       = (255, 0  , 0  )
YELLOW    = (255, 255, 0  )

# game settings
WIDTH   = 1024
HEIGHT  = 768
FPS     = 60
TITLE   = "RESCUE APOCALYPSE"
BGCOLOR = DARKGREY

TILESIZE    = 64
GRIDWIDTH   = WIDTH  / TILESIZE
GRIDHEIGHT  = HEIGHT / TILESIZE
LEVELWIDTH  = 30*TILESIZE
LEVELHEIGHT = 20*TILESIZE

# Player settings
PLAYER_SPEED    = 100
GRAVITY         = vec(0, 250 )
JUMPFORCE       = vec(0, -260)
PLAYER_HEALTH   = 100
PLAYER_HIT_RECT = pg.Rect(0, 0, 40, 84)

# Shuriken settings
SHURIKEN_SPEED  = 250
SHURIKEN_RATE   = 800
SHURIKEN_RANGE  = 1200
SHURIKEN_OFFSET = vec(40, 0)
SHURIKEN_DAMAGE = 10

# Zombie settings
ZOMBIE_SPEED = PLAYER_SPEED//4
ZOMBIE_HEALTH     = 50
ZOMBIE_DAMAGE     = 20
ZOMBIE_HIT_RECT   = pg.Rect(0, 0, 40, 82)

# item settings
BOB_RANGE   = 40
BOB_SPEED   = 1
ITEM_IMAGES = {'Blades': 'Kunai.png'}
ITEM_LIST   = ['Blades']

# MUSIC
BG_MUSIC = 'BG.ogg'

