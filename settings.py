import pygame, math
from pygame import Vector2 as vector
from random import randint, uniform, choice

# WINDOW
pygame.display.init()
WIDTH, HEIGHT = WINDOW_SIZES = pygame.display.get_desktop_sizes()[0]
H_WIDTH, H_HEIGHT = WIDTH//2, HEIGHT//2
WINDOW_CENTER = vector(H_WIDTH, H_HEIGHT)
WINDOW_TITLE = "Open Farm"
WINDOW_FPS = 0

# COLORS
FOG_COLOR = (110,150,124)
HOUSE_BG_COL = (40,40,40)
TEXT_WHITE = (243,244,231)
TEXT_LIGHT = (232,207,166)
TEXT_DARK = (182,137,98)
NIGHT_COLOR = (0,50,120)
TRANSITION_COL = FOG_COLOR

# COOLDOWNS
BERRY_COOLDOWN =       60*1000
TREE_COOLDOWN = 10    *60*1000
COW_COOLDOWN = 4      *60*1000
CHICKEN_COOLDOWN = 3  *60*1000
DAY_START = 8         *3600
SUNRISE_TIME = 6      *3600
SUNSET_TIME = 19      *3600
MIDNIGHT_TIME = 24    *3600
DAY_END = 21          *3600
CROP_COOLDOWNS = {
    "tomato": 5*60*1000,
    "wheat": 4*60*1000,
}

# SPEEDS
ANIMATION_SPEED = 6
TIME_SPEED = 1
BAG_SPEED = 10
TAB_SPEED = 20
DIALOGUE_SPEED = 10
TEXT_SPEED = 30
TRANSITION_SPEED = 10
PLAYER_SPEED = 300
ANIMAL_SPEEDS = {
    "chicken": 30,
    "cow": 50,
}

# CONSTANTS
TILE_SIZE = 1536//28
H_TILE_SIZE = TILE_SIZE//2
SMALL_REAL_TILE_SIZE = 16
MID_REAL_TILE_SIZE = 32
REAL_TILE_SIZE = 64

# SCALES
SMALL_SCALE = TILE_SIZE/SMALL_REAL_TILE_SIZE
MID_SCALE = TILE_SIZE/MID_REAL_TILE_SIZE
SCALE = TILE_SIZE/REAL_TILE_SIZE
UI_SCALE = SCALE*3
UI_SCALE_S = SCALE*2
UI_SCALE_B = SCALE*4

# ZONE
ZONE_TILE_NUM = 60
H_ZONE_TILE_NUM = ZONE_TILE_NUM//2
ZONE_SIZE = ZONE_TILE_NUM*TILE_SIZE
H_ZONE_SIZE = ZONE_SIZE//2

# WEIGHTS
FLOOR_WEIGHTS = [100,100,100,20,20,30,50,50,50,10,10,30,1000]
PLANT_WEIGHTS = [100,100,10,10,60, 80,80,10,10,-1]
FUNGUS_WEIGHTS = [0,0,1000,1000,0,0,0,800,800,-1]
WINDOW_WEIGHTS = [100,20]

# WORLD
TREE_SIZES =  ["small", "medium"]
USE_SMALL = ["house"]
FOG_SIZE = int(TILE_SIZE*3)
NIGHT_ALPHA = 70
TRANSITION_THRESHOLD = 30
TINTS = [
    (0, 0, 0),
    (20, 0, 0),
    (0, 20, 0),
    (0, 0, 20),
    (20, 20, 0),
    (20, 0, 20),
    (0, 20, 20),
    (20, 20, 20),
    (20, 10, 0),
    (10, 0, 20),
    (0, 10, 20),
    (0, 20, 10),
    (10, 20, 0),
]
NO_TINT = (0,0,0)

# PLAYER
PLAYER_MAX_WATER = 20
INTERACT_RADIUS = TILE_SIZE*4
ITEM_SHORTCUT = {
    1: "axe",
    2: "hoe",
    3: "water",
    4: "wheat-seeds",
    5: "tomato-seeds",
}

# INVENTORY
TOOLS = ["axe","hoe","water"]
OBJECTS = ["wheat-seeds","tomato-seeds"]
ITEMS = ["wood","tomato","wheat","grass","apple", "berry","egg","milk"]
LOCKED_TOOLS = []
PLACEABLE = []

# MENU
UI_OFFSET = int(10*SCALE)
UI_OFFSET_H = UI_OFFSET//2
ANTIALAS = False
OUTLINE_SIZE = 2

# VILLAGER
VILLAGERS = {
    "Soil Farmer" : {
        "trade": True,
        "craft": False,
        "trade-num": (3,5),
        "trades": {
            "grass": 1,
            "tomato": 22,
            "wheat": 20,
            "tomato-seeds": 11,
            "wheat-seeds": 10,
        }
    },
    "Wood Cutter": {
        "trade": True,
        "craft": False,
        "trade-num": (1,2),
        "trades": {
            "wood": 3,
            "grass": 2,
        }
    },
    "Tree Farmer":{
        "trade": True,
        "craft": False,
        "trade-num": (2,3),
        "trades": {
            "apple": 6,
            "berry": 8,
            "wood": 2
        }
    },
    "Animal Farmer": {
        "trade": True,
        "craft": False,
        "trade-num": (2,4),
        "trades": {
            "milk": 40,
            "egg": 30,
            "wheat": 15,
            "grass": 1
        }
    },
    "Villager": {
        "trade": False,
        "craft": False,
        "dialogues": [
            "Hi, welcome to our village!",
            "Welcome adventurer. Please help us!",
            "I thought noone could travel through the dark forest!",
            "Welcome, welcome! We will be happy to trade with you!",
        ] 
    },
#    "Crafter": {
#        "trade": False,
#        "craft": True,
#        "crafts": [
#            ["wood", 3, "fence", 1]
#        ]
#    }
}