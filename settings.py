# game options/settings
import pygame as pg
vec = pg.math.Vector2

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
BROWN = (106, 55, 5)

TITLE = "Tilemap"
WIDTH = 1024
HEIGHT = 768
FPS = 60
BGCOLOR = BROWN

WALL_IMG = 'tile_14.png'

# Effects
MUZZLE_FLASHES = ['whitePuff15.png', 'whitePuff16.png', 'whitePuff17.png', 
				  'whitePuff18.png']
SPLAT = 'splat green.png'
FLASH_DURATION = 40
DAMAGE_ALPHA = [i for i in range(0, 255, 25)]
NIGHT_COLOR = (20, 20, 20)
LIGHT_RADIUS = (500, 500)
LIGHT_MASK = "light_350_med.png"

# Button images
BUTTON_IMAGES = {1: 'KeyboardButtonsDir_up.png',
				 2: 'KeyboardButtonsDir_down.png',
				 3: 'KeyboardButtonsDir_left.png',
				 4: 'KeyboardButtonsDir_right.png',
				 5: 'w.png',
				 6: 's.png',
				 7: 'a.png',
				 8: 'd.png',
				 9: 'space_bar.png'}
# Items
ITEM_IMAGES = {'health': 'health_pack.png',
			   'shotgun': 'obj_shotgun.png',
			   'jump': 'bolt_gold.png'}
HEALTH_PACK_AMOUNT = 20
BOB_RANGE = 15
BOB_SPEED = 0.9

# Sounds
BG_MUSIC = 'espionage.ogg'
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
ZOMBIE_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav',
                      'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav', 'zombie-roar-7.wav']
ZOMBIE_HIT_SOUNDS = ['splat-15.wav']
WEAPON_SOUNDS = {'pistol': ['flame_arrow.wav'],
				  'shotgun': ['shotgun.wav']}
EFFECTS_SOUNDS = {'level_start': 'level_start.wav',
                  'health_up': 'health_pack.wav',
                  'gun_pickup': 'gun_pickup.wav'}

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1

# Player properties
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = vec(30, 10) # Put into dictionary for different hero

PLAYERS = {}
PLAYERS['knight'] = {'speed': 100,
					 'health': 150.0,
					 'dodge_dist': 50,
					 'dodge_time': 100,
					 'images': {},
					 'weapon': 'pistol'}
PLAYERS['mage'] = {'speed': 150,
					 'health': 500.0,
					 'dodge_dist': 1100,
					 'dodge_time': 1000,
					 'images':{},
					 'weapon': 'shotgun'}

'''for player in PLAYERS:
	for img in PLAYERS[player]['images']:
		load image'''

PLAYERS['mage']['images'] = {'up': ['amg1_bk1.png','amg1_bk2.png'],
				 		  	   'down': ['amg1_fr1.png','amg1_fr2.png'],
				 			   'left': ['amg1_lf1.png','amg1_lf2.png'],
				 			   'right': ['amg1_rt1.png','amg1_rt2.png']}

PLAYERS['knight']['images'] = {'up': ['knt2_bk1.png','knt2_bk2.png'],
				 		  	   'down': ['knt2_fr1.png','knt2_fr2.png'],
				 			   'left': ['knt2_lf1.png','knt2_lf2.png'],
				 			   'right': ['knt2_rt1.png','knt2_rt2.png']}


# Mob settings
MOB_IMG = 'zoimbie1_hold.png'
MOB_SPEEDS = [150, 100, 75, 125]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 400 # How far the mob can see in pixels

# Weapon settings
BULLET_IMG = 'fireball.png'
WEAPONS = {}
WEAPONS['pistol'] = {'bullet_speed': 100, # sword range
					  'bullet_lifetime': 60,
					  'rate': 250,
					  'kickback': 30,
					  'spread': 5,
					  'damage': 17,
					  'bullet_size': 'lg',
					  'bullet_count': 1,
					  'ammo_count': float("inf"),
					  'reload_time': 1000}
WEAPONS['shotgun'] = {'bullet_speed': 400,
					  'bullet_lifetime': 500,
					  'rate': 900,
					  'kickback': 80,
					  'spread': 20,
					  'damage': 5,
					  'bullet_size': 'sm',
					  'bullet_count': 12,
					  'ammo_count': 5,
					  'reload_time': 1000}

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDWIDTH = HEIGHT / TILESIZE