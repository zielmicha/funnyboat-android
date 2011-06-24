import pygame

from water import Water
from locals import *
import cloud
import util

class Menu:
    NEWGAME = 0
    HIGHSCORES = 1
    OPTIONS = 3
    QUIT = 2

    STORY = 0
    ENDLESS = 1
    def __init__(self, screen, gametype_select = False):
        self.screen = screen

        self.gametype_select = gametype_select

        self.sky = util.load_image("taivas")

        self.water = Water.global_water
        self.water_sprite = pygame.sprite.Group()
        self.water_sprite.add(self.water)

        self.logo = util.load_image("logo")

        self.font = util.load_font("Cosmetica", 28)

        self.url_font = util.load_font("Cosmetica", 14)
        self.option_rects = {}
        self.selection = 0
        self.t = 0

    def run(self):
        done = False

        while not done:
            self.screen.blit(self.sky, self.screen.get_rect())
            self.water.update()
            self.water_sprite.draw(self.screen)

            if not self.gametype_select:
                self.render("New Game", Menu.NEWGAME)
                self.render("High Scores", Menu.HIGHSCORES)
                #self.render("Options", Menu.OPTIONS)
                self.render("Quit", Menu.QUIT)
            else:
                self.render("Story mode", Menu.STORY)
                self.render("Endless mode", Menu.ENDLESS)

            cloud.update()

            cloud.draw(self.screen)

            rect = self.logo.get_rect()
            rect.centerx = self.screen.get_rect().centerx
            rect.top = 0
            self.screen.blit(self.logo, rect)

            image = self.url_font.render("https://github.com/zielmicha/funnyboat-android", True, (0,0,0))
            bottom = rect.bottom
            rect = image.get_rect()
            rect.midbottom = self.screen.get_rect().midbottom
            #rect.bottomright = self.screen.get_rect().bottomright
            #rect.bottom = bottom
            self.screen.blit(image, rect)

            pygame.display.flip()

            self.t += 1

            nextframe = False
            while not nextframe:
                pygame.event.post(pygame.event.wait())
                for event in pygame.event.get():
                    if event.type == QUIT or \
                        event.type == KEYDOWN and event.key == K_ESCAPE:
                        self.selection = -1
                        done = True
                        nextframe = True
                    elif event.type == MOUSEBUTTONUP or event.type == MOUSEBUTTONDOWN:
                        pos = event.pos
                        for id, rect in self.option_rects.items():
                            if rect.collidepoint(pos):
                                self.selection = id
                    if event.type == MOUSEBUTTONUP:
                        done = True
                    elif event.type == NEXTFRAME:
                        nextframe = True
                    elif event.type == JOYAXISMOTION:
                        if event.axis == 1:
                            if event.value < -0.5:
                                self.selection -= 1
                                if not self.gametype_select:
                                    if self.selection == Menu.OPTIONS:
                                        self.selection = Menu.HIGHSCORES
                                if self.selection < 0:
                                    self.selection = 0
                            if event.value > 0.5:
                                self.selection += 1
                                if not self.gametype_select:
                                    if self.selection == Menu.OPTIONS:
                                        self.selection = Menu.QUIT
                                    if self.selection > Menu.QUIT:
                                        self.selection = Menu.QUIT
                                else:
                                    if self.selection > Menu.ENDLESS:
                                        self.selection = Menu.ENDLESS
                    elif event.type == JOYBUTTONDOWN:
                        if event.button == 0:
                            done = True
                    elif event.type == KEYDOWN:
                        if event.key == K_UP:
                            self.selection -= 1
                            if not self.gametype_select:
                                if self.selection == Menu.OPTIONS:
                                    self.selection = Menu.HIGHSCORES
                            if self.selection < 0:
                                self.selection = 0
                        elif event.key == K_DOWN:
                            self.selection += 1
                            if not self.gametype_select:
                                if self.selection == Menu.OPTIONS:
                                    self.selection = Menu.QUIT
                                if self.selection > Menu.QUIT:
                                    self.selection = Menu.QUIT
                            else:
                                if self.selection > Menu.ENDLESS:
                                    self.selection = Menu.ENDLESS
                        elif event.key == K_SPACE or event.key == K_RETURN:
                            done = True

        return self.selection

    def render(self, text, id):
        color = (0,0,0)
        if self.selection == id:
            color = (220, 120, 20)

        image = self.font.render(text, True, color)
        rect = image.get_rect()
        rect.centerx = self.screen.get_rect().centerx
        rect.top = self.logo.get_height() + id * rect.height * 1.1
	self.option_rects[id] = rect
	
        self.screen.blit(image, rect)
