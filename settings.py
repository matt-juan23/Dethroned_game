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

TITLE = "Dethroned"
WIDTH = 1024
HEIGHT = 768
FPS = 60

# Effects
MUZZLE_FLASHES = ['whitePuff15.png', 'whitePuff16.png', 'whitePuff17.png', 
				  'whitePuff18.png']
SPLAT = 'splat green.png'
STAR = 'stars_184.png'
FLASH_DURATION = 40
DAMAGE_ALPHA = [i for i in range(0, 255, 25)]

# Button images
BUTTON_IMAGES = {1: 'KeyboardButtonsDir_up.png',
				 2: 'KeyboardButtonsDir_down.png',
				 3: 'KeyboardButtonsDir_left.png',
				 4: 'KeyboardButtonsDir_right.png',
				 5: 'w.png',
				 6: 's.png',
				 7: 'a.png',
				 8: 'd.png',
				 9: 'keyboard_key_e.png',
				 10: 'space_bar.png'}
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
# Will change when I find better sounds
ZOMBIE_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav',
                      'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav', 'zombie-roar-7.wav']
ZOMBIE_HIT_SOUNDS = ['splat-15.wav']
# Will change later
WEAPON_SOUNDS = {'fireball': ['flame_arrow.wav', 'fireball2.wav'],
				  'sword': ['sword1.wav', 'sword2.wav']}
EFFECTS_SOUNDS = {'level_start': 'level_start.wav',
                  'health_up': 'health_pack.wav',
                  'gun_pickup': 'gun_pickup.wav'}

# Layers
WALL_LAYER = 1
ITEMS_LAYER = 1
PLAYER_LAYER = 2
MOB_LAYER = 2
BULLET_LAYER = 3
EFFECTS_LAYER = 4

# Player properties

PLAYERS = {}

PLAYERS['mage'] = {'speed': 150,
					 'health': 500.0,
					 'dodge_dist': 300,
					 'dodge_time': 1000,
					 'images':{},
					 'ability':'test_field.png',
					 'weapon': 'fireball',
					 'e_cooldown': 3000,
					 'e_length': 5000,
					 'barrel_offset': vec(0, 0)}

PLAYERS['mage']['images'] = {'up': ['amg1_bk1.png','amg1_bk2.png'],
				 		  	   'down': ['amg1_fr1.png','amg1_fr2.png'],
				 			   'left': ['amg1_lf1.png','amg1_lf2.png'],
				 			   'right': ['amg1_rt1.png','amg1_rt2.png']}

PLAYERS['knight'] = {'speed': 180,
					 'health': 300.0,
					 'dodge_dist': 5,
					 'dodge_time': 100,
					 'images': {},
					 'ability':'tile_14.png',
					 'weapon': 'sword', 
					 'e_cooldown': 3000,
					 'e_length': 5000,
					 'barrel_offset': vec(30, 10)}

PLAYERS['knight']['images'] = {'up': ['knt2_bk1.png','knt2_bk2.png'],
				 		  	   'down': ['knt2_fr1.png','knt2_fr2.png'],
				 			   'left': ['knt2_lf1.png','knt2_lf2.png'],
				 			   'right': ['knt2_rt1.png','knt2_rt2.png']}

PLAYERS['ninja'] = {'speed': 300,
					 'health': 80.0,
					 'dodge_dist': 5,
					 'dodge_time': 100,
					 'images': {},
					 'ability':'tile_14.png',
					 'weapon': 'fireball', 
					 'e_cooldown': 3000,
					 'e_length': 5000,
					 'barrel_offset': vec(30, 10)}

PLAYERS['ninja']['images'] = {'up': ['nja4_bk1.png','nja4_bk2.png'],
				 		  	   'down': ['nja4_fr1.png','nja4_fr2.png'],
				 			   'left': ['nja4_lf1.png','nja4_lf2.png'],
				 			   'right': ['nja4_rt1.png','nja4_rt2.png']}

# Weapon settings
BULLET_IMG = 'fireball.png'
WEAPONS = {}
WEAPONS['sword'] = {'bullet_speed': 400, # sword range
					  'bullet_lifetime': 400,
					  'rate': 250,
					  'kickback': 30,
					  'spread': 5,
					  'damage': 17,
					  'bullet_size': 'lg',
					  'bullet_count': 1,
					  'ammo_count': float("inf"),
					  'reload_time': 1000}
WEAPONS['fireball'] = {'bullet_speed': 400,
					  'bullet_lifetime': 500,
					  'rate': 900,
					  'kickback': 80,
					  'spread': 8,
					  'damage': 170,
					  'bullet_size': 'lg',
					  'bullet_count': 1,
					  'ammo_count': 7,
					  'reload_time': 1000}

# Mob settings

MOBS = {}
MOBS['zombie'] = {'speed': [150, 100, 75, 125],
				   'health': 100,
				   'damage': 10,
				   'knockback': 20,
				   'avoid_radius': 50,
				   'detect_radius': 300, # how far the mob can see
				   'images': {}}

MOBS['zombie']['images'] = {'up': ['mst1_bk1.png', 'mst1_bk2.png'],
							 'down': ['mst1_fr1.png', 'mst1_fr2.png'],
							 'left': ['mst1_lf1.png', 'mst1_lf2.png'],
							 'right': ['mst1_rt1.png', 'mst1_rt2.png']}

MOBS['trooper'] = {'speed': [150, 100, 75, 125],
				   'health': 100,
				   'damage': 10,
				   'knockback': 20,
				   'avoid_radius': 50,
				   'detect_radius': 300, # how far the mob can see
				   'images': {}}

MOBS['trooper']['images'] = {'up': ['gsd1_bk1.png', 'gsd1_bk2.png'],
							 'down': ['gsd1_fr1.png', 'gsd1_fr2.png'],
							 'left': ['gsd1_lf1.png', 'gsd1_lf2.png'],
							 'right': ['gsd1_rt1.png', 'gsd1_rt2.png']}


#BOSS = ['zoimbie1_hold.png']

BOSS = {}
BOSS['level1'] = {'speed': 20,
				  'health': 200,
				  'damage': 10,
				  'knockback': 20,
				  'avoid_radius': 50,
				  'detect_radius': 400,
				  'image': ['zoimbie1_hold.png'], # not necessary to be list. maybe change later on
				  'bullet_img': 'bullet.png'}


MOB_WEAPON = {}
MOB_WEAPON['trooper'] = {'bullet_speed': 400}


'''TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDWIDTH = HEIGHT / TILESIZE'''