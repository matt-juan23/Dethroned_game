'''
MAIN PROBLEMS:
 - bars do not get drawn over if sprite does not move
'''

# Sprites classes for game
import pygame as pg
import pytweening as tween
import time
from random import uniform, choice, randint, random
from settings import *
from tilemap import *
from itertools import chain
vec = pg.math.Vector2

def collide_with_walls(sprite, group, dir): 
    # Not my code. taken from kidscancode
    # handles colliding with walls
    # takes sprite, walls group and direction of collision
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2.0
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2.0
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x

    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2.0
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2.0
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

# All subprograms within each class have a parameter of self which passes the class as a parameter

class Player(pg.sprite.Sprite):
    # initialise as a sprite
    def __init__(self, game, x, y, char):
        # initialise variables to be used in class
        # takes game class from main file, x and y int coordinates of spawn and string define which character was selected
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.char = char
        self.image = game.player_img[self.char]['down'][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = self.rect
        self.hit_rect.center = self.rect.center
        self.vel_x, self.vel_y = 0, 0
        self.vel = vec(self.vel_x, self.vel_y)
        self.pos = vec(x, y) 
        self.rot = 0
        self.camera = Camera(game.map.width, game.map.height)

        #time initialising
        time_now = time.time() # time when player object is initialised
        self.last_shot = time_now
        self.last_reload = time_now
        self.last_dodge = 0 # change to time.time()
        self.last_sprite_change = time_now
        self.last_ability = time_now

        # player and weapon data initialise
        self.weapon = PLAYERS[self.char]['weapon']
        self.health = PLAYERS[self.char]['health']
        self.weapon_data = WEAPONS[self.weapon]
        self.player_data = PLAYERS[self.char] 
        self.ammo_count = WEAPONS[self.weapon]['ammo_count']
        self.full_ammo = WEAPONS[self.weapon]['ammo_count']
        self.ability_uses = PLAYERS[self.char]['e_uses']

        # boolean intialising
        self.damaged = False
        self.reloading = False
        self.moving = False
        self.lvlup = False
        self.ability_active = False

        self.power = ''
        self.which_sprite = 0

        self.seconds_string = self.player_data['e_cooldown'] # string for ability timer
        self.seconds_timer = time_now # time comparison variable

    def get_keys(self):
        # called repeatedly to check for which keys are pressed
        # This method is for keys being held
        # single press is in the events method in main.py

        # set values in case nothing gets set to it
        self.vel_x, self.vel_y = 0, 0
        keys = pg.key.get_pressed()

        # default face
        self.face = 'down'

        # Check if arrow key is pressed and set values accordingly
        # Should convert this to function to avoid repetition
        if keys[pg.K_UP]:
            self.vel_y = -self.player_data['speed']
            self.face = 'up' 
        if keys[pg.K_DOWN]:
            self.vel_y = self.player_data['speed']
            self.face = 'down' 
        if keys[pg.K_RIGHT]:
            self.vel_x = self.player_data['speed']
            self.face = 'right' 
        if keys[pg.K_LEFT]:
            self.vel_x = -self.player_data['speed']
            self.face = 'left' 

        # Diagonal movemnt
        if self.vel_x != 0 and self.vel_y != 0:
            self.vel_x *= 0.7071
            self.vel_y *= 0.7071

        if self.vel_x == 0 and self.vel_y == 0:
            self.moving = False # set moving to false when player is not moving
        else:
            self.moving = True

        # Check if WASD is pressed. Maybe something that looks more efficient
        if self.ammo_count > 0 and self.reloading == False:
            if keys[pg.K_w]:
                self.face = 'up'
                self.shoot(90)
            elif keys[pg.K_s]:
                self.face = 'down'
                self.shoot(270)
            elif keys[pg.K_a]:
                self.face = 'left'
                self.shoot(180)
            elif keys[pg.K_d]:
                self.face = 'right'
                self.shoot(0)

        # Reload if condition 
        if (keys[pg.K_r] and self.ammo_count != self.full_ammo) or self.ammo_count == 0:
            self.reload()

        # Jump if condition
        '''if keys[pg.K_SPACE] and self.moving == True:
            now = pg.time.get_ticks()
            if now - self.last_dodge > self.player_data['dodge_time']:
                self.last_dodge = now
                self.dodge()'''

    def draw_player_health(self, surf, x, y, pct):
        # Draw player health in the top left corner
        if pct < 0:
            pct = 0
        BAR_LENGTH = 100
        BAR_HEIGHT = 20
        fill = pct * BAR_LENGTH
        outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)

        # Change color based on percentage of health
        if pct > 0.6:
            col = GREEN
        elif pct > 0.3:
            col = YELLOW
        else:
            col = RED

        # draw the health bar
        pg.draw.rect(surf, col, fill_rect)
        pg.draw.rect(surf, WHITE, outline_rect, 2)

    def dodge(self): # allows to phase through walls
        # function called when space is hit
        # shifts character certain distance in a direction determined by self.face string
        now = pg.time.get_ticks()
        time = 0
        if now - self.last_dodge > self.player_data['dodge_time']:
        	self.last_dodge = now
        	if self.face == 'up':
        		self.vel_y -= self.player_data['dodge_dist']
        	if self.face == 'down':
        		self.vel_y += self.player_data['dodge_dist']
        	if self.face == 'left':
        		self.vel_x -= self.player_data['dodge_dist']
        	if self.face == 'right':
        		self.vel_x += self.player_data['dodge_dist']

    def reload(self):
        # reload function
        self.last_reload = time.time()
        self.reloading = True
        self.ammo_count = self.full_ammo # sets ammo back to full

    def shoot(self, rot):
        # shoot function
        self.image = self.game.player_img[self.char][self.face][0] # change sprite to face in shooting direction
        if time.time() - self.last_shot > self.weapon_data['rate']:
            self.ammo_count -= 1
            self.last_shot = time.time()
            dir = vec(1, 0).rotate(-rot)
            pos = self.pos + PLAYERS[self.char]['barrel_offset'][self.face].rotate(-rot) # offsets where bullet sprite spawns
            self.vel = vec(-self.weapon_data['kickback'], 0).rotate(-rot) # knockback when shooting
            Bullet(self.game, pos, dir, self.weapon_data['damage'], rot) # spawn bullet

            # play sound
            snd = choice(self.game.weapon_sounds[self.weapon])
            if snd.get_num_channels() > 2:
                snd.stop()
            snd.play()

            # Mostly not mine. Handles pellets per shot and bullet spread
            '''for i in range(self.weapon_data['bullet_count']):
                spread = uniform(-self.weapon_data['spread'], self.weapon_data['spread'])
                Bullet(self.game, pos, dir.rotate(spread), self.weapon_data['damage'], rot) # Spawn bullet
                snd = choice(self.game.weapon_sounds[self.weapon])
                if snd.get_num_channels() > 2: # 
                    snd.stop()
                snd.play()'''
            #MuzzleFlash(self.game, pos)

    # works - not my code
    def hit(self): # apply to mobs
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA) # 1 flash

    def sprite_change(self):
        # called whenever the sprite needs to be changed
        self.which_sprite = 1 - self.which_sprite
        self.image = self.game.player_img[self.char][self.face][self.which_sprite]

    def powerup(self, item):
        # powerup method
        # item is a string that is determined by which powerup is hit
        self.power = item
        if item == 'shotgun':
        	self.weapon_data['damage'] *= 2
        if item == 'jump':
        	self.player_data['dodge_dist'] *= 2

    def e_ability(self):
        # e ability
        if time.time() - self.last_ability > self.player_data['e_cooldown'] and self.ability_active == False and self.ability_uses > 0: 
            self.ability_active = True
            self.ability_uses -= 1
            self.last_ability = time.time()

            # spawn ability
            Ability(self, self.game)
            '''for bullet in self.game.mob_bullets:
                bullet.kill()''' # idea for clearing all mob bullets off screen

    def draw_ability(self):
        if self.ability_active:
            # equation for the health bar to decrease over time
            width = int(self.rect.width * abs(time.time() - self.last_ability - PLAYERS[self.char]['e_length']) / PLAYERS[self.char]['e_length'])
            ability_bar = pg.Rect(0, 0, width, 7)
            pg.draw.rect(self.image, GREEN, ability_bar)

    def update(self):
        # update all necessary values and calls get_keys() subprogram
        self.vel = vec(self.vel_x, self.vel_y)
        self.get_keys()

        # Reload timer
        if self.reloading and time.time() - self.last_reload > self.weapon_data['reload_time']:
            self.reloading = False
        
        # Level up timer
        if self.damaged and self.lvlup == True:
        	self.lvlup = False
        	if self.power == 'shotgun':
        		self.weapon_data['damage'] /= 2
        	if self.power == 'jump':
        		self.player_data['dodge_dist'] /= 2

        # Sprite change
        if (self.moving and time.time() - self.last_sprite_change > 0.1) or self.damaged:
            self.last_sprite_change = time.time()
            #self.which_sprite = 1 - self.which_sprite # switch between 1 and 0
            self.sprite_change()

        self.image = self.image.copy() # used for the ability timer to be displayed properly on all sprites

        # update timer for the ability
        if time.time() - self.seconds_timer >= 1:
            self.seconds_timer = time.time()
            self.seconds_string -= 1
            if self.seconds_string < 0:
            	self.seconds_string = 0

        if self.damaged:
        	try:
        		# special flags in pygame
        		self.image.fill((255, 255, 255, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
        	except:
        		self.damaged = False # exception is raised

        # Update player position
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x

        # Collision detection
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

class Mob(pg.sprite.Sprite):
    # initialise as a sprite
    def __init__(self, game, x, y, type):
        # initialise mob sprite
        # parameters passed are the game class, x and y int coordinates of spawn and which type of mob, held in a string
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.enemy_type = type
        self.image = game.mob_img[self.enemy_type]['down'][0]
        self.mob_data = MOBS[self.enemy_type]

        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect.copy()
        self.hit_rect.center = self.rect.center
        self.rect.center = self.pos
        self.face = 'down'
        self.rot = 0
        self.which_sprite = 0
        self.last_sprite_change = pg.time.get_ticks()
        self.health = self.mob_data['health']
        self.speed = choice(self.mob_data['speed'])
        self.target = game.player
        self.moving = False
        self.damaged = False
        self.point_worth = 1

    def avoid_mobs(self): 
        # avoids mobs stacking on top of each other
        # kidscancode code
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < self.mob_data['avoid_radius']:
                    self.acc += dist.normalize()

    def hit(self): # apply to mobs
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA) # 1 flash

    def sprite_change(self):
        # called when sprite needs to be changed
        self.which_sprite = 1 - self.which_sprite
        self.image = self.game.mob_img[self.enemy_type][self.face][self.which_sprite]

    def draw_health(self):
        # draws health of each mob on top of sprite
        #change color based on health
        health_pct = self.health / self.mob_data['health']
        if health_pct > 0.6:
            col = GREEN
        elif health_pct > 0.3:
            col = YELLOW
        else:
            col = RED

        width = int(self.rect.width * self.health / self.mob_data['health'])
        if width < 0:
            width = 0
        health_bar = pg.Rect(0, 0, width, 7)
        if health_pct < 1:
        	pg.draw.rect(self.image, col, health_bar)

    def killed(self):
    	# called when mob dies
    	self.game.score += self.point_worth # add to score
        choice(self.game.zombie_hit_sounds).play()
        self.kill() # remove sprite from group
        self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))

    def change_face(self):
        if -135 <= self.rot <= -45:
        	self.face = 'down'
        if 45 <= self.rot <= 135:
        	self.face = 'up'
        if 0 < self.rot < 45 or -45 < self.rot <= 0:
        	self.face = 'right'
        if -180 < self.rot <= -135 or 135 < self.rot < 179:
        	self.face = 'left'

    def update(self):
    	'''
    	 * PUT THE DAMAGE STUFF OUTSIDE THE IF STATEMENT * 
    	'''
        # updates all necessary values
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < self.mob_data['detect_radius']**2:
            if random() < 0.002:
                choice(self.game.zombie_moan_sounds).play()
            self.moving = True
            self.rot = target_dist.angle_to(vec(1, 0)) # angle between player and mob
            self.change_face()

            self.image = self.image.copy()

            # update mob position
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mobs()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2

            # collision detection
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center

        else:
            self.moving = False

        # mob death
        if self.health <= 0:
        	self.killed()

        # check to change sprite
        if (self.moving and pg.time.get_ticks() - self.last_sprite_change > 100) or self.damaged:
            self.last_sprite_change = pg.time.get_ticks()
            #self.which_sprite = 1 - self.which_sprite
            self.sprite_change()

        self.image = self.image.copy()

        if self.damaged:
        	try:
        		# special flags in pygame
        		self.image.fill((255, 255, 255, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
        	except:
        		self.damaged = False # exception raised

class Trooper(Mob):
    def __init__(self, game, x, y, type):
        Mob.__init__(self, game, x, y, type) # call mob class init
        self.weapon_data = WEAPONS[type]
        self.last_shoot = time.time()
        self.point_worth = 2

    def shoot(self):
    	# shoot method
        if time.time() - self.last_shoot > self.weapon_data['rate']:
            self.last_shoot = time.time()
            pos = self.pos + vec(10, 10).rotate(-self.rot)
            dir = vec(1, 0).rotate(-self.rot)
            MobBullet(self.game, pos, dir, self.weapon_data['damage'], self.rot, 'trooper')

    def update(self):
        super(Trooper, self).update() # call mob class update
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < self.mob_data['detect_radius']**2:
            self.shoot()

class Demon(Mob):
	def __init__(self, game, x, y, type):
		Mob.__init__(self, game, x, y, type)
		self.weapon_data = WEAPONS[type]
		self.last_shoot = time.time()
		self.point_worth = 3

	def shoot(self):
		if time.time() - self.last_shoot > self.weapon_data['rate']:
			self.last_shoot = time.time()
			# dude has a shotgun
			for i in range(self.weapon_data['bullet_count']):
				pos = self.pos + vec(10, 10).rotate(-self.rot)
				dir = vec(1, 0).rotate(-self.rot)
				spread = uniform(-self.weapon_data['spread'], self.weapon_data['spread'])
				MobBullet(self.game, pos, dir.rotate(spread), self.weapon_data['damage'], self.rot, 'demon') # Spawn bullet

	def update(self):
		super(Demon, self).update()
		target_dist = self.target.pos - self.pos
		if target_dist.length_squared() < self.mob_data['detect_radius']**2:
			self.shoot()

class Level1(Mob):
    def __init__(self, game, x, y):
    	# initialise variables
    	# takes game class, x and y coordinates
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.boss_img[0]
        self.mob_data = BOSS['level1']
        self.weapon_data = WEAPONS['level1']

        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect.copy()
        self.rect.center = self.pos
        self.hit_rect.center = self.rect.center
        self.rot = 0
        self.health = self.mob_data['health']
        self.speed = self.mob_data['speed']
        self.target = game.player
        self.last_shoot = time.time()
        self.point_worth = 10
        self.damaged = False

    def shoot(self):
    	# shoot method
        if time.time() - self.last_shoot > self.weapon_data['rate']:
            self.last_shoot = time.time()
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.pos + vec(10, 10).rotate(-self.rot)
            MobBullet(self.game, pos, dir, self.weapon_data['damage'], self.rot, 'level1')
            pos = self.pos + vec(10, -15).rotate(-self.rot)
            MobBullet(self.game, pos, dir, self.weapon_data['damage'], self.rot, 'level1')

    def update(self):
        #updates all necessary values
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < self.mob_data['detect_radius']**2:
            if random() < 0.002:
                choice(self.game.zombie_moan_sounds).play()
            self.rot = target_dist.angle_to(vec(1, 0)) #angle between player and mob
            self.shoot()            
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mobs()

            self.image = self.image.copy()

            if self.damaged:
	            try:
	                # special flags in pygame you can use
	                self.image.fill((255, 255, 255, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
	            except:
	                self.damaged = False # exception is raised

            # update position
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2

            # collision detection
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
            self.image = pg.transform.rotate(self.game.boss_img[0], self.rot)

            if self.health <= 0:
            	self.killed()

class Bullet(pg.sprite.Sprite):
    # initialise as a sprite
    def __init__(self, game, pos, dir, damage, angle):
        # initialise values
        # game is game class, pos is x and y integer coodinates, dir is integer for bullet with spread and angle is integer for angle of bullet
        self.game = game
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        #self.image = game.bullet_images[WEAPONS[game.player.weapon]['bullet_size']]
        self.image = game.bullet_images[game.player.weapon]
        self.image = pg.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed'] * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage

    def update(self):
        # updates bullet position
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        # self.kill() removes sprite from screen if hit
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon]['bullet_lifetime']: # change this for the boss shooting
            self.kill()

class MobBullet(Bullet):
    def __init__(self, game, pos, dir, damage, angle, type):
        self.game = game
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.mob_bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = game.bullet_images[type]
        self.image = pg.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.type = type
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir * WEAPONS[type]['bullet_speed'] * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage

    def update(self):
        # update bullet position
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        # self.kill() removes sprite from screen if hit
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.type]['bullet_lifetime']: # change this for the boss shooting
            self.kill()

class Obstacle(pg.sprite.Sprite):
    # initialise as sprite
    def __init__(self, game, x, y, w, h):
        # game is game class, x and y integer coordinates and w = width and h = height
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class Exit(pg.sprite.Sprite):
	def __init__(self, game, x, y, w, h):
		self.groups = game.exit
		pg.sprite.Sprite.__init__(self, self.groups)
		self.rect = pg.Rect(x, y, w, h)
		self.x = x
		self.y = y
		self.rect.x = x
		self.rect.y = y

# Will somewhat implement later
'''class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(20, 50)
        self.image = pg.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION: # effect duration check
            self.kill()'''

class Item(pg.sprite.Sprite):
    # initialise as sprite
    def __init__(self, game, pos, type):
        # game is game class, pos is integer of position and type is string of which item
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.type = type
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        # update necessary values
        # Not my code. Looked cool from the tutorial I watched
        # bobbing motion
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1

class Ability(pg.sprite.Sprite): # POSSIBLY CHANGE TO HAVE THE PLAYER GET KEYS METHOD
    # initialise as sprite
    def __init__(self, player, game):
        # player is player class and game is game class
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.player = player
        self.game = game
        self.pos = self.player.pos
        self.char = self.player.char
        self.image = game.ability_images[self.char]
        self.player_img = self.player.image
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect = self.rect
        self.spawn_time = time.time()
        self.time_in = time.time()

    def add_health(self):
        # method that determines how fast the character gains health and how much health is gained
        '''if time.time() - self.time_in > PLAYERS[self.char]['e_gain_rate']:
            self.time_in = time.time()
            if self.player.health + PLAYERS[self.char]['e_health_gain'] >= PLAYERS[self.char]['health']:
                self.player.health = PLAYERS[self.char]['health']
            else:
                self.player.health += PLAYERS[self.char]['e_health_gain']'''
        if self.player.health + PLAYERS[self.char]['e_health_gain'] >= PLAYERS[self.char]['health']:
        	self.player.health = PLAYERS[self.char]['health']
        else:
        	self.player.health += PLAYERS[self.char]['e_health_gain']


    def update(self):
        # different pygame collide functions based on character
        if self.char == 'mage':
            hits = pg.sprite.collide_rect(self, self.player)
            if hits:
            	if time.time() - self.time_in > PLAYERS[self.char]['e_gain_rate']:
            		self.time_in = time.time()
                	self.add_health()

        if self.char == 'knight':
            self.rect.center = self.player.rect.center
            hits = pg.sprite.spritecollide(self, self.game.mob_bullets, True)
            for hit in hits:
                self.add_health()

            hits = pg.sprite.spritecollide(self, self.game.mobs, False, collide_hit_rect)
            for mob in hits:
                self.add_health()
                mob.vel = vec(0, 0) # slows down mob when entering shield

        if self.char == 'ninja' and self.game.mob_hit:
        	self.add_health()

        # removes the sprite from the screen if the time of ability is up
        if time.time() - self.spawn_time > PLAYERS[self.char]['e_length']:
            self.player.ability_active = False
            self.player.seconds_string = PLAYERS[self.char]['e_cooldown'] # set ability time string to the cooldown of the chars ability
            self.player.last_ability = time.time()
            self.kill() # despawn the ability