# Settings File
import pygame as pg
vec = pg.math.Vector2

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
MINT = (100, 224, 170)

# Game settings
TITLE = "Dethroned"
WIDTH = 1024
HEIGHT = 768
FPS = 60

# Other images
STAR = 'stars_184.png'
ABILITY = 'ability.png'
CONTROLS = 'controls.png'
BACKGROUND = 'castle background.png'
CROSSHAIR = 'crosshair.png'
HOW_TO_PLAY = 'how_to_play.png'
FLASH_DURATION = 40
DAMAGE_ALPHA = [i for i in range(0, 255, 70)] # increase last number to get faster flash

# Level maps
LEVELS = ['level1.tmx',
          'level2.tmx',
          'level3.tmx']

# Sounds
BG_MUSIC = 'Mystic Dungeon.ogg'
LEVEL_START_SOUND = 'level_start.wav'
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
DEATH_SOUND = 'death.wav'

WEAPON_SOUNDS = [['fireball1.wav', 'fireball2.wav'],
                 ['sword1.wav', 'sword2.wav'],
                 ['kunai1.wav', 'kunai2.wav']]

# Layers
WALL_LAYER = 1
ITEMS_LAYER = 1
PLAYER_LAYER = 2
MOB_LAYER = 2
BULLET_LAYER = 3
CROSSHAIR_LAYER = 4
EFFECTS_LAYER = 4

# Player properties
PLAYERS = {}
PLAYERS['mage'] = {'speed': 200,
                     'health': 200.0,
                     'dodge_dist': 750.0,
                     'dodge_cooldown': 1,
                     'images':{},
                     'ability':'test_field.png',
                     'weapon': 'fireball',
                     'e_cooldown': 3,
                     'e_length': 5,
                     'e_health_gain': 20,
                     'e_gain_rate': 1, # gain health every 1 second
                     'e_uses': 5,
                     'barrel_offset': {},
                     'id': 0}

PLAYERS['mage']['images'] = {'up': ['amg1_bk1.png','amg1_bk2.png'],
                               'down': ['amg1_fr1.png','amg1_fr2.png'],
                               'left': ['amg1_lf1.png','amg1_lf2.png'],
                               'right': ['amg1_rt1.png','amg1_rt2.png']}

PLAYERS['mage']['barrel_offset'] = {'up': vec(20, 10),
                                    'down': vec(5, 15),
                                    'left': vec(10, 0),
                                    'right': vec(10, 0)}


PLAYERS['knight'] = {'speed': 150,
                     'health': 350.0,
                     'dodge_dist': 450.0,
                     'dodge_cooldown': 1.5,
                     'images': {},
                     'ability':'tile_14.png',
                     'weapon': 'sword', 
                     'e_cooldown': 3,
                     'e_length': 5,
                     'e_health_gain': 10,
                     'e_uses': 5,
                     'barrel_offset': {},
                     'id': 1}

PLAYERS['knight']['images'] = {'up': ['knt2_bk1.png','knt2_bk2.png'],
                               'down': ['knt2_fr1.png','knt2_fr2.png'],
                               'left': ['knt2_lf1.png','knt2_lf2.png'],
                               'right': ['knt2_rt1.png','knt2_rt2.png']}

PLAYERS['knight']['barrel_offset'] = {'up': vec(20, 10),
                                      'down': vec(25, 12),
                                      'left': vec(30, 0),
                                      'right': vec(30, 0)}

PLAYERS['ninja'] = {'speed': 300,
                     'health': 10.0,
                     'dodge_dist': 750.0,
                     'dodge_cooldown': 0.8,
                     'images': {},
                     'ability':'tile_10.png',
                     'weapon': 'kunai', 
                     'e_cooldown': 1,
                     'e_length': 6,
                     'e_health_gain': 40,
                     'e_uses': 5,
                     'barrel_offset': {},
                     'id': 2}

PLAYERS['ninja']['images'] = {'up': ['nja4_bk1.png','nja4_bk2.png'],
                               'down': ['nja4_fr1.png','nja4_fr2.png'],
                               'left': ['nja4_lf1.png','nja4_lf2.png'],
                               'right': ['nja4_rt1.png','nja4_rt2.png']}

PLAYERS['ninja']['barrel_offset'] = {'up': vec(20, 10),
                                     'down': vec(5, 15),
                                     'left': vec(10, 0),
                                     'right': vec(10, 0)}

# Weapon settings
WEAPONS = {}
WEAPONS['fireball'] = {'bullet_speed': 400,
                       'bullet_lifetime': 500,
                       'rate': 0.9,
                       'kickback': 80,
                       'damage': 100,
                       'ammo_count': 7,
                       'reload_time': 1,
                       'scale': (30, 30),
                       'image': 'fireball.png'}

WEAPONS['sword'] = {'bullet_speed': 400, # sword range
                    'bullet_lifetime': 50,
                    'rate': 0.3,
                    'kickback': 30,
                    'damage': 130,
                    'ammo_count': float("inf"),
                    'reload_time': 0,
                    'scale': (60, 20),
                    'image': 'Katana_Pixel.png'}

WEAPONS['kunai'] = {'bullet_speed': 600,
                    'bullet_lifetime': 500,
                    'rate': 0.6,
                    'kickback': 80,
                    'damage': 90,
                    'ammo_count': 10,
                    'reload_time': 0.8,
                    'scale': (25, 25),
                    'image': 'Kunai_Pixel.png'}

WEAPONS['trooper'] = {'bullet_speed': 400,
                      'bullet_lifetime': 500,
                      'rate': 2,
                      'damage': 10,
                      'scale': (30, 30),
                      'image': 'tile_369.png'}

WEAPONS['demon'] = {'bullet_speed': 322,
                    'bullet_lifetime': 500,
                    'rate': 1,
                    'damage': 6,
                    'scale': (30, 30),
                    'bullet_count': 7,
                    'spread': 20,
                    'image': 'bullet2.png'}

WEAPONS['level1'] = {'bullet_speed': 300,
                      'bullet_lifetime': 700,
                      'rate': 2.5,
                      'damage': 30,
                      'scale': (30, 30),
                      'image': 'bullet.png'}

WEAPONS['level2'] = {'bullet_speed': 400,
                      'bullet_lifetime': 700,
                      'rate': 2.5,
                      'damage': 35,
                      'scale': (30, 30),
                      'image': 'bullet.png'}

# Mob settings
MOBS = {}
MOBS['brawler'] = {'speed': [150, 100, 75, 125],
                   'health': 200.0,
                   'con_damage': 10,
                   'knockback': 20,
                   'avoid_radius': 50,
                   'detect_radius': 200, # how far the mob can see
                   'images': {}}

MOBS['brawler']['images'] = {'up': ['mst1_bk1.png', 'mst1_bk2.png'],
                             'down': ['mst1_fr1.png', 'mst1_fr2.png'],
                             'left': ['mst1_lf1.png', 'mst1_lf2.png'],
                             'right': ['mst1_rt1.png', 'mst1_rt2.png']}

MOBS['trooper'] = {'speed': [150, 100, 75, 125],
                   'health': 150.0,
                   'con_damage': 10, # contact damage
                   'knockback': 20,
                   'avoid_radius': 50,
                   'detect_radius': 300, # how far the mob can see
                   'images': {}}

MOBS['trooper']['images'] = {'up': ['gsd1_bk1.png', 'gsd1_bk2.png'],
                             'down': ['gsd1_fr1.png', 'gsd1_fr2.png'],
                             'left': ['gsd1_lf1.png', 'gsd1_lf2.png'],
                             'right': ['gsd1_rt1.png', 'gsd1_rt2.png']}

MOBS['demon'] = {'speed': [150, 100, 75, 125],
                 'health': 125.0,
                 'con_damage': 10,
                 'knockback': 30,
                 'avoid_radius': 50,
                 'detect_radius': 300, # how far the mob can see
                 'images': {}}

MOBS['demon']['images'] = {'up': ['dvl1_bk1.png', 'dvl1_bk2.png'],
                           'down': ['dvl1_fr1.png', 'dvl1_fr2.png'],
                           'left': ['dvl1_lf1.png', 'dvl1_lf2.png'],
                           'right': ['dvl1_rt1.png', 'dvl1_rt2.png']}

# Boss settings
BOSS = {}
BOSS['level1'] = {'speed': 20,
                  'health': 600.0,
                  'con_damage': 20,
                  'knockback': 0,
                  'avoid_radius': 50,
                  'detect_radius': 400,
                  'image': 'zoimbie1_hold.png'}

BOSS['level2'] = {'speed': 25,
                  'health': 800.0,
                  'con_damage': 23,
                  'knockback': 70,
                  'avoid_radius': 50,
                  'detect_radius': 350,
                  'image': 'robot1_machine.png'}