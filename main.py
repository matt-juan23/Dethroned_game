''' 
Acknowledgements:
1. Background Music - Darren Curtis
2. Level Sprites - DawnHack
3. Boss Sprites - Kenney
4. Player and Mob Sprites - Philipp Lenssen. Website: outer-court.com
5. Tutorial and Project Framework - KidsCanCode
6. Inspiration - Vladimir Tosic
7. High Score functions -  http://programarcadegames.com/python_examples/show_file.php?file=high_score.py
8. Button function - Sentdex
'''

# Python 2.7 64 bit
# Import external modules
import sys
import pygame as pg
from os import path
from pygame.locals import *
from settings import *
from sprites2 import *
from tilemap import *
from random import random, choice

# Game class
# Stores all the functions that run the game and the screens
class Game:
    # All subprograms have a parameter of self which allows attributes to be accessed throughout the whole class

    # Initialises Pygame, music and screen settings
    # Author: KidsCanCode
    def __init__(self): 
        pg.mixer.pre_init(44100, -16, 1, 2048) # less lag between shot audio
        pg.init()
        # Enable this for 60 fps but in full screen
        flags = FULLSCREEN | DOUBLEBUF
        #self.screen = pg.display.set_mode((WIDTH, HEIGHT), flags)
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.level = 0
        self.load_data()

    # Draws text as a button to the screen
    # Inputs: text to be drawn onto screen, font, size of text, colour of text, x and y position,
    # current time, function name (action) and possible character string (char)
    # Author: Sentdex
    def draw_button(self, text, font_name, size, color, x, y, time_now, action, char=None):
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
            text_surface = mod_font.render(text, True, color) # underline text
            if click[0] == 1 and draw_ticks - time_now > 200:
                if char in PLAYERS: # only used in the picking character screen
                    action(char, self.level, 0, PLAYERS[char]['health'])
                else: # otherwise run the function
                    action()

        self.screen.blit(text_surface, text_rect)

    # Draws text to screen
    # Inputs: text to be drawn onto screen, font, size of text, colour of text, x and y position
    # Author: KidsCanCode
    def draw_text(self, text, font_name, size, color, x, y):
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()
        font = pg.font.Font(font_name, size)
        mod_font = pg.font.Font(font_name, size)

        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)

        self.screen.blit(text_surface, text_rect)

    # Loads all image and sound data into appropriate data structures
    # Author: KidsCanCode, me
    def load_data(self):
        # Folder names
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')
        self.map_folder = path.join(game_folder, 'maps')

        # Title fonts
        self.hud_font = path.join(img_folder, '04B_30__.TTF')

        # Load player images
        self.player_img = {}
        for player in PLAYERS:
            self.player_img[player] = {}
            for dir in PLAYERS[player]['images']:
                self.player_img[player][dir] = []
                for img in PLAYERS[player]['images'][dir]:
                    i = pg.image.load(path.join(img_folder, img)).convert_alpha()
                    self.player_img[player][dir].append(i)

        # Image for crosshair
        self.crosshair_img = pg.image.load(path.join(img_folder, CROSSHAIR)).convert_alpha()
        self.crosshair_img = pg.transform.scale(self.crosshair_img, (16, 16))

        # Load bullet images
        self.bullet_images = {}
        for weapon in WEAPONS:
            i = pg.image.load(path.join(img_folder, WEAPONS[weapon]['image'])).convert_alpha()
            i = pg.transform.scale(i, WEAPONS[weapon]['scale'])
            self.bullet_images[weapon] = i

        # Mob loading
        self.mob_img = {}
        for mob in MOBS:
            self.mob_img[mob] = {}
            for dir in MOBS[mob]['images']:
                self.mob_img[mob][dir] = []
                for img in MOBS[mob]['images'][dir]:
                    i = pg.image.load(path.join(img_folder, img)).convert_alpha()
                    self.mob_img[mob][dir].append(i)

        # Boss loading
        self.boss_images = {}
        for boss in BOSS:
            self.boss_images[boss] = pg.image.load(path.join(img_folder, BOSS[boss]['image'])).convert_alpha()

        # Load other images
        self.background_img = pg.image.load(path.join(img_folder, BACKGROUND)).convert_alpha()
        self.star_img = pg.image.load(path.join(img_folder, STAR)).convert_alpha()
        self.ability_img = pg.image.load(path.join(img_folder, ABILITY)).convert_alpha()
        self.controls_img = pg.image.load(path.join(img_folder, CONTROLS)).convert_alpha()
        self.how_to_play_img = pg.image.load(path.join(img_folder, HOW_TO_PLAY)).convert_alpha()

        # Load ability images
        self.ability_images = {}
        for player in PLAYERS:
            self.ability_images[player] = pg.image.load(path.join(img_folder, PLAYERS[player]['ability'])).convert_alpha()

        # Sound loading
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC)) # background music
        self.level_start_sound = pg.mixer.Sound(path.join(snd_folder, LEVEL_START_SOUND))

        self.weapon_sounds = [[], [], []] # Process information into a 2D array
        for i in range(len(WEAPON_SOUNDS)):
            for j in range(len(WEAPON_SOUNDS[i])):
                s = pg.mixer.Sound(path.join(snd_folder, WEAPON_SOUNDS[i][j]))
                s.set_volume(0.3)
                self.weapon_sounds[i].append(s)

        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))

        self.death_sound = pg.mixer.Sound(path.join(snd_folder, DEATH_SOUND))

    # initialize all variables and do all the setup for a new game
    # Inputs: character selected, level, score and health values
    # Author: KidsCanCode, me
    def new(self, char, level, score, health):
        # initialises groups
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.mob_bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.exit = pg.sprite.GroupSingle()

        self.level = level
        self.player_char = char
        self.win = False

        if self.level > 2: # check for last level
            self.show_win_screen()
        else:
            self.map = TiledMap(path.join(self.map_folder, LEVELS[self.level])) # load the correct level 
            self.map_img = self.map.make_map()
            self.map_rect = self.map_img.get_rect()

        # Load objects based on name from Tiled file
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2, 
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y, self.player_char)
            if tile_object.name == 'brawler':
                Brawler(self, obj_center.x, obj_center.y, tile_object.name)
            if tile_object.name == 'level1':
                Level1(self, obj_center.x, obj_center.y)
            if tile_object.name == 'level2':
                Level2(self, obj_center.x, obj_center.y)
            if tile_object.name == 'trooper':
                Trooper(self, obj_center.x, obj_center.y, tile_object.name)
            if tile_object.name == 'demon':
                Demon(self, obj_center.x, obj_center.y, tile_object.name)
            if tile_object.name == 'wall':
                Wall(self, tile_object.x, tile_object.y, 
                         tile_object.width, tile_object.height)
            if tile_object.name == 'exit':
                Exit(self, tile_object.x, tile_object.y, 
                         tile_object.width, tile_object.height)

        # get mouse values
        mouse_pos = pg.mouse.get_pos()
        self.mouse = Mouse(self, mouse_pos[0], mouse_pos[1])

        # initialise other variables
        self.camera = Camera(self.map.width, self.map.height)
        self.paused = False
        self.score = score
        self.player.health = health
        self.level_start_sound.set_volume(0.2)
        self.level_start_sound.play()

    # Main loop of game
    # Author: KidsCanCode, me
    def run(self):
        self.playing = True
        pg.mixer.music.set_volume(0.05)
        if pg.mixer.music.get_busy(): # check to see if the music is paused
            pg.mixer.music.unpause()
        else:
            pg.mixer.music.play(loops=-1) # repeat music

        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0 
            self.events()
            if not self.paused: # only if paused is false will we update
                self.update()
            self.draw()

        # check for win
        if self.win == False:
            self.show_lose_screen()
        else:
            self.show_win_screen()

    # Quit application upon being called
    # Author: KidsCanCode
    def quit(self):
        pg.quit()
        sys.exit()

    # update all sprites + hit detection
    # Author: KidsCanCode, me
    def update(self):
        # update screen
        self.screen.fill(BLACK)
        self.all_sprites.update()
        self.camera.update(self.player)

        # player hits exit
        hits = pg.sprite.spritecollide(self.player, self.exit, False)
        if hits:
            self.level += 1 # increment the level counter
            game_loop(self.player_char, self.level, self.score, self.player.health) # call the game loop with the new level

        # mobs hit player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            if random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= MOBS['brawler']['con_damage']
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
                self.win = False
        if hits:
            self.player.hit()
            self.player.pos += vec(MOBS['brawler']['knockback'], 0).rotate(-hits[0].rot)

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

    # draws hud elements + sprites onto screen
    # Author: KidsCanCode, me
    def draw(self):
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            if isinstance(sprite, Player):
                sprite.draw_ability_bar()
            if isinstance(sprite, Mouse):
                self.screen.blit(sprite.image, sprite.rect)
            else:
                self.screen.blit(sprite.image, self.camera.apply(sprite))

        # HUD functions
        self.player.draw_player_health(self.screen, 10, 10, self.player.health / PLAYERS[self.player.char]['health'])

        if self.player.seconds_string > 0 and self.player.ability_uses > 0:
            self.draw_text(str(self.player.seconds_string), self.hud_font, 20, YELLOW, WIDTH - 50, HEIGHT - 120)
        elif self.player.seconds_string == 0 and self.player.ability_active == False and self.player.ability_uses > 0:
            self.draw_text("ABILITY READY", self.hud_font, 20, GREEN, WIDTH - 150, HEIGHT - 120)

        self.draw_text("Ability uses: " + str(self.player.ability_uses), self.hud_font, 20, MINT, WIDTH - 153, HEIGHT - 80) # ability uses
        self.draw_text(str("Ammo: " + str(self.player.ammo_count)), self.hud_font, 20, WHITE, WIDTH - 100, HEIGHT - 40) # ammo
        self.draw_text('Score: {}'.format(self.score), self.hud_font, 30, WHITE, WIDTH - 135, 20)

        if self.player.reloading == True:
            self.draw_text("Reloading", self.hud_font, 20, WHITE, WIDTH / 2, HEIGHT / 2 + 50) # reloading
        if self.paused:
            self.pause_screen()

        # check for no mobs left in map
        if len(self.mobs) == 0: 
            self.draw_text("Great job! Reach the doors to move on", self.hud_font, 20, GREEN, WIDTH / 2, 50)

        pg.display.flip()

    # unpauses the game
    # Author: Sentdex
    def unpause(self):
        self.paused = False
        self.run()

    # catches all single press keypresses
    # Author: KidsCanCode
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE: # Remove later
                    self.quit()
                if event.key == pg.K_p:
                    self.paused = True

    # All high score functions are from http://programarcadegames.com/python_examples/show_file.php?file=high_score.py

    # retrives high score from file and returns it
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
            pass
        except ValueError:
            # There's a file there, but we don't understand the number.
            pass
     
        return high_score

    # check if there is a new high score
    # returns flag whether old high score was beaten or not
    def new_highscore_check(self, high_score):
        current_score = self.score
        beat_high_score = False

        if current_score > high_score:
            beat_high_score = True

        # return true or false to whether the current score is greater than highscore
        return beat_high_score

    # if the new score is a highscore, overwrite the old high score with the new one
    def save_high_score(self, new_high_score):
        try:
            # Write the file to text file
            high_score_file = open("high_score.txt", "w")
            high_score_file.write(str(new_high_score))
            high_score_file.close()
        except IOError:
            pass

    # function that waits for a quit key to be pressed
    # Author: KidsCanCode
    def wait_for_key(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

    # Author of all screens is me
    # All have a while loop that waits for user input such as user clicking button

    # pause screen
    def pause_screen(self):
        waiting = True
        time_now = pg.time.get_ticks()
        pg.mixer.music.pause() # pause music

        while waiting:
            self.screen.fill(BLACK)
            self.clock.tick(FPS)
            self.draw_text("Paused", self.hud_font, 90, WHITE, WIDTH / 2, HEIGHT / 3) # pause
            self.draw_button("Resume Game", self.hud_font, 40, GREEN, WIDTH / 2, HEIGHT / 2, time_now, self.unpause)
            self.draw_button("Quit to start screen", self.hud_font, 40, RED, WIDTH / 2, HEIGHT * 2 / 3, time_now, self.show_start_screen)
            pg.display.flip()
            self.wait_for_key()

    # start screen
    # first screen that shows upon launch
    def show_start_screen(self):
        # displays start screen
        waiting = True
        time_now = pg.time.get_ticks()    

        while waiting:
            self.clock.tick(FPS)    
            self.screen.blit(self.background_img, (0, 0))
            self.draw_text('DETHRONE', self.hud_font, 55, YELLOW,
                            WIDTH / 2, HEIGHT / 6) 
            self.draw_button("START", self.hud_font, 40, GREEN,
                            WIDTH / 2, (HEIGHT / 6) + 110, time_now, self.char_select)
            self.draw_button("CHARACTER STATS", self.hud_font, 40, MINT,
                            WIDTH / 2, (HEIGHT / 6) + 220, time_now, self.show_char_stats_screen)
            self.draw_button("HOW TO PLAY", self.hud_font, 40, WHITE,
                            WIDTH / 2, (HEIGHT / 6) + 330, time_now, self.show_how_to_play_screen)
            self.draw_button("CONTROLS", self.hud_font, 40, BLUE,
                            WIDTH / 2, (HEIGHT / 6) + 440, time_now, self.show_controls_screen)
            self.draw_button("EXIT GAME", self.hud_font, 40, RED,
                            WIDTH / 2, (HEIGHT / 6) + 550, time_now, self.confirm_quit)
            pg.display.flip()
            self.wait_for_key() 

    # displays character stats
    def show_char_stats_screen(self):
        time_now = pg.time.get_ticks()
        waiting = True

        while waiting:
            self.screen.fill(BLACK)
            self.clock.tick(FPS)
            self.screen.blit(self.star_img, (0, 0))
            self.draw_button("<-", self.hud_font, 40, RED, 40, 40, time_now, self.show_start_screen)
            self.draw_button("ABILITIES", self.hud_font, 40, MINT, WIDTH / 2, HEIGHT - 80, time_now, self.show_abilities_screen)
            pg.display.flip()
            self.wait_for_key() 

    # display each characters abilities
    def show_abilities_screen(self):
        waiting = True
        time_now = pg.time.get_ticks()

        # Char text
        while waiting:
            self.screen.fill(BLACK)
            self.clock.tick(FPS)
            self.screen.blit(self.ability_img, (0, 0))
            self.draw_button("<-", self.hud_font, 40, RED, 40, 40, time_now, self.show_char_stats_screen)
            pg.display.flip()
            self.wait_for_key() 

    # show controls screen
    def show_controls_screen(self):
        # Show controls screen
        waiting = True
        time_now = pg.time.get_ticks()

        while waiting:
            self.screen.fill(BLACK)
            self.clock.tick(FPS)
            self.screen.blit(self.controls_img, (0, 0))
            self.draw_button("<-", self.hud_font, 40, RED, 40, 40, time_now, self.show_start_screen)
            pg.display.flip()
            self.wait_for_key()

    # show charcter select screen
    def char_select(self):
        waiting = True
        time_now = pg.time.get_ticks()
        self.level = 0

        while waiting:
            self.screen.fill(BLACK)
            self.clock.tick(FPS)
            self.draw_text("SELECT YOUR CHARACTER", self.hud_font, 45, WHITE, WIDTH / 2, HEIGHT / 8)
            self.draw_button("<-", self.hud_font, 40, RED, 40, 40, time_now, self.show_start_screen)
            self.draw_button("MAGE", self.hud_font, 40, BLUE, WIDTH / 2, HEIGHT / 2 - 150, time_now, game_loop, 'mage')
            self.draw_button("KNIGHT", self.hud_font, 40, BLUE, WIDTH / 2, HEIGHT / 2, time_now, game_loop, 'knight')
            self.draw_button("NINJA", self.hud_font, 40, BLUE, WIDTH / 2, HEIGHT / 2 + 150, time_now, game_loop, 'ninja')
            pg.display.flip()
            self.wait_for_key()

    # show how to play screen
    def show_how_to_play_screen(self):
        waiting = True
        time_now = pg.time.get_ticks()

        while waiting:
            self.screen.fill(BLACK)
            self.screen.blit(self.how_to_play_img, (0, 0))
            self.draw_button("<-", self.hud_font, 40, RED, 40, 40, time_now, self.show_start_screen)
            pg.display.flip()
            self.wait_for_key()

    # show win screen
    def show_win_screen(self):
        pg.mixer.music.stop()
        waiting = True
        time_now = pg.time.get_ticks()

        # high score stuff
        high_score = self.get_high_score()
        beat_high_score = self.new_highscore_check(high_score)
        if beat_high_score:
            self.save_high_score(self.score)
            high_score = self.score

        while waiting:
            self.screen.fill(BLACK)
            self.clock.tick(FPS)
            self.draw_text("YOU WON", self.hud_font, 80, GREEN, WIDTH / 2, HEIGHT / 4 + 30)
            self.draw_text("High Score: " + str(high_score), self.hud_font, 50, BLUE, WIDTH / 2, HEIGHT / 4 + 130)
            if beat_high_score:
                self.draw_text("NEW", self.hud_font, 45, GREEN, WIDTH / 2 + 400, HEIGHT / 4 + 130)
            self.draw_text("Your Score: " + str(self.score), self.hud_font, 50, BLUE, WIDTH / 2, HEIGHT / 4 + 230)
            self.draw_button("Start Screen", self.hud_font, 45, WHITE, 
                            WIDTH / 2, HEIGHT / 4 + 330, time_now, self.show_start_screen)
            pg.display.flip()
            self.wait_for_key()

    # show game over screen
    def show_lose_screen(self):
        pg.mixer.music.stop()
        waiting = True
        time_now = pg.time.get_ticks()

        # high score stuff
        high_score = self.get_high_score()
        beat_high_score = self.new_highscore_check(high_score)
        if beat_high_score:
            self.save_high_score(self.score)
            high_score = self.score

        while waiting:
            self.clock.tick(FPS)
            self.screen.fill(BLACK)
            self.draw_text("GAME OVER", self.hud_font, 80, RED, WIDTH / 2 , HEIGHT / 4 + 30)
            self.draw_text("High Score: " + str(self.get_high_score()), self.hud_font, 50, BLUE, WIDTH / 2, HEIGHT / 4 + 130)
            self.draw_text("Your Score: " + str(self.score), self.hud_font, 50, BLUE, WIDTH / 2, HEIGHT / 4 + 230)
            if beat_high_score:
                self.draw_text("NEW", self.hud_font, 50, GREEN, WIDTH / 2 + 400, HEIGHT / 4 + 130)
            self.draw_button("Start Screen", self.hud_font, 45, WHITE, 
                            WIDTH / 2, HEIGHT / 4 + 330, time_now, self.show_start_screen)

            pg.display.flip()
            self.wait_for_key()

    # screen asking user to confirm they want to quit
    def confirm_quit(self):
        waiting = True
        time_now = pg.time.get_ticks()

        while waiting:
            self.screen.fill(BLACK)
            self.clock.tick(FPS)
            self.draw_text("Are you sure you want to quit?", self.hud_font, 35, RED, WIDTH / 2, HEIGHT / 3)
            self.draw_button("NO", self.hud_font, 40, WHITE, WIDTH / 3, HEIGHT / 2 + 60, time_now, self.show_start_screen)
            self.draw_button("YES", self.hud_font, 40, WHITE, WIDTH * 2 / 3, HEIGHT / 2 + 60, time_now, self.quit)
            pg.display.flip()
            self.wait_for_key()

# function that runs the game indefinitely
# Input: character user selected as string, level, score and health value
# Author: KidsCanCode
def game_loop(char, level, score, health):
    while True:
        g.new(char, level, score, health)
        g.run()

g = Game() # creates game object

g.show_start_screen() # start game