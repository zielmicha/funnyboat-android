import pygame
import math

from water import Water

import util

from locals import *

def init():
    Pirateboat.image = util.load_image("merkkari")
    Pirateboat.death_sound = util.load_sound("blub")

class Pirateboat(pygame.sprite.Sprite):
    image = None
    death_sound = None
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        if not Pirateboat.image or not Pirateboat.death_sound:
            pirateboat.init()

        self.image = Pirateboat.image
        self.rect = pygame.Rect(SCREEN_WIDTH, Water.global_water.get_water_level(SCREEN_WIDTH), self.image.get_width(), self.image.get_height())
        self.area = pygame.display.get_surface().get_rect()

        self.hitmask = pygame.surfarray.array_alpha(self.image)

        self.taking_damage = False
        self.shooting = False
        self.angle = 0
        self.targetangle = 0
        self.dying = False
        self.dead = False

        self.health = 2

        self.dx, self.dy = -1,0.0
        self.t = 0

    def damage(self):
        self.health -= 1

        if self.health == 0:
            self.die()

    def update(self):
        water_levels = [Water.global_water.get_water_level(self.rect.left),
                        Water.global_water.get_water_level(self.rect.centerx),
                        Water.global_water.get_water_level(self.rect.right)]
        self.t += 1

        if self.dying:
            angle = 0.1 * self.target_angle + 0.9 * self.angle

            self.update_angle(angle)
            self.rect.top += self.dy
            self.dy += 1

            if self.rect.bottom > water_levels[1]:
                self.dy *= 0.8

            if self.rect.top >= SCREEN_HEIGHT:
                self.dead = True
            return

        if self.rect.bottom > water_levels[1] + 4:
            self.dy *= 0.8
            if self.rect.top > water_levels[1]:
                self.dy -= 2
            else:
                self.dy -= 0.25 * (self.rect.bottom - water_levels[1])

            self.targetangle = 180.0 / math.pi * math.atan((water_levels[0] - water_levels[2]) / 32.0) + math.sin(self.t * 0.05) * 5

        self.dy += 1

        self.rect.left += self.dx
        self.rect.top += self.dy

        self.update_angle(self.angle * 0.8 + self.targetangle * 0.2)

    def update_angle(self, angle):
        self.angle = angle
        self.image = pygame.transform.rotate(Pirateboat.image, angle)
        self.rect.width = self.image.get_width()
        self.rect.height = self.image.get_height()
        self.hitmask = pygame.surfarray.array_alpha(self.image)

    def get_point(self, point):
        dx = point[0] - self.image.get_rect().centerx
        dy = point[1] - self.image.get_rect().centery

        new_point = [-dy * math.sin(-math.pi / 180.0 * self.angle) + dx * math.cos(-math.pi / 180.0 * self.angle),
                      dy * math.cos(-math.pi / 180.0 * self.angle) + dx * math.sin(-math.pi / 180.0 * self.angle)]
        
        return new_point

    def die(self):
        Pirateboat.death_sound.play(3, 0)
        self.dying = True
        self.dy = -5
        self.target_angle = 90
