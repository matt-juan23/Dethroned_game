''' Requirements
1. Effective GUI. Good design and ergonomic features
4. At least 1 array of records or multi-dimensional array
6. Modularised into sub-programs
'''

# Python 2.7
import sys
import pygame as pg
from os import path
from appJar import gui
from pygame.locals import *
from settings import *
from sprites2 import *
from tilemap import *
from random import random, choice

class Game:
    # Game class that holds all subprograms relating to the game and its functionality
    # All subprograms have a parameter of self which passes the game class as a parameter
    def __init__(self): 
        # Initialises music and screen settings
        pg.mixer.pre_init(44100, -16, 1, 2048) # less lag between shot audio
        pg.init()
        # Enable this for 60 fps but in full screen
        #`flags = FULLSCREEN #| DOUBLEBUF
        #self.screen = pg.display.set_mode((WIDTH, HEIGHT), flags)
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.level = 1
        self.load_data()

    def draw_button(self, text, font_name, size, color, x, y, time, action, char=None):
        # Draws text as a button to the screen
        ''' Inputs: text to be drawn onto screen, font, size of text, colour of text, x and y position
        current time, function name (action) or character string (char)'''
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()
        font = pg.font.Font(font_name, size)
        mod_font = pg.font.Font(font_name, size)
        mod_font.set_underline(1) # set underline to true

        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)

        draw_ticks = pg.time.get_ticks()
        if text_rect.collidepoint(mouse):
            text_surface = mod_font.render(text, True, color)
            if click[0] == 1 and draw_ticks - time > 300:
                if char in PLAYERS: # Only used in the picking character screen
                    action(char, self.level)
                else:
                    action()

        self.screen.blit(text_surface, text_rect)

    def draw_text(self, text, font_name, size, color, x, y):
        # Draws text to screen
        #Inputs: text to be drawn onto screen, font, size of text, colour of text, x and y position
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()
        font = pg.font.Font(font_name, size)
        mod_font = pg.font.Font(font_name, size)
        mod_font.set_underline(1) # set underline to true

        if text == 'DETHRONE':
            font = mod_font

        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)

        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        # Loads all image and sound data into appropriate data structures
        # Folder names
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')
        self.map_folder = path.join(game_folder, 'maps')

        # Title fonts
        #self.title_font = path.join(img_folder, 'joystix monospace.ttf')
        self.hud_font = path.join(img_folder, '04B_30__.TTF')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))

        # Load player images
        self.player_img = {}
        for player in PLAYERS:
            self.player_img[player] = {}
            for dir in PLAYERS[player]['images']:
                self.player_img[player][dir] = []
                for img in PLAYERS[player]['images'][dir]:
                    # 32 x 32
                    i = pg.image.load(path.join(img_folder, img)).convert_alpha()
                    self.player_img[player][dir].append(i)

        # Load bullet images
        self.bullet_images = {}
        for weapon in WEAPONS:
            i = pg.image.load(path.join(img_folder, WEAPONS[weapon]['image'])).convert_alpha()
            i = pg.transform.scale(i, WEAPONS[weapon]['scale'])
            self.bullet_images[weapon] = i

        #Mob loading
        self.mob_img = {}
        for mob in MOBS:
            self.mob_img[mob] = {}
            for dir in MOBS[mob]['images']:
                self.mob_img[mob][dir] = []
                for img in MOBS[mob]['images'][dir]:
                    i = pg.image.load(path.join(img_folder, img)).convert_alpha()
                    self.mob_img[mob][dir].append(i)

        # Boss loading
        self.boss_img = []
        for boss in BOSS:
            i = pg.image.load(path.join(img_folder, BOSS[boss]['image'])).convert_alpha()
            self.boss_img.append(i)

        #self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        #self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.splat = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))

        self.star_img = pg.image.load(path.join(img_folder, STAR)).convert_alpha()
        self.ability_img = pg.image.load(path.join(img_folder, ABILITY)).convert_alpha()
        '''self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(path.join(img_folder, img)).convert_alpha())'''

        # Load item images
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()
        self.buttons = {}
        for button in BUTTON_IMAGES:
            self.buttons[button] = pg.image.load(path.join(img_folder, BUTTON_IMAGES[button])).convert_alpha()
            if button != 10:
                self.buttons[button] = pg.transform.scale(self.buttons[button], (50, 50))

        # Load ability images
        self.ability_images = {}
        for player in PLAYERS:
            self.ability_images[player] = pg.image.load(path.join(img_folder, PLAYERS[player]['ability'])).convert_alpha()

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

    def new(self, char, level):
        # initialize all variables and do all the setup for a new game
        # char is character user selected from char_select method
        self.all_sprites = pg.sprite.LayeredUpdates() # drawing in layer orders
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.mob_bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.exit = pg.sprite.GroupSingle()
        self.level = level
        self.player_char = char
        #self.map = TiledMap(path.join(self.map_folder, 'town.tmx'))  
        self.map = TiledMap(path.join(self.map_folder, LEVELS[self.level])) # load the correct level 
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        itemimages = []
        for item in ITEM_IMAGES:
            itemimages.append(item)

        # Load object based on name from Tiled file
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2, 
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y, self.player_char)
                #self.player = Mage(self, obj_center.x, obj_center.y, self.player_char)
            if tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y, tile_object.name)
            if tile_object.name == 'level1':
                #Boss(self, obj_center.x, obj_center.y, tile_object.name)
                Level1(self, obj_center.x, obj_center.y)
            if tile_object.name == 'trooper':
                Trooper(self, obj_center.x, obj_center.y, tile_object.name)
            if tile_object.name == 'demon':
                Demon(self, obj_center.x, obj_center.y, tile_object.name)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, 
                         tile_object.width, tile_object.height)
            if tile_object.name in itemimages:
                Item(self, obj_center, tile_object.name)
            if tile_object.name == 'exit':
                Exit(self, tile_object.x, tile_object.y, 
                         tile_object.width, tile_object.height)

        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.paused = False
        self.score = 0
        self.effects_sounds['level_start'].set_volume(0.5)
        self.effects_sounds['level_start'].play()

    def run(self):
        # Main loop of game
        # set self.playing = False to end the game
        self.playing = True
        pg.mixer.music.play(loops=-1) # repeat music
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0 
            self.events()
            if not self.paused: # Only if paused is false will we update
                self.update()
            self.draw()

        if self.win == True:
            self.show_win_screen() # show if win
        else:
            self.show_go_screen() # show if lose

    def quit(self):
        # Quit application upon being called
        pg.quit()
        sys.exit()

    # Hit detection
    def update(self):
        # update sprites + hit detection
        # update all sprites and player
        self.screen.fill(BLACK)
        self.all_sprites.update()
        self.camera.update(self.player)

        # game over?
        if len(self.mobs) == 0:
            self.playing = False
            self.win = True

        hits = pg.sprite.spritecollide(self.player, self.exit, False)
        '''
        TODO
        2D array for the levels of the game
        Change the exit singlegroup in def new() to a sprite group for the directions
        '''
        if hits:
            self.level += 1 # increment the level counter
            game_loop(self.player_char, self.level) # call the game loop with the new level

        # player hits items    
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYERS[self.player.char]['health']:
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.health += 30
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
            self.player.health -= MOBS['zombie']['con_damage']
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
                self.win = False
        if hits:
            self.player.hit()
            self.player.pos += vec(MOBS['zombie']['knockback'], 0).rotate(-hits[0].rot)

        # bullets hit mobs
        self.mob_hit = False
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            for bullet in hits[mob]:
                self.mob_hit = True
                mob.health -= bullet.damage
            mob.vel = vec(0, 0)
            mob.hit()

        # bullet hits player
        hits = pg.sprite.spritecollide(self.player, self.mob_bullets, True, collide_hit_rect)
        for hit in hits:
            self.player.health -= hit.damage 
            self.player.hit()
            if self.player.health <= 0:
                self.playing = False
                self.win = False 

    def draw(self):
        # draws hud elements + sprites onto screen
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            if isinstance(sprite, Player):
                sprite.draw_ability()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(wall.rect), 1)

        # HUD functions
        self.player.draw_player_health(self.screen, 10, 10, self.player.health / PLAYERS[self.player.char]['health'])

        if self.player.seconds_string > 0 and self.player.ability_uses > 0:
            self.draw_text(str(self.player.seconds_string), self.hud_font, 20, YELLOW, WIDTH - 50, HEIGHT - 120)
        elif self.player.seconds_string == 0 and self.player.ability_active == False and self.player.ability_uses > 0:
            self.draw_text("READY", self.hud_font, 20, GREEN, WIDTH - 50, HEIGHT - 120)

        self.draw_text("Ability uses: " + str(self.player.ability_uses), self.hud_font, 20, GREEN, WIDTH - 153, HEIGHT - 80) # ability uses
        self.draw_text(str(self.player.ammo_count), self.hud_font, 20, RED, WIDTH - 50, HEIGHT - 40) # ammo
        #self.draw_text('Zombies: {}'.format(len(self.mobs)), self.hud_font, 30, WHITE, WIDTH - 135, 20) # zombies left
        self.draw_text('Score: {}'.format(self.score), self.hud_font, 30, WHITE, WIDTH - 135, 20)
        #self.draw_text("{:.2f}".format(self.clock.get_fps()), self.hud_font, 30, WHITE, 
                        #WIDTH - 135, 20)
        if self.player.reloading == True:
            self.draw_text("Reloading", self.hud_font, 20, WHITE, WIDTH / 2, HEIGHT / 2 + 50) # reloading
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.hud_font, 105, RED, WIDTH / 2, HEIGHT / 2) # pause
        # flip everything to be visible on screen
        pg.display.flip()

    def events(self):
        # catch all single press events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_e:
                    self.player.e_ability()
                if event.key == pg.K_SPACE and self.player.moving:
                    self.player.dodge()
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused # toggle between true and false

    # http://programarcadegames.com/python_examples/show_file.php?file=high_score.py
    # 13 may 18
    def get_high_score(self):
        # Default high score
        high_score = 0
     
        # Try to read the high score from a file
        try:
            high_score_file = open("high_score.txt", "r")
            high_score = int(high_score_file.read())
            high_score_file.close()
        except IOError:
            # Error reading file, no high score
            print "There is no high score yet." 
        except ValueError:
            # There's a file there, but we don't understand the number.
            print "I'm confused. Starting with no high score."
     
        return high_score

    def save_high_score(self, new_high_score):
        try:
            # Write the file to disk
            high_score_file = open("high_score.txt", "w")
            high_score_file.write(str(new_high_score))
            high_score_file.close()
        except IOError:
            # Hm, can't write it.
            print "Unable to save the high score."

    def wait_for_key(self):
        # function that waits for a quit key to be pressed
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
                self.quit()

    def show_start_screen(self):
        # displays start screen
        waiting = True
        time_now = pg.time.get_ticks()    

        while waiting:
            self.screen.fill(BLACK)
            self.clock.tick(FPS)    
            self.draw_text('DETHRONE', self.hud_font, 55, YELLOW,
                            WIDTH / 2, HEIGHT / 5) 
            self.draw_button("START", self.hud_font, 40, GREEN,
                            WIDTH / 2, (HEIGHT / 5) + 120, time_now, self.char_select)
            self.draw_button("CHARACTER STATS", self.hud_font, 40, WHITE,
                            WIDTH / 2, (HEIGHT / 5) + 240, time_now, self.char_stats)
            self.draw_button("CONTROLS", self.hud_font, 40, BLUE,
                            WIDTH / 2, (HEIGHT / 5) + 360, time_now, self.show_controls)
            self.draw_button("EXIT GAME", self.hud_font, 40, RED,
                            WIDTH / 2, (HEIGHT / 5) + 480, time_now, self.quit)
            pg.display.flip()
            self.wait_for_key() 

    def char_stats(self):
        # displays character stats
        time_now = pg.time.get_ticks()
        waiting = True

        while waiting:
            self.screen.fill(BLACK)
            self.clock.tick(FPS)
            # Stars
            self.screen.blit(self.star_img, (0, 0))
            self.draw_button("<-", self.hud_font, 40, RED, 40, 40, time_now, self.show_start_screen)
            self.draw_button("ABILITIES", self.hud_font, 40, GREEN, 830, 75, time_now, self.show_abilities)
            pg.display.flip()
            self.wait_for_key() 

    def show_abilities(self):
        # display each characters abilities
        waiting = True
        time_now = pg.time.get_ticks()
        # Char text

        while waiting:
            self.screen.fill(BLACK)
            self.screen.blit(self.ability_img, (0, 0))
            self.draw_button("<-", self.hud_font, 40, RED, 40, 40, time_now, self.char_stats)
            '''self.draw_text("ABILITIES", self.hud_font, 55, WHITE,
                            WIDTH / 2, HEIGHT / 10)
            self.draw_text("MAGE", self.hud_font, 35, BLUE,
                            WIDTH / 6, HEIGHT / 3)
            self.draw_text("Throws a healing potion on the ground",
                            self.hud_font, 20, YELLOW, (WIDTH / 2) + 80, (HEIGHT / 3) - 15)
            self.draw_text("Stay within its radius to slowly recover health",
                            self.hud_font, 20, YELLOW, (WIDTH / 2) + 110, (HEIGHT / 3) + 15)
            self.draw_text("KNIGHT", self.hud_font, 35, BLUE,
                            WIDTH / 6, (HEIGHT / 3) + 170)
            self.draw_text("Hold up your shield to absorb", self.hud_font, 20, YELLOW,
                            (WIDTH / 2) + 80, (HEIGHT / 3) + 155)
            self.draw_text("damage and gain health", self.hud_font, 20, YELLOW,
                            (WIDTH / 2) + 80, (HEIGHT / 3) + 185)
            self.draw_text("NINJA", self.hud_font, 35, BLUE,
                            WIDTH / 6, (HEIGHT / 3) + 340)
            self.draw_text("Hit mobs to steal their health", self.hud_font, 20, YELLOW,
                            WIDTH / 2 + 80, (HEIGHT / 3) + 340)'''
            self.clock.tick(FPS)
            pg.display.flip()
            self.wait_for_key() #do with image

    def show_controls(self):
        # show controls screen
        arrow_x = 140
        arrow_y = 180
        wasd_x = 500
        wasd_y = 180
        space_x = 130
        space_y = 580
        dir_list = {1:'up', 2:'down', 3:'left', 4:'right'}
        time_now = pg.time.get_ticks()
        self.screen.fill(BLACK)
        self.draw_text("CONTROLS", self.hud_font, 60, WHITE, WIDTH / 2, HEIGHT / 7)

        # For loop for evenly spacing
        # use image
        for i in self.buttons:
            if i <= 4: # arrow keys
                self.screen.blit(self.buttons[i], (arrow_x, arrow_y))
                self.draw_text("Move player %s" % (dir_list[i]), self.hud_font, 15, WHITE, arrow_x + 165, arrow_y + 20)
                arrow_y += 100
            elif i <= 8: # wasd keys
                self.screen.blit(self.buttons[i], (wasd_x, wasd_y))
                self.draw_text("Shoot %s" % (dir_list[i-4]), self.hud_font, 15, WHITE, wasd_x + 150, wasd_y + 20)
                wasd_y += 100
            elif i == 9: # e key
                self.screen.blit(self.buttons[i], (500, 580))
                self.draw_text("Ability", self.hud_font, 15, WHITE, 640, 605)
            elif i == 10: # space bar
                self.screen.blit(self.buttons[i], (space_x, space_y))
                self.draw_text("Dodge", self.hud_font, 15, WHITE, space_x + 220, space_y + 15)

        waiting = True
        while waiting:
            self.clock.tick(FPS)
            self.draw_button("<-", self.hud_font, 40, RED, 40, 40, time_now, self.show_start_screen)
            pg.display.flip()
            self.wait_for_key() #do with image

    def char_select(self):
        # show charcter select screen
        waiting = True
        time_now = pg.time.get_ticks()

        while waiting:
            self.screen.fill(BLACK)
            self.draw_text("SELECT YOUR CHARACTER", self.hud_font, 45, GREEN, WIDTH / 2, HEIGHT / 8)
            self.draw_button("<-", self.hud_font, 40, RED, 40, 40, time_now, self.show_start_screen)
            self.draw_button("MAGE", self.hud_font, 40, BLUE, WIDTH / 2, HEIGHT / 2 - 150, time_now, game_loop, 'mage')
            self.draw_button("KNIGHT", self.hud_font, 40, BLUE, WIDTH / 2, HEIGHT / 2, time_now, game_loop, 'knight')
            self.draw_button("NINJA", self.hud_font, 40, BLUE, WIDTH / 2, HEIGHT / 2 + 150, time_now, game_loop, 'ninja')
            pg.display.flip()
            self.wait_for_key()

    def show_win_screen(self):
        # show win screen
        pg.mixer.music.stop()
        waiting = True
        time_now = pg.time.get_ticks()

        # high score stuff
        high_score = self.get_high_score()

        current_score = self.score

        if current_score > high_score:
            self.save_high_score(current_score)
            high_score = current_score

        while waiting:
            self.screen.fill(BLACK)
            self.clock.tick(FPS)
            self.draw_text("YOU WON", self.hud_font, 80, GREEN, WIDTH / 2, HEIGHT / 4 + 30)
            self.draw_text("High Score: " + str(high_score), self.hud_font, 50, BLUE, WIDTH / 2, HEIGHT / 4 + 130)
            self.draw_text("Your Score: " + str(current_score), self.hud_font, 50, BLUE, WIDTH / 2, HEIGHT / 4 + 230)
            self.draw_button("Start Screen", self.hud_font, 45, WHITE, 
                            WIDTH / 2, HEIGHT / 4 + 330, time_now, self.show_start_screen)
            pg.display.flip()
            self.wait_for_key()

    def show_go_screen(self):
        # show game over screen
        pg.mixer.music.stop()
        waiting = True
        time_now = pg.time.get_ticks()

        # high score stuff
        high_score = self.get_high_score()

        current_score = self.score

        if current_score > high_score:
            self.save_high_score(current_score)
            high_score = current_score

        while waiting:
            self.clock.tick(FPS)
            self.screen.fill(BLACK)
            self.draw_text("GAME OVER", self.hud_font, 80, RED, WIDTH / 2 , HEIGHT / 4 + 30)
            self.draw_text("High Score: " + str(high_score), self.hud_font, 50, BLUE, WIDTH / 2, HEIGHT / 4 + 130)
            self.draw_text("Your Score: " + str(current_score), self.hud_font, 50, BLUE, WIDTH / 2, HEIGHT / 4 + 230)
            self.draw_button("Start Screen", self.hud_font, 45, WHITE, 
                            WIDTH / 2, HEIGHT / 4 + 330, time_now, self.show_start_screen)
            pg.display.flip()
            self.wait_for_key()

class MyApplication():

    # Build the GUI
    def Prepare(self, app):
        # Form GUI
        app.setTitle("Login Form")
        app.setFont(16)
        app.setStopFunction(self.BeforeExit)

        # Add labels & entries
        # in the correct row & column
        app.addLabel("userLab", "Username:", 0, 0)
        app.addEntry("username", 0, 1)
        app.addLabel("passLab", "Password:", 1, 0)
        app.addSecretEntry("password", 1, 1)
        app.addButtons( ["Submit", "Cancel"], self.Submit, colspan=2)

        return app
        
    # Build and Start your application
    def Start(self):
        # Creates a UI
        app = gui()

        app.showSplash("Something", fill='red', stripe='black', fg='white', font=44)

        # Run the prebuild method that adds items to the UI
        app = self.Prepare(app)

        # Make the app class-accesible
        self.app = app

        # Start appJar
        app.go()

    # Callback execute before quitting your app
    def BeforeExit(self):
        return self.app.yesNoBox("Confirm Exit", "Are you sure you want to exit the application?")
    
    # Define method that is executed when the user clicks on the submit buttons
    # of the form
    def Submit(self, btnName):
        if btnName == "Submit":
            username = self.app.getEntry("username")
            password = self.app.getEntry("password")

            # Very stupid login system (both strings equal to ourcodeworld)
            if username and password == "o":
                self.app.stop()
            else:
                self.app.errorBox("Error", "Your credentials are invalid !")

# create the game object
def game_loop(char, level):
    # function that creates a game object and runs the game in a while loop
    # passes char parameter which is string to pass into new method in Game class
    #g = Game()
    while True:
        g.new(char, level)
        g.run()

'''App = MyApplication()

App.Start()'''

g = Game()

g.show_start_screen()
#g.char_stats()
#g.show_abilities()
#g.show_go_screen()
#g.show_win_screen()
#g.show_controls()
#g.char_select()
