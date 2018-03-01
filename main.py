# Tile map
import pygame as pg
import sys
from os import path
from pygame.locals import *
from settings import *
from sprites2 import *
from tilemap import *
from random import random, choice

# HUD functions
def draw_player_health(surf, x, y, pct, player):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)

class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 1, 2048) # less lag between shot audiok
        pg.init()
        # Enable this for 60 fps but in full screen
        #flags = FULLSCREEN | DOUBLEBUF
        #self.screen = pg.display.set_mode((WIDTH, HEIGHT), flags)
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()

    def draw_text(self, text, font_name, size, color, x, y, action=None, char=None):
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        if font_name == self.title_font:
            text_rect.height -= 10
        #pg.draw.rect(self.screen, YELLOW, text_rect, 1)
        self.screen.blit(text_surface, text_rect)
        draw_ticks = pg.time.get_ticks()
        if text_rect.collidepoint(mouse) == True and click[0] == 1 and action != None and draw_ticks - self.time_now > 300:
            if char in PLAYERS:
                action(char)
            else:
                action()

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')
        self.map_folder = path.join(game_folder, 'maps')
        self.title_font = path.join(img_folder, 'ZOMBIE.TTF')
        self.hud_font = path.join(img_folder, '04B_30__.TTF')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))
        self.player_img = {}
        for player in PLAYERS:
            self.player_img[player] = {}
            for dir in PLAYERS[player]['images']:
                self.player_img[player][dir] = []
                for img in PLAYERS[player]['images'][dir]:
                    #pass
                    i = pg.image.load(path.join(img_folder, img)).convert_alpha()
                    self.player_img[player][dir].append(i)
        self.bullet_images = {}
        self.bullet_images['lg'] = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.bullet_images['lg'] = pg.transform.scale(self.bullet_images['lg'], (30, 30))
        self.bullet_images['sm'] = pg.transform.scale(self.bullet_images['lg'], (10, 10))
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.splat = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))
        self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(path.join(img_folder, img)).convert_alpha())
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()
        self.buttons = {}
        for button in BUTTON_IMAGES:
            self.buttons[button] = pg.image.load(path.join(img_folder, BUTTON_IMAGES[button])).convert_alpha()
            if button != 9:
                self.buttons[button] = pg.transform.scale(self.buttons[button], (50, 50))

        # lighting effect
        self.fog = pg.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(path.join(img_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()
        # Sound loading
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
        self.effects_sounds = {}
        for type in EFFECTS_SOUNDS:
            self.effects_sounds[type] = pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[type]))
        self.weapon_sounds = {}
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for snd in WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(snd_folder, snd))
                s.set_volume(0.3)
                self.weapon_sounds[weapon].append(s)
        self.zombie_moan_sounds = []
        for snd in ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.1) # reduce volume
            self.zombie_moan_sounds.append(s)
        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))
        self.zombie_hit_sounds = []
        for snd in ZOMBIE_HIT_SOUNDS:
            self.zombie_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))

    def new(self, char):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates() # drawing in layer orders
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.map = TiledMap(path.join(self.map_folder, 'dungeon.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.player_char = char
        itemimages = []
        for item in ITEM_IMAGES:
            itemimages.append(item)
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2, 
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y, self.player_char)
            if tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, 
                         tile_object.width, tile_object.height)
            if tile_object.name in itemimages:
                Item(self, obj_center, tile_object.name)
        self.camera = Camera(self.map.width, self.map.height) #480 x 480 16bit
        self.draw_debug = False
        self.paused = False # value for whether paused or not
        self.night = False
        self.effects_sounds['level_start'].set_volume(0.5)
        self.effects_sounds['level_start'].play()

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0  # fix for Python 2.x
            self.events()
            if not self.paused: # Only if paused is false will we update
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)
        # game over?
        if len(self.mobs) == 0:
            self.playing = False
        # player hits items    
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYERS[self.player.char]['health']:
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.powerup(hit.type)
            if hit.type == 'shotgun':
                hit.kill()
                self.effects_sounds['gun_pickup'].play()
                self.player.lvlup = True
                self.player.powerup(hit.type)
            if hit.type == 'jump':
                hit.kill()
                self.player.lvlup = True
                self.player.powerup(hit.type)
        # mobs hit player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            if random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
        if hits:
            self.player.hit()
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
        # bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            #hit.health -= WEAPONS[self.player.weapon]['damage'] * len(hits[hit])
            for bullet in hits[mob]:
                mob.health -= bullet.damage
            mob.vel = vec(0, 0)

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def render_fog(self):
        # draw the light mask (gradient) onto fog image
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        #self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        # self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(wall.rect), 1)
        # pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)
        if self.night:
            self.render_fog()
        # HUD functions
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYERS[self.player.char]['health'], self.player)
        self.draw_text('Zombies: {}'.format(len(self.mobs)), self.hud_font, 30, WHITE, 
                        WIDTH - 135, 20)
        #self.draw_text("{:.2f}".format(self.clock.get_fps()), self.hud_font, 30, WHITE, 
                        #WIDTH - 135, 20)
        if self.player.reloading == True:
            self.draw_text("Reloading", self.hud_font, 20, WHITE,
                            WIDTH / 2, HEIGHT / 2 + 50)
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.title_font, 105, RED, 
                            WIDTH / 2, HEIGHT / 2)
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused # toggle between true and false
                if event.key == pg.K_n:
                    self.night = not self.night

    def show_start_screen(self):
        self.screen.fill(BLACK)
        waiting = True
        self.time_now = pg.time.get_ticks()
        self.draw_text("CASTLE RAIDERS", self.hud_font, 75, YELLOW,
                        WIDTH / 2, HEIGHT / 3)  
        while waiting:
            self.clock.tick(FPS)        
            self.draw_text("START", self.hud_font, 40, GREEN,
                            WIDTH / 2, (HEIGHT / 2) + 20, self.char_select)
            self.draw_text("HOW TO PLAY", self.hud_font, 40, BLUE,
                            WIDTH / 2, (HEIGHT / 2) + 120, self.show_htp)
            self.draw_text("EXIT", self.hud_font, 40, RED,
                            WIDTH / 2, (HEIGHT / 2) + 220, self.quit)
            pg.display.flip()
            self.wait_for_key()

    def wait_for_key(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
                self.quit()
            if event.type == pg.MOUSEBUTTONDOWN:
                return True

    def show_go_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font, 100, RED,
                        WIDTH / 2, HEIGHT / 3)
        waiting = True
        self.time_now = pg.time.get_ticks()
        while waiting:
            self.clock.tick(FPS)
            self.draw_text("Start Screen", self.title_font, 75, WHITE, 
                            WIDTH / 2, HEIGHT * 3 / 5, self.show_start_screen)
            pg.display.flip()
            self.wait_for_key()

    def show_htp(self):
        arrow_x = 140
        arrow_y = 220
        wasd_x = 500
        wasd_y = 220
        dir_list = {1:'up', 2:'down', 3:'left', 4:'right'}
        self.screen.fill(BLACK)
        self.draw_text("HOW TO PLAY", self.hud_font, 60, WHITE, WIDTH / 2, HEIGHT / 7)

        for i in self.buttons:
            if i <= 4:
                self.screen.blit(self.buttons[i], (arrow_x, arrow_y))
                self.draw_text("Move player %s" % (dir_list[i]), self.hud_font, 15, WHITE, arrow_x + 165, arrow_y + 20)
                arrow_y += 100
            elif i <= 8:
                self.screen.blit(self.buttons[i], (wasd_x, wasd_y))
                self.draw_text("Shoot %s" % (dir_list[i-4]), self.hud_font, 15, WHITE, wasd_x + 150, wasd_y + 20)
                wasd_y += 100
            elif i == 9:
                self.screen.blit(self.buttons[i], (600, 600))

        waiting = True
        self.time_now = pg.time.get_ticks()
        while waiting:
            self.clock.tick(FPS)
            self.draw_text("<-", self.hud_font, 40, RED, 40, 40, self.show_start_screen)
            pg.display.flip()
            self.wait_for_key()

    def char_select(self): # Show information when clicked/hovering
        self.screen.fill(BLACK)
        waiting = True
        self.time_now = pg.time.get_ticks()
        self.draw_text("SELECT YOUR CHARACTER", self.hud_font, 45, GREEN, WIDTH / 2, HEIGHT / 8)
        while waiting:
            mouse_pos = pg.mouse.get_pos()
            self.draw_text("MAGE", self.hud_font, 40, BLUE, WIDTH / 2, HEIGHT / 2 - 150, game_loop, 'mage')
            self.draw_text("KNIGHT", self.hud_font, 40, BLUE, WIDTH / 2, HEIGHT / 2, game_loop, 'knight')
            self.draw_text("ARCHER", self.hud_font, 40, BLUE, WIDTH / 2, HEIGHT / 2 + 150)
            pg.display.flip()
            self.wait_for_key()

# create the game object
def game_loop(char):
    g = Game()
    while True:
        g.new(char)
        g.run()
        g.show_go_screen()

g = Game()
g.show_start_screen()
#g.show_go_screen()
#g.show_htp()
#g.char_select()
