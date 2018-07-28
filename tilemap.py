# Tilemap File
import pygame as pg
import pytmx
from settings import *
from pytmx.util_pygame import load_pygame

# All code here comes from KidsCanCode

# Class that load the map from Tiled
class TiledMap: 
    # initialises values before rendering
    # Input: name of map file
    def __init__(self, filename):
        tm = load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth # 50 * 64
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    # makes the map
    # returns the rendered map
    def make_map(self):
        # return the rendered surface
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

    # render map to surface 
    # Input: screen surface
    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer): # Tile layer
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth, 
                                            y * self.tmxdata.tileheight))

# Class that makes the scrolling camera
class Camera:
    # initialises camera class attributes
    # Input: width and height of map
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    # apply offset to sprite
    # Input: sprite object
    def apply(self, entity): 
        return entity.rect.move(self.camera.topleft)

    # apply offset to rectangle
    # Input: object rectangle attribute
    def apply_rect(self, rect): 
        return rect.move(self.camera.topleft)

    # update the camera's position
    def update(self, target):
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)
        self.camera = pg.Rect(x, y, self.width, self.height)
