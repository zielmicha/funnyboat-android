#!/usr/bin/python
import pygame

try:
    import android
    import sys
    class surfarray:
        def array_alpha(self, img): pass
    pygame.surfarray = surfarray()
except ImportError:
    android = None

import pygame
import math
import random
import sys

import PixelPerfect

from pygame.locals import *

from water import Water
from menu import Menu
from game import Game
from highscores import Highscores

import util

from locals import *

import health
import cloud
import mine
import steamboat
import pirateboat
import shark
import seagull

import water
import game
import particles
import titanic
import powerup

def init():
    health.init()
    steamboat.init()
    shark.init()
    pirateboat.init()
    cloud.init()
    mine.init()
    seagull.init()
    
    for module in [health, steamboat, shark, pirateboat, cloud, mine, seagull, water, game,
                   particles, titanic, powerup]:
        module.SCREEN_WIDTH = SCREEN_WIDTH
        module.SCREEN_HEIGHT = SCREEN_HEIGHT

def load_size():
    surf = pygame.display.set_mode((0, 0))
    width, height = surf.get_size()
    scale = 300.0 / height
    new_width = int(scale * width)
    new_height = 300
    if (new_width % 5) != 0:
        new_width -= (new_width % 5)
    print new_width, new_height
    return new_width, new_height

def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    
    if android:
        android.init()
        android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
    pygame.init()
    
    SCREEN_WIDTH, SCREEN_HEIGHT = load_size()
    
    noparticles = False
    usealpha = True

    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg == "-np":
                noparticles = True
            elif arg == "-na":
                usealpha = False
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_icon(util.load_image("kuvake"))
    pygame.display.set_caption("Trip on the Funny Boat")

    init()

    joy = None
    if pygame.joystick.get_count() > 0:
        joy = pygame.joystick.Joystick(0)
        joy.init()

    try:
        util.load_music("JDruid-Trip_on_the_Funny_Boat")
        util.mixer.music.play(-1)
    except:
        pass

    pygame.time.set_timer(NEXTFRAME, 1000 / FPS) # 30 fps

    Water.global_water = Water(usealpha)

    while True:
        selection = Menu(screen).run()
        if selection == Menu.NEWGAME:
            #print "New game!"
            selection = Menu(screen, gametype_select = True).run()
            if selection == Menu.STORY:
                score = Game(screen, usealpha, noparticles).run()
                #print "Final score: " + str(score)
                Highscores(screen, score).run()
            elif selection == Menu.ENDLESS:
                score = Game(screen, usealpha, noparticles, True).run()
                #print "Final score: " + str(score)
                Highscores(screen, score, True).run()
        elif selection == Menu.HIGHSCORES:
            #print "High scores!"
            selection = Menu(screen, gametype_select = True).run()
            if selection == Menu.STORY:
                Highscores(screen).run()
            elif selection == Menu.ENDLESS:
                Highscores(screen, endless = True).run()
        #elif selection == Menu.OPTIONS:
        #print "Options!"
        #elif selection == Menu.QUIT:
        else:
            #print "Quit! :-("
            return


if __name__ == '__main__':
    main()
