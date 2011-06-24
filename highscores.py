import pygame
import os
import sys
import codecs

import util
from locals import *
from water import Water

import cloud

class Highscores:
    def __init__(self, screen, new_score = -1, endless = False):
        self.screen = screen

        # using HOME doesn't work on Windows :-(
        self.pathname = ""
        try: 
            self.pathname = os.environ["HOME"] + "/.funnyboat"
        except:
            try:
                self.pathname = os.environ["APPDATA"] + "/Funny Boat"
            except:
                print "Couldn't get environment variable for home directory"
                self.pathname = "."
                #self.done = True
                #return
        if not endless:
            self.filename = self.pathname + "/scores"
        else:
            self.filename = self.pathname + "/endless_scores"

        self.scores = []
        self.done = False

        try:
            if not os.path.exists(self.pathname):
                os.mkdir(self.pathname)
        except:
            print "Can't make directory " + self.pathname
            self.done = True
            return

        if not os.path.exists(self.filename):
            #print "Creating dummy high scores"
            self.dummy_scores()
        else:
            try:
                f = codecs.open(self.filename, "r", "utf_8")
                i = 0
                name, score = "", 0
                for line in f:
                    if i % 2 == 0:
                        name = line.strip()
                    else:
                        try:
                            score = int(line)
                        except:
                            print "Corrupt high score file."
                            self.dummy_scores()
                            break
                        self.scores.append((name, score))
                    i += 1
            except:
                self.dummy_scores()
                print "Can't open file " + self.filename + " or file corrupt"

        if len(self.scores) < 10:
            print "Corrupt high score file."
            self.dummy_scores()

        #self.font = pygame.font.Font(pygame.font.get_default_font(), 12)
        self.font = util.load_font("Cosmetica", 14)
        #self.title_font = pygame.font.Font(pygame.font.get_default_font(), 24)
        self.title_font = util.load_font("Cosmetica", 28)
        self.title = self.title_font.render("High Scores", True, (0,0,0))

        self.sky = util.load_image("taivas")

        self.inputting = False
        self.input_score = -1 

        if new_score > self.scores[9][1]:
            #print "It's a new high score!"
            self.inputting = True
            for i in range(10):
                if self.scores[i][1] < new_score:
                    self.input_score = i
                    for j in range(9 - i):
                        self.scores[9 - j] = self.scores[8 - j]
                    self.scores[i] = ["", new_score]
                    break

    def run(self):
        water = Water.global_water
        water_sprite = pygame.sprite.Group()
        water_sprite.add(water)
        if util.android:
            util.android.show_keyboard()
        while not self.done:
            self.screen.blit(self.sky, self.screen.get_rect())
            water.update()
            cloud.update()
            cloud.draw(self.screen)
            water_sprite.draw(self.screen)

            rect = self.title.get_rect()
            rect.centerx = self.screen.get_rect().centerx
            rect.top = 10

            self.screen.blit(self.title, rect)

            for i in range(10):
                color = (0,0,0)
                if self.inputting and self.input_score == i:
                    color = (220, 120, 20)
                score = self.scores[i]
                image = self.font.render(str(i + 1) + ". " + score[0], True, color)
                rect = image.get_rect()
                rect.top = 50 + i * 1.5 * rect.height
                rect.left = 10
                self.screen.blit(image, rect)

                image = self.font.render(str(score[1]), True, color)
                rect = image.get_rect()
                rect.top = 50 + i * 1.5 * rect.height
                rect.right = self.screen.get_rect().right - 10
                self.screen.blit(image, rect)

            pygame.display.flip()

            nextframe = False
            while not nextframe:
                pygame.event.post(pygame.event.wait())
                for event in pygame.event.get():
                    if event.type == NEXTFRAME:
                        nextframe = True
                        continue
                    if self.inputting:
                        if event.type == QUIT:
                            self.inputting = False
                            self.write_scores()
                        
                        if event.type == KEYDOWN:
                            if event.key == K_RETURN or event.key == K_ESCAPE:
                                self.inputting = False
                                self.write_scores()
                            elif event.key == K_BACKSPACE:
                                if len(self.scores[self.input_score][0]) != 0:
                                    self.scores[self.input_score][0] = self.scores[self.input_score][0][:-1]
                            elif event.key == K_SPACE or event.unicode != " ":
                                if len(self.scores[self.input_score][0]) < 32:
                                    self.scores[self.input_score][0] += event.unicode
                    else:
                        if event.type == KEYDOWN or event.type == QUIT or event.type == JOYBUTTONDOWN or event.type == MOUSEBUTTONDOWN:
                            self.done = True
                            nextframe = True

    def dummy_scores(self):
        self.scores = []
        #for i in range(10):
        self.scores.append(("Funny Boat",     2000)) # 1
        self.scores.append(("Hectigo",        1500)) # 2
        self.scores.append(("JDruid",         1000)) # 3
        self.scores.append(("Pekuja",          750)) # 4
        self.scores.append(("Pirate",          500)) # 5
        self.scores.append(("Shark",           400)) # 6
        self.scores.append(("Seagull",         300)) # 7
        self.scores.append(("Naval mine",      200)) # 8
        self.scores.append(("Cannonball",      100)) # 9
        self.scores.append(("Puffy the Cloud",  50)) #10

        self.write_scores()

    def write_scores(self):
        try:
            f = codecs.open(self.filename, "w", "utf_8")
            for i in range(10):
                print >> f, self.scores[i][0]
                print >> f, self.scores[i][1]
        except:
            print "Failed to write high scores to file " + self.filename
            self.done = True
            return
        if util.android:
            util.android.hide_keyboard()
