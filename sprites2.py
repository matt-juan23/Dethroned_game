# Sprites classes for game
import pygame as pg
import pytweening as tween
from random import uniform, choice, randint, random
from settings import *
from tilemap import *
from itertools import chain
vec = pg.math.Vector2

def collide_with_walls(sprite, group, dir): 
	# Not my code
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
		self.vx, self.vy = 0, 0
		self.vel = vec(self.vx, self.vy)
		self.pos = vec(x, y) 
		self.rot = 0
		self.last_shot = 0
		self.last_reload = 0
		self.last_dodge = 0
		self.last_sprite_change = 0
		self.last_ability = 0
		self.last_lvlup = 0
		self.camera = Camera(game.map.width, game.map.height)
		self.weapon = PLAYERS[self.char]['weapon']
		self.health = PLAYERS[self.char]['health']
		self.weapon_data = WEAPONS[self.weapon]
		self.player_data = PLAYERS[self.char] 
		self.ammo_count = WEAPONS[self.weapon]['ammo_count']
		self.full_ammo = WEAPONS[self.weapon]['ammo_count']
		self.damaged = False
		self.reloading = False
		self.moving = False
		self.face = 0
		self.lvlup = False
		self.power = ''
		self.which_sprite = 0

	def get_keys(self):
		# called repeatedly to check for which keys are pressed
		# This method is for keys being held
		# single press is in the events method in main.py
		# set values in case nothing gets set to it
		self.vx, self.vy = 0, 0
		self.rot_speed = 0
		keys = pg.key.get_pressed()
		self.face = 'down'

		# Check if arrow key is pressed and set values accordingly
		# Should convert this to function to avoid repetition
		if keys[pg.K_UP]:
			self.vy = -self.player_data['speed']
			self.face = 'up' 
			self.moving = True
		if keys[pg.K_DOWN]:
			self.vy = self.player_data['speed']
			self.face = 'down' 
			self.moving = True
		if keys[pg.K_RIGHT]:
		    self.vx = self.player_data['speed']
		    self.face = 'right' 
		    self.moving = True
		if keys[pg.K_LEFT]:
			self.vx = -self.player_data['speed']
			self.face = 'left' 
			self.moving = True
		# Diagonal movemnt
		if self.vx != 0 and self.vy != 0:
			self.vx *= 0.7071
			self.vy *= 0.7071
		if self.vx == 0 and self.vy == 0:
			self.moving = False
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

		# Sprite change if condition
		if self.moving and pg.time.get_ticks() - self.last_sprite_change > 100:
			self.last_sprite_change = pg.time.get_ticks()
			self.which_sprite = 1 - self.which_sprite # switch between 1 and 0
			self.sprite_change()

	def dodge(self): # allows to phase through walls
		# function called when space is hit
		# shifts character certain distance in a direction determined by self.face string
		now = pg.time.get_ticks()
		if now - self.last_dodge > self.player_data['dodge_time']:
			self.last_dodge = now
			if self.face == 'up':
				self.vy -= self.player_data['dodge_dist']
			if self.face == 'down':
				self.vy += self.player_data['dodge_dist']
			if self.face == 'left':
				self.vx -= self.player_data['dodge_dist']
			if self.face == 'right':
				self.vx += self.player_data['dodge_dist']

	def reload(self):
		# reload function
		self.last_reload = pg.time.get_ticks()
		self.reloading = True
		self.ammo_count = self.full_ammo # sets ammo back to full

	def shoot(self, rot):
		# shoot function
		self.image = self.game.player_img[self.char][self.face][0] # change sprite to face in shooting direction
		now = pg.time.get_ticks()
		if now - self.last_shot > self.weapon_data['rate']:
			self.ammo_count -= 1
			self.last_shot = now
			dir = vec(1, 0).rotate(-rot)
			pos = self.pos + PLAYERS[self.char]['barrel_offset'].rotate(-rot) # offsets where bullet sprite spawns
			self.vel = vec(-self.weapon_data['kickback'], 0).rotate(-rot) # knockback when shooting
			Bullet(self.game, pos, dir, self.weapon_data['damage'], rot)

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

	# Doesn't work at the moment. May exclude from final game
	'''def hit(self): # apply to mobs
		self.damaged = True
		self.damage_alpha = chain(DAMAGE_ALPHA) # 1 flash'''

	def sprite_change(self):
		# called whenever the sprite needs to be changed
		self.image = self.game.player_img[self.char][self.face][self.which_sprite]

	def powerup(self, item):
		# powerup method
		# item is a string that is determined by which powerup is hit
		self.power = item
		if item == 'shotgun':
			self.weapon_data['damage'] *= 2
			self.last_lvlup = pg.time.get_ticks()
		if item == 'jump':
			self.player_data['dodge_dist'] *= 2
			self.last_lvlup = pg.time.get_ticks()

	def e_ability(self):
		# e ability
		if pg.time.get_ticks() - self.last_ability > PLAYERS[self.char]['e_cooldown'] + PLAYERS[self.char]['e_length']: 
			self.last_ability = pg.time.get_ticks()
			Ability(self, self.game)
			'''for bullet in self.game.mob_bullets:
				bullet.kill()''' # idea for clearing all mob bullets off screen

	def update(self):
		# update all necessary values and calls get_keys() subprogram
		# checks if time is up 
		self.vel = vec(self.vx, self.vy)
		#print self.vel
		self.get_keys()
		# Reload timer
		if self.reloading and pg.time.get_ticks() - self.last_reload > self.weapon_data['reload_time']:
			self.reloading = False
		
		# Level up timer
		if pg.time.get_ticks() - self.last_lvlup > 5000 and self.lvlup == True:
			if self.power == 'shotgun':
				self.weapon_data['damage'] /= 2
				self.lvlup = False
			if self.power == 'jump':
				self.player_data['dodge_dist'] /= 2
				self.lvlup = False

	# Other part of def hit()
		'''if self.damaged:
			try:
				# special flags in pygame you can use
				self.image.fill((255, 255, 255, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
			except:
				self.damaged = False # exception is raised'''

		# Update player position
		self.rect = self.image.get_rect()
		self.rect.center = self.pos
		self.pos += self.vel * self.game.dt
		self.hit_rect.centerx = self.pos.x
		# Collision detection
		# Need to update to work with jump
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
        self.rect = self.image.get_rect()
        #self.rect.center = (x, y)
        self.hit_rect = self.rect.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.dir = 'down'
        self.rot = 0
        self.which_sprite = 0
        self.last_sprite_change = 0
        self.health = self.mob_data['health']
        self.speed = choice(self.mob_data['speed'])
        self.target = game.player
        self.moving = False

    def avoid_mobs(self): 
    	# avoids mobs stacking on top of each other
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < self.mob_data['avoid_radius']:
                    self.acc += dist.normalize()

    def sprite_change(self):
    	# called when sprite needs to be changed
    	self.image = self.game.mob_img[self.enemy_type][self.dir][self.which_sprite]

    def update(self):
    	# updates all necessary values
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < self.mob_data['detect_radius']**2:
            if random() < 0.002:
                choice(self.game.zombie_moan_sounds).play()
            self.moving = True
            self.rot = target_dist.angle_to(vec(1, 0)) # angle between player and mob
            #Convert to function
            if -135 <= self.rot <= -45:
            	self.dir = 'down'
            if 45 <= self.rot <= 135:
            	self.dir = 'up'
            if 0 < self.rot < 45 or -45 < self.rot <= 0:
            	self.dir = 'right'
            if -180 < self.rot <= -135 or 135 < self.rot < 179:
            	self.dir = 'left'

            if self.moving and pg.time.get_ticks() - self.last_sprite_change > 100:
            	self.last_sprite_change = pg.time.get_ticks()
            	self.which_sprite = 1 - self.which_sprite
            	self.sprite_change()

            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mobs()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center

        else:
        	self.moving = False

        if self.health <= 0:
            choice(self.game.zombie_hit_sounds).play()
            self.kill()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))

        self.image = self.image.copy() # used for drawing appropriate health bar for each mob

    def draw_health(self):
    	# draws health of each mob on top of sprite
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / self.mob_data['health'])
        if width < 0:
        	width = 0
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < self.mob_data['health']:
            pg.draw.rect(self.image, col, self.health_bar)

class Trooper(Mob):
	def __init__(self, game, x, y, type):
		Mob.__init__(self, game, x, y, type)
		self.last_shoot = 0

	def shoot(self):
		now = pg.time.get_ticks()
		if now - self.last_shoot > 1000:
			self.last_shoot = now
			pos = self.pos + vec(10, 10).rotate(-self.rot)
			dir = vec(1, 0).rotate(-self.rot)
			MobBullet(self.game, pos, dir, 10, self.rot)

	def update(self):
		# updates all necessary values
		target_dist = self.target.pos - self.pos
		if target_dist.length_squared() < self.mob_data['detect_radius']**2:
			if random() < 0.002:
				choice(self.game.zombie_moan_sounds).play()
			self.moving = True
			self.rot = target_dist.angle_to(vec(1, 0)) # angle between player and mob
			#Convert to function
			if -135 <= self.rot <= -45:
				self.dir = 'down'
			if 45 <= self.rot <= 135:
				self.dir = 'up'
			if 0 < self.rot < 45 or -45 < self.rot <= 0:
				self.dir = 'right'
			if -180 < self.rot <= -135 or 135 < self.rot < 179:
				self.dir = 'left'

			if self.moving and pg.time.get_ticks() - self.last_sprite_change > 100:
				self.last_sprite_change = pg.time.get_ticks()
				self.which_sprite = 1 - self.which_sprite
				self.sprite_change()

			self.rect.center = self.pos
			self.acc = vec(1, 0).rotate(-self.rot)
			self.avoid_mobs()
			self.acc.scale_to_length(self.speed)
			self.acc += self.vel * -1
			self.vel += self.acc * self.game.dt
			self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
			self.hit_rect.centerx = self.pos.x
			collide_with_walls(self, self.game.walls, 'x')
			self.hit_rect.centery = self.pos.y
			collide_with_walls(self, self.game.walls, 'y')
			self.rect.center = self.hit_rect.center

			self.shoot() # can shoot diagonal. not sure if i should keep it that way

		else:
			self.moving = False

		if self.health <= 0:
			choice(self.game.zombie_hit_sounds).play()
			self.kill()
			self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))

		self.image = self.image.copy() # used for drawing appropriate health bar for each mob

class Boss(Mob):
	def __init__(self, game, x, y, type):
		self._layer = MOB_LAYER
		self.groups = game.all_sprites, game.mobs
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.image = game.boss_img[0]
		self.mob_data = BOSS['level1'] # make dictionary
		self.rect = self.image.get_rect()
		self.hit_rect = self.rect.copy()
		self.hit_rect.center = self.rect.center
		self.pos = vec(x, y)
		self.vel = vec(0, 0)
		self.rect.center = self.pos
		self.rot = 0
		self.health = self.mob_data['health']
		self.speed = self.mob_data['speed']
		self.target = game.player
		self.last_shoot = 0

	def shoot(self):
		now = pg.time.get_ticks()
		if now - self.last_shoot > 1000:
			self.last_shoot = now
			dir = vec(1, 0).rotate(-self.rot)
			pos = self.pos + vec(10, 10).rotate(-self.rot)
			MobBullet(self.game, pos, dir, 10, self.rot)
			pos = self.pos + vec(10, -15).rotate(-self.rot)
			MobBullet(self.game, pos, dir, 10, self.rot)

	def update(self):
		#updates all necessary values
		target_dist = self.target.pos - self.pos
		if target_dist.length_squared() < self.mob_data['detect_radius']**2:
			if random() < 0.002:
				choice(self.game.zombie_moan_sounds).play()
			self.rot = target_dist.angle_to(vec(1, 0)) #angle between player and mob
			'''#convert to function
			if -135 <= self.rot <= -45:
				self.dir = 'down'
			if 45 <= self.rot <= 135:
				self.dir = 'up'
			if 0 < self.rot < 45 or -45 < self.rot <= 0:
				self.dir = 'right'
			if -180 < self.rot <= -135 or 135 < self.rot < 180:
				self.dir = 'left'''

			self.shoot()            
			self.rect.center = self.pos
			self.acc = vec(1, 0).rotate(-self.rot)
			self.avoid_mobs()
			self.acc.scale_to_length(self.speed)
			self.acc += self.vel * -1
			self.vel += self.acc * self.game.dt
			self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
			self.hit_rect.centerx = self.pos.x
			collide_with_walls(self, self.game.walls, 'x')
			self.hit_rect.centery = self.pos.y
			collide_with_walls(self, self.game.walls, 'y')
			self.rect.center = self.hit_rect.center
			self.image = pg.transform.rotate(self.game.boss_img[0], self.rot)

			'''self.rect.center = self.pos
			self.hit_rect.centerx = self.pos.x
			self.hit_rect.centery = self.pos.y
			self.rect.center = self.hit_rect.center'''

			if self.health <= 0:
				choice(self.game.zombie_moan_sounds).play()
				self.kill()
				self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))

			self.image = self.image.copy() # used for drawing appropriate health bar for each mob

class Bullet(pg.sprite.Sprite):
	# initialise as a sprite
	def __init__(self, game, pos, dir, damage, angle):
		# initialise values
		# game is game class, pos is x and y integer coodinates, dir is integer for bullet with spread and angle is integer for angle of bullet
		self.game = game
		self._layer = BULLET_LAYER
		self.groups = game.all_sprites, game.bullets
		pg.sprite.Sprite.__init__(self, self.groups)
		self.image = game.bullet_images[WEAPONS[game.player.weapon]['bullet_size']]
		self.image = pg.transform.rotate(self.image, angle)
		self.rect = self.image.get_rect()
		self.hit_rect = self.rect
		self.pos = vec(pos)
		self.rect.center = pos
		self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed'] * uniform(0.9, 1.1)
		self.spawn_time = pg.time.get_ticks()
		self.damage = damage

	def update(self):
		# updates necessary values
		self.pos += self.vel * self.game.dt
		self.rect.center = self.pos
		# self.kill() removes sprite from screen if hit
		if pg.sprite.spritecollideany(self, self.game.walls):
			self.kill()
		if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon]['bullet_lifetime']: # change this for the boss shooting
			self.kill()

class MobBullet(Bullet):
	def __init__(self, game, pos, dir, damage, angle):
		#Bullet.__init__(self, game, pos, dir, damage, angle)
		#self.groups = game.all_sprites, game.mob_bullets
		self.game = game
		self._layer = BULLET_LAYER
		self.groups = game.all_sprites, game.mob_bullets
		pg.sprite.Sprite.__init__(self, self.groups)
		self.image = game.boss_bullet
		self.image = pg.transform.rotate(self.image, angle)
		self.rect = self.image.get_rect()
		self.hit_rect = self.rect
		self.pos = vec(pos)
		self.rect.center = pos
		self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed'] * uniform(0.9, 1.1)
		self.spawn_time = pg.time.get_ticks()
		self.damage = damage

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

class Ability(pg.sprite.Sprite):
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
		self.rect = self.image.get_rect()
		self.rect.center = self.pos
		self.hit_rect = self.rect
		self.spawn_time = pg.time.get_ticks()
		self.time_in = 0

	def update(self):
		if self.char == 'mage':
			hits = pg.sprite.collide_rect(self, self.player)
			if hits:
				if pg.time.get_ticks() - self.time_in > 1000:
					self.time_in = pg.time.get_ticks()
					if self.player.health >= PLAYERS[self.char]['health']:
						self.player.health = PLAYERS[self.char]['health']
					else:
						self.player.health += 30

		if self.char == 'knight':
			self.rect.center = self.player.rect.center
			hits = pg.sprite.spritecollide(self, self.game.mob_bullets, True)
			for hit in hits:
				if self.player.health >= PLAYERS[self.char]['health']:
					self.player.health = PLAYERS[self.char]['health']
				else:
					self.player.health += 30

			hits = pg.sprite.spritecollide(self, self.game.mobs, False, collide_hit_rect)
			for mob in hits:
				if self.player.health >= PLAYERS[self.char]['health']:
					self.player.health = PLAYERS[self.char]['health']
				else:
					self.player.health += 30

				mob.vel = vec(0, 0) # slows down mob when entering shield

		# will implement an ability for each character later
		if pg.time.get_ticks() - self.spawn_time > PLAYERS[self.char]['e_length']:
			self.kill()