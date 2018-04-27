import pygame as pg
import pytmx
from settings import *
from pytmx.util_pygame import load_pygame

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

class TiledMap: # Load map from Tiled to game
    def __init__(self, filename):
        tm = load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth # 50 * 64
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        # render map to surface which is parameter
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer): # Tile layer
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth, 
                                            y * self.tmxdata.tileheight))

    def make_map(self):
        # return the rendered surface
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

class Camera:
    # camera class
    def __init__(self, width, height):
        # parameters are width and height of map
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity): # apply offset to sprite
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect): # apply offset to rectangle
        return rect.move(self.camera.topleft)

    def update(self, target):
        # update the camera's position
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        '''# limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom'''
        self.camera = pg.Rect(x, y, self.width, self.height)