# Sprites File
import pygame as pg
import time
from random import uniform, choice, randint, random
from settings import *
from tilemap import *
from itertools import chain
vec = pg.math.Vector2

# handles colliding with walls
# Input: sprite, walls group and direction of collision
# Author: KidsCanCode
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

# hit_rect collision detection
# takes two sprites and returns whether the hit_rects collide
# Author: KidsCanCode
def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

# All classes take pg.sprite.Sprite which signifies that it is a Pygame sprite
# All subprograms have a parameter of self which allows attributes to be accessed throughout the whole class

# Player class
# Author: KidsCanCode, me
class Player(pg.sprite.Sprite):
    # initialise variables to be used in class
    # Input: game class from main file, x and y coordinates of spawn point and character selected as string
    # Author: KidsCanCode, me
    def __init__(self, game, x, y, char):
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

        #time initialising
        time_now = time.time() # gets current time
        self.last_shot = time_now
        self.last_reload = time_now
        self.last_dodge = time_now # change to time.time()
        self.last_sprite_change = time_now
        self.last_ability = time_now

        # player and weapon data initialise
        self.weapon = PLAYERS[self.char]['weapon']
        self.health = PLAYERS[self.char]['health']
        self.weapon_data = WEAPONS[self.weapon] 
        self.ammo_count = WEAPONS[self.weapon]['ammo_count']
        self.full_ammo = WEAPONS[self.weapon]['ammo_count']
        self.player_data = PLAYERS[self.char]
        self.ability_uses = PLAYERS[self.char]['e_uses']
        self.face = 'down'
        self.dir_move = 'down'

        # boolean intialising
        self.damaged = False
        self.reloading = False
        self.moving = False
        self.ability_active = False
        self.which_sprite = 0

        self.seconds_string = self.player_data['e_cooldown'] # string for ability timer
        self.seconds_timer = time_now # timer for ability seconds

        self.mouse_offset_pos = 0

    # called repeatedly to check for which keys are pressed
    # this method are for keys being held
    # Author: KidsCanCode, me
    def get_keys(self):
        # set values in case nothing gets set to it
        self.vel_x, self.vel_y = 0, 0

        keys = pg.key.get_pressed()
        mouse_click = pg.mouse.get_pressed() # check for mouse button press
        mouse_raw_pos = vec(pg.mouse.get_pos()) # initialise a vector of the mouse position
        self.mouse_offset_pos = mouse_raw_pos - vec(self.game.camera.camera.topleft) # offset the mouse position for scrolling map

        # Conditions for shooting. mouse_click[0] is left mouse button
        if self.ammo_count > 0 and self.reloading == False and mouse_click[0]:
            self.shoot()

        # Keys for moving
        if keys[pg.K_w]:
            self.vel_y = -self.player_data['speed']
            self.dir_move = 'up' 
        if keys[pg.K_s]:
            self.vel_y = self.player_data['speed']
            self.dir_move = 'down' 
        if keys[pg.K_d]:
            self.vel_x = self.player_data['speed']
            self.dir_move = 'right'
        if keys[pg.K_a]:
            self.vel_x = -self.player_data['speed']
            self.dir_move = 'left'

        # Diagonal movement
        if self.vel_x != 0 and self.vel_y != 0:
            self.vel_x *= 0.7071
            self.vel_y *= 0.7071

        if self.vel_x == 0 and self.vel_y == 0:
            self.moving = False # set moving to false when player is not moving
        else:
            self.moving = True

        # Reload
        if (keys[pg.K_r] and self.ammo_count != self.full_ammo) or self.ammo_count == 0:
            self.reload()

        # E ability
        if keys[pg.K_e]:
            self.e_ability()

        # Dodge
        if keys[pg.K_SPACE] and self.moving:
            self.dodge()

    # changes the value of self.face based on the value of self.rot
    # Author: me
    def change_face(self):
        if -135 <= self.rot <= -45:
            self.face = 'down'
        if 45 <= self.rot <= 135:
            self.face = 'up'
        if 0 < self.rot < 45 or -45 < self.rot <= 0:
            self.face = 'right'
        if -180 <= self.rot <= -135 or 135 < self.rot < 179:
            self.face = 'left'

    # Draw player health in the top left corner
    # Author: KidsCanCode, me
    def draw_player_health(self, surf, x, y, pct):
        if pct < 0: # if percentatge is 0
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

    # function called when space is hit
    # moves character certain distance in a direction determined by self.face string
    # Author: KidsCanCode, me
    def dodge(self):
        now = time.time()
        if now - self.last_dodge > self.player_data['dodge_cooldown']:
            self.last_dodge = now
            # Thanks Nathan
            if self.dir_move == 'up':
                self.vel_y -= self.player_data['dodge_dist']
            if self.dir_move == 'down':
                self.vel_y += self.player_data['dodge_dist']
            if self.dir_move == 'left':
                self.vel_x -= self.player_data['dodge_dist']
            if self.dir_move == 'right':
                self.vel_x += self.player_data['dodge_dist']

    # reloads user's weapon
    def reload(self):
        self.last_reload = time.time()
        self.reloading = True
        self.ammo_count = self.full_ammo # sets ammo back to full

    # user shoots 
    def shoot(self):
        self.image = self.game.player_img[self.char][self.face][0] # change sprite to face in shooting direction
        if time.time() - self.last_shot > self.weapon_data['rate']:
            self.ammo_count -= 1
            self.last_shot = time.time()
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.pos + PLAYERS[self.char]['barrel_offset'][self.face].rotate(-self.rot) # offsets where bullet sprite spawns
            Bullet(self.game, pos, dir, self.weapon_data['damage'], self.rot) # spawn bullet

            # play sound
            snd = choice(self.game.weapon_sounds[self.player_data['id']])
            if snd.get_num_channels() > 2:
                snd.stop()
            snd.play()

    # Sets variables for flash effect when hit
    # Author: KidsCanCode
    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA) # 1 flash

    # changes sprite
    # Author: KidsCanCode, me
    def sprite_change(self):
        self.which_sprite = 1 - self.which_sprite
        self.image = self.game.player_img[self.char][self.face][self.which_sprite]

    # Spawns ability
    # Author: KidsCanCode, me
    def e_ability(self):
        if time.time() - self.last_ability > self.player_data['e_cooldown'] and self.ability_active == False and self.ability_uses > 0: 
            self.ability_active = True
            self.ability_uses -= 1
            self.last_ability = time.time()

            # spawn ability
            Ability(self, self.game)

    # draws the time left for the ability to be active
    # Author: KidsCanCode, me
    def draw_ability_bar(self):
        if self.ability_active:
            # equation for the ability bar to decrease over time
            width = int(self.rect.width * abs(time.time() - self.last_ability - PLAYERS[self.char]['e_length']) / PLAYERS[self.char]['e_length'])
            ability_bar = pg.Rect(0, 0, width, 7)
            pg.draw.rect(self.image, GREEN, ability_bar)

    # update the player object and calls get_keys() subprogram
    # Author: KidsCanCode, me
    def update(self):
        self.vel = vec(self.vel_x, self.vel_y)

        self.get_keys()
        dist = self.mouse_offset_pos - self.pos # vector between mouse and player position
        self.rot = dist.angle_to(vec(1, 0)) # angle between player and mouse
        self.change_face()

        # Reload timer
        if self.reloading and time.time() - self.last_reload > self.weapon_data['reload_time']:
            self.reloading = False

        # Sprite change
        if (self.moving and time.time() - self.last_sprite_change > 0.1) or self.damaged:
            self.last_sprite_change = time.time()
            self.sprite_change()

        self.image = self.image.copy() # used for the ability timer to be displayed properly on all sprites

        # update timer for the ability
        if time.time() - self.seconds_timer > 1:
            self.seconds_timer = time.time() # update timer
            self.seconds_string -= 1
            if self.seconds_string < 0:
                self.seconds_string = 0

        if self.damaged:
            try:
                # player image flashes if hit
                self.image.fill((255, 255, 255, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except:
                self.damaged = False

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

# Mouse class
# Author: me
class Mouse(pg.sprite.Sprite):
    # initialises class
    # Author: me
    def __init__(self, game, x, y):
        self._layer = CROSSHAIR_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.crosshair_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.hit_rect = self.rect

    # update mouse object
    # Author: me
    def update(self):
        self.rect = self.image.get_rect()
        self.pos = pg.mouse.get_pos()
        self.rect.center = self.pos
        self.hit_rect = self.rect # so game doesn't crash when in hitbox mode

# Mob super class
# Author: KidsCanCode, me
class Mob(pg.sprite.Sprite):
    # initialises Mob super class
    # Input: game object, x and y coordinates and type of mob as string
    # Author: KidsCanCode, me
    def __init__(self, game, x, y, type):
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
        self.rect.center = self.pos
        self.hit_rect = self.rect.copy()
        self.hit_rect.center = self.rect.center
        self.face = 'down'
        self.rot = 0
        self.which_sprite = 0
        self.last_sprite_change = pg.time.get_ticks()
        self.health = self.mob_data['health']
        self.speed = choice(self.mob_data['speed'])
        self.target = game.player
        self.moving = False
        self.damaged = False
    
    # avoids mobs stacking on top of each other
    # Author: KidsCanCode
    def avoid_mobs(self): 
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < self.mob_data['avoid_radius']:
                    self.acc += dist.normalize()

    # Sets variables for flash effect when hit
    # Author: KidsCanCode
    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA) # 1 flash

    # changes mob image
    # Author: me
    def sprite_change(self):
        self.which_sprite = 1 - self.which_sprite
        self.image = self.game.mob_img[self.enemy_type][self.face][self.which_sprite]

    # draws health of each mob on top of sprite
    # Author: KidsCanCode, me
    def draw_health(self):
        # change color based on health
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

    # called when mob dies
    # Author: KidsCanCode, me
    def killed(self):
        self.game.score += self.point_worth # add to score
        self.game.death_sound.play()
        self.kill() # remove sprite from group

    # Change value of self.face based on self.rot value
    # Author: KidsCanCode, me
    def change_face(self):
        if -135 <= self.rot <= -45:
            self.face = 'down'
        if 45 <= self.rot <= 135:
            self.face = 'up'
        if 0 < self.rot < 45 or -45 < self.rot <= 0:
            self.face = 'right'
        if -180 <= self.rot <= -135 or 135 < self.rot < 179:
            self.face = 'left'

    # updates the mob class
    # Author: KidsCanCode, me
    def update(self):
        target_dist = self.target.pos - self.pos
        # checks whether player is within mob detectrange
        if target_dist.length_squared() < self.mob_data['detect_radius']**2: 
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
                # image flash if hit
                self.image.fill((255, 255, 255, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except:
                self.damaged = False # exception raised

# Brawler sub class
# Author: KidsCanCode, me
class Brawler(Mob):
    # initialises brawler sub class
    # Input: game object, x and y coordinates and type of mob as string 
    def __init__(self, game, x, y, type):
        Mob.__init__(self, game, x, y, type) # initialise super class
        self.point_worth = 1

# Trooper sub class
# Author: KidsCanCode, me
class Trooper(Mob):
    # initialises brawler sub class
    # Input: game object, x and y coordinates and type of mob as string 
    def __init__(self, game, x, y, type):
        Mob.__init__(self, game, x, y, type) # initialise super class
        self.weapon_data = WEAPONS[type]
        self.last_shoot = time.time()
        self.point_worth = 2

    # makes the mob shoots
    def shoot(self):
        if time.time() - self.last_shoot > self.weapon_data['rate']:
            self.last_shoot = time.time()
            pos = self.pos + vec(10, 10).rotate(-self.rot)
            dir = vec(1, 0).rotate(-self.rot)
            MobBullet(self.game, pos, dir, self.weapon_data['damage'], self.rot, 'trooper')

    # calls mob class update and adds the shoot method call
    def update(self):
        super(Trooper, self).update() # call mob class update
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < self.mob_data['detect_radius']**2:
            self.shoot()

# Demon sub class
# Author: KidsCanCode, me
class Demon(Mob):
    # initialises brawler sub class
    # Input: game object, x and y coordinates and type of mob as string 
    def __init__(self, game, x, y, type):
        Mob.__init__(self, game, x, y, type) # initialise super class
        self.weapon_data = WEAPONS[type]
        self.last_shoot = time.time()
        self.point_worth = 5

    # makes the mob shoot
    def shoot(self):
        if time.time() - self.last_shoot > self.weapon_data['rate']:
            self.last_shoot = time.time()
            # dude has a shotgun
            for i in range(self.weapon_data['bullet_count']):
                pos = self.pos + vec(10, 10).rotate(-self.rot)
                dir = vec(1, 0).rotate(-self.rot)
                spread = uniform(-self.weapon_data['spread'], self.weapon_data['spread'])
                MobBullet(self.game, pos, dir.rotate(spread), self.weapon_data['damage'], self.rot, 'demon') # Spawn bullet

    # calls mob class update and adds the shoot method call
    def update(self):
        super(Demon, self).update()
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < self.mob_data['detect_radius']**2:
            self.shoot()

# Boss super class
# Author: KidsCanCode, me
class Boss(Mob):
    # initialises boss super class
    # Input: game object, x and y coordinates and type of mob as string 
    def __init__(self, game, x, y, type):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = type
        self.image = game.boss_images[self.type]
        self.mob_data = BOSS[self.type]
        self.weapon_data = WEAPONS[self.type]

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

    # updates boss object
    def update(self):
        #updates all necessary values
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < self.mob_data['detect_radius']**2:
            self.rot = target_dist.angle_to(vec(1, 0)) #angle between player and mob
            self.shoot()            
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mobs()

            self.image = self.image.copy()

            if self.damaged:
                try:
                    # mob flashes if hit
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
            self.image = pg.transform.rotate(self.game.boss_images[self.type], self.rot)

            if self.health <= 0:
                self.killed()

# Level1 sub class
# Author: KidsCanCode, me
class Level1(Boss):
    # initialises level1 sub class
    # Input: game object, x and y coordinates and type of mob as string 
    # Boss that spawns in level 1
    def __init__(self, game, x, y):
        # takes game class, x and y coordinates as parameters
        type = 'level1'
        Boss.__init__(self, game, x, y, type) # initialise super class

    # makes the boss shoot
    def shoot(self):
        if time.time() - self.last_shoot > self.weapon_data['rate']:
            self.last_shoot = time.time()
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.pos + vec(10, 10).rotate(-self.rot)
            MobBullet(self.game, pos, dir, self.weapon_data['damage'], self.rot, self.type)
            pos = self.pos + vec(10, -15).rotate(-self.rot)
            MobBullet(self.game, pos, dir, self.weapon_data['damage'], self.rot, self.type)

# Level2 sub class
# Author: KidsCanCode, me
class Level2(Boss):
    # initialises level2 sub class
    # Input: game object, x and y coordinates and type of mob as string 
    # Boss that spawns in level 2
    def __init__(self, game, x, y):
        # takes game class, x and y coordinates as parameters
        type = 'level2'
        Boss.__init__(self, game, x, y, type) # initialise super class

    # makes the boss shoot
    def shoot(self):
        if time.time() - self.last_shoot > self.weapon_data['rate']:
            self.last_shoot = time.time()
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.pos + vec(10, 10).rotate(-self.rot)
            MobBullet(self.game, pos, dir, self.weapon_data['damage'], self.rot, self.type)

# Player bullet class
# Author: KidsCanCode, me
class Bullet(pg.sprite.Sprite):
    # initialises bullet class
    # Input: game object, position to spawn, direction facing, damage value and angle to be fired 
    # Author: KidsCanCode, me
    def __init__(self, game, pos, dir, damage, angle):
        self.game = game
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = game.bullet_images[game.player.weapon]
        self.image = pg.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed'] * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage

    # update bullet position
    # Author: KidsCanCode, me
    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        # bullet hits walls
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()

        # bullet lifetime is up
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon]['bullet_lifetime']:
            self.kill()

# Mob bullet class
# Author: KidsCanCode, me
class MobBullet(pg.sprite.Sprite):
    # initialises mobbullet class
    # Input: game object, position to spawn, direction facing, damage value and angle to be fired and type of mob as string
    # Author: KidsCanCode, me
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

    # update bullet position
    # Author: KidsCanCode, me
    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.type]['bullet_lifetime']: # change this for the boss shooting
            self.kill()

# Wall class
# Author: KidsCanCode, me
class Wall(pg.sprite.Sprite):
    # Input: game object, x and y integer coordinates, width and height
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

# Exit class
# Author: KidsCanCode, me
class Exit(pg.sprite.Sprite):
    # initialise exit block which triggers the next level to spawn
# Input: game object, x and y integer coordinates, width and height
    def __init__(self, game, x, y, w, h):
        self.groups = game.exit
        pg.sprite.Sprite.__init__(self, self.groups)
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

# Ability class
# Author: KidsCanCode, me
class Ability(pg.sprite.Sprite):
    # initialise ability variables for the player
    # Input: player and game object
    def __init__(self, player, game):
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

    # adds health to player
    # Author: KidsCanCode, me
    def add_health(self):
        if self.player.health + PLAYERS[self.char]['e_health_gain'] >= PLAYERS[self.char]['health']:
            self.player.health = PLAYERS[self.char]['health']
        else:
            self.player.health += PLAYERS[self.char]['e_health_gain']

    # updates the position and time spawned of ability image
    # Author: KidsCanCode, me
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

        if self.char == 'ninja':
            self.rect.center = self.player.rect.center
            if self.game.mob_hit:
                self.add_health()

        # removes the sprite from the screen if the time of ability is up
        if time.time() - self.spawn_time > PLAYERS[self.char]['e_length']:
            self.player.ability_active = False
            self.player.seconds_string = PLAYERS[self.char]['e_cooldown'] # set ability time string to the cooldown of the chars ability
            self.player.seconds_timer = time.time() # reset timer
            self.player.last_ability = time.time()
            self.kill()
