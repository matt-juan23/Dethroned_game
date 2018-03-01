# Sprites classes for game
import pygame as pg
import pytweening as tween
from random import uniform, choice, randint, random
from settings import *
from tilemap import *
from itertools import chain
vec = pg.math.Vector2

def collide_with_walls(sprite, group, dir):
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

class Player(pg.sprite.Sprite): 
	def __init__(self, game, x, y, char):
		self._layer = PLAYER_LAYER
		self.groups = game.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.char = char
		self.image = game.player_img[self.char]['down'][0]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.hit_rect = PLAYER_HIT_RECT
		self.hit_rect.center = self.rect.center
		self.vx, self.vy = 0, 0
		self.vel = vec(self.vx, self.vy)
		self.pos = vec(x, y) 
		self.rot = 0
		self.last_shot = 0
		self.last_reload = 0
		self.last_dodge = 0
		self.last_sprite_change = 0
		self.camera = Camera(game.map.width, game.map.height)
		self.weapon = PLAYERS[self.char]['weapon']
		self.health = PLAYERS[self.char]['health']
		self.weapon_data = WEAPONS[self.weapon]
		self.player_data = PLAYERS[self.char] 
		self.damaged = False
		self.reloading = False
		self.moving = False
		self.count = 0
		self.face = 0
		self.lvlup = False
		self.last_lvlup = 0
		self.power = '' # Make variables for weapon and player
		self.which_sprite = 0

	def get_keys(self):
		self.vx, self.vy = 0, 0
		self.rot_speed = 0
		ammo = self.weapon_data['ammo_count']
		keys = pg.key.get_pressed()
		self.face = 'down'
		if keys[pg.K_UP]:
			self.vy = -self.player_data['speed']
			self.face = 'up' #3
			self.rot = 90
			self.moving = True
		if keys[pg.K_DOWN]:
			self.vy = self.player_data['speed']
			self.face = 'down' #2
			self.rot = 270
			self.moving = True
		if keys[pg.K_RIGHT]:
		    self.vx = self.player_data['speed']
		    self.face = 'right' #0
		    self.rot = 0
		    self.moving = True
		if keys[pg.K_LEFT]:
			self.vx = -self.player_data['speed']
			self.face = 'left' #1
			self.rot = 180
			self.moving = True
		if self.vx != 0 and self.vy != 0:
			self.vx *= 0.7071
			self.vy *= 0.7071
		if self.vx == 0 and self.vy == 0:
			self.moving = False
		if ammo > 0 and self.reloading == False:
			if keys[pg.K_w]:
				self.rot = 90
				self.face = 'up'
				self.shoot()
			elif keys[pg.K_s]:
				self.rot = 270
				self.face = 'down'
				self.shoot()
			elif keys[pg.K_a]:
				self.rot = 180
				self.face = 'left'
				self.shoot()
			elif keys[pg.K_d]:
				self.rot = 0
				self.face = 'right'
				self.shoot()

		if keys[pg.K_r] or self.weapon_data['ammo_count'] == 0:
			self.reload()

		if keys[pg.K_SPACE] and self.moving == True:
			now = pg.time.get_ticks()
			if now - self.last_dodge > self.player_data['dodge_time']:
				self.last_dodge = now
				self.dodge()

		if self.moving and pg.time.get_ticks() - self.last_sprite_change > 100:
			self.last_sprite_change = pg.time.get_ticks()
			self.which_sprite = 1 - self.which_sprite
			self.sprite_change()

	def dodge(self):
		if self.face == 'up':
			self.vy -= self.player_data['dodge_dist']
		if self.face == 'down':
			self.vy += self.player_data['dodge_dist']
		if self.face == 'left':
			self.vx -= self.player_data['dodge_dist']
		if self.face == 'right':
			self.vx += self.player_data['dodge_dist']

	def reload(self):
		self.last_reload = pg.time.get_ticks()
		self.reloading = True
		self.weapon_data['ammo_count'] += self.count
		self.count = 0

	def shoot(self):
		self.image = self.game.player_img[self.char][self.face][0]
		now = pg.time.get_ticks()
		if now - self.last_shot > self.weapon_data['rate']:
			self.last_shot = now
			dir = vec(1, 0).rotate(-self.rot)
			pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
			self.vel = vec(-self.weapon_data['kickback'], 0).rotate(-self.rot)
			for i in range(self.weapon_data['bullet_count']):
				spread = uniform(-self.weapon_data['spread'], self.weapon_data['spread'])
				Bullet(self.game, pos, dir.rotate(spread), self.weapon_data['damage'], self.rot)
				snd = choice(self.game.weapon_sounds[self.weapon])
				if snd.get_num_channels() > 2:
					snd.stop()
				snd.play()
			MuzzleFlash(self.game, pos)
			self.weapon_data['ammo_count'] -= 1
			self.count += 1

	def hit(self): # apply to mobs
		self.damaged = True
		self.damage_alpha = chain(DAMAGE_ALPHA) # 1 flash

	def sprite_change(self):
		self.image = self.game.player_img[self.char][self.face][self.which_sprite]
		'''if pg.time.get_ticks() - self.last_sprite_change > 240:
			self.last_sprite_change = pg.time.get_ticks()
			self.image = self.game.player_img[self.char][self.face][1]
		else:
			self.image = self.game.player_img[self.char][self.face][0]'''

	def powerup(self, item):
		self.power = item
		if item == 'shotgun':
			self.weapon_data['damage'] *= 2
			self.last_lvlup = pg.time.get_ticks()
		if item == 'jump':
			self.player_data['dodge_dist'] *= 2
			self.last_lvlup = pg.time.get_ticks()

	def update(self):
		self.vel = vec(self.vx, self.vy)
		self.get_keys()
		if self.reloading and pg.time.get_ticks() - self.last_reload > self.weapon_data['reload_time']:
			self.reloading = False
			
		if pg.time.get_ticks() - self.last_lvlup > 5000 and self.lvlup == True:
			if self.power == 'shotgun':
				self.weapon_data['damage'] /= 2
				self.lvlup = False
			if self.power == 'jump':
				self.player_data['dodge_dist'] /= 2
				self.lvlup = False
		'''if self.damaged:
			try:
				# special flags in pygame you can use
				self.image.fill((255, 255, 255, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
			except:
				self.damaged = False # exception is raised'''
		self.rect = self.image.get_rect()
		self.rect.center = self.pos
		self.pos += self.vel * self.game.dt
		self.hit_rect.centerx = self.pos.x
		collide_with_walls(self, self.game.walls, 'x')
		self.hit_rect.centery = self.pos.y
		collide_with_walls(self, self.game.walls, 'y')
		self.rect.center = self.hit_rect.center

class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = MOB_HEALTH
        self.speed = choice(MOB_SPEEDS)
        self.target = game.player

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update(self):
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < DETECT_RADIUS**2:
            if random() < 0.002:
                choice(self.game.zombie_moan_sounds).play()
            self.rot = target_dist.angle_to(vec(1, 0))
            self.image = pg.transform.rotate(self.game.mob_img, self.rot)
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
        if self.health <= 0:
            choice(self.game.zombie_hit_sounds).play()
            self.kill()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))

    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        if width < 0:
        	width = 0
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)

class Bullet(pg.sprite.Sprite):
	def __init__(self, game, pos, dir, damage, angle):
		self._layer = BULLET_LAYER
		self.groups = game.all_sprites, game.bullets
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.image = game.bullet_images[WEAPONS[game.player.weapon]['bullet_size']]
		self.image = pg.transform.rotate(self.image, angle)
		self.rect = self.image.get_rect()
		self.hit_rect = self.rect
		self.pos = vec(pos)
		self.rect.center = pos
		#spread = uniform(-GUN_SPREAD, GUN_SPREAD)
		self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed'] * uniform(0.9, 1.1)
		self.spawn_time = pg.time.get_ticks()
		self.damage = damage

	def update(self):
		self.pos += self.vel * self.game.dt
		self.rect.center = self.pos
		if pg.sprite.spritecollideany(self, self.game.walls):
			self.kill()
		if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon]['bullet_lifetime']:
			self.kill()

class Wall(pg.sprite.Sprite):
	def __init__(self, game, x, y):
		self._layer = WALL_LAYER
		self.groups = game.all_sprites, game.walls
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.image = game.wall_img
		self.rect = self.image.get_rect()
		self.x = x
		self.y = y
		self.rect.x = x * TILESIZE
		self.rect.y = y * TILESIZE

class Obstacle(pg.sprite.Sprite):
	def __init__(self, game, x, y, w, h):
		self.groups = game.walls
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.rect = pg.Rect(x, y, w, h)
		self.x = x
		self.y = y
		self.rect.x = x
		self.rect.y = y

class MuzzleFlash(pg.sprite.Sprite):
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
			self.kill()

class Item(pg.sprite.Sprite):
	def __init__(self, game, pos, type):
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
		# bobbing motion
		offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
		self.rect.centery = self.pos.y + offset * self.dir
		self.step += BOB_SPEED
		if self.step > BOB_RANGE:
			self.step = 0
			self.dir *= -1
