import pygame
import math

from water import Water
from locals import *

import util

class Cannonball (pygame.sprite.Sprite):
    image = None
    sound = None
    def __init__(self, ship_rect, ship_angle, left = False):
        pygame.sprite.Sprite.__init__(self)

        if not Cannonball.image:
            Cannonball.image = util.load_image("kuti")
        if not Cannonball.sound:
            Cannonball.sound = util.load_sound("pam")
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()

        self.image = Cannonball.image


        self.hitmask = pygame.surfarray.array_alpha(self.image)

        Cannonball.sound.play()

        #self.dy = -5
        #self.dx = 10
        # Shoot at an angle of 25 relative to the ship
        if not left:
            self.rect = pygame.Rect(ship_rect.right, ship_rect.centery, self.image.get_width(), self.image.get_height())
            self.vect = [math.cos((-ship_angle - 25.0) / 180.0 * math.pi) * 11.0,
                         math.sin((-ship_angle - 25.0) / 180.0 * math.pi) * 11.0]
        else:
            self.rect = pygame.Rect(ship_rect.left, ship_rect.centery, self.image.get_width(), self.image.get_height())
            self.vect = [math.cos((-ship_angle + 180.0 + 25.0) / 180.0 * math.pi) * 11.0,
                         math.sin((-ship_angle + 180.0 + 25.0) / 180.0 * math.pi) * 11.0]
        # Will have to think this through later
        #self.vect = [10, -2] #vect

    def update(self):
        self.rect.left += self.vect[0] #self.dx
        self.rect.top += self.vect[1] #self.dy

        self.vect[1] += 0.4
        #self.dy += 1
        if self.rect.bottom > Water.global_water.get_water_level(self.rect.centerx):
            self.vect[0] *= 0.9
            self.vect[1] *= 0.9

