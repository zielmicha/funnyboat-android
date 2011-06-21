import pygame
import math
import random
import sys

import PixelPerfect

from pygame.locals import *

from shark import Shark
from health import Health
from cannonball import Cannonball
from steamboat import Steamboat
from particles import Particles
from mine import Mine
from score import Score
from water import Water
from pirateboat import Pirateboat
from seagull import Seagull
from level import Level
from titanic import Titanic
from powerup import Powerup

import cloud

import util

from locals import *

class Game:
    def __init__(self, screen, usealpha = True, noparticles = False, endless = False):
        self.screen = screen
        self.usealpha = usealpha
        self.noparticles = noparticles

        self.sharks = []
        self.shark_sprites = pygame.sprite.Group()

        self.player = Steamboat()
        self.player_sprite = pygame.sprite.Group()
        self.player_sprite.add(self.player)

        self.health = Health()
        self.health_sprite = pygame.sprite.Group()
        self.health_sprite.add(self.health)

        self.damage_count = 0

        self.t = 0

        self.water = Water.global_water #Water(self.usealpha)
        #Water.global_water = self.water
        self.water_sprite = pygame.sprite.Group()
        self.water_sprite.add(self.water)

        self.sky = util.load_image("taivas")
        self.sky = pygame.transform.scale(self.sky, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.cannonballs = []
        self.cannonball_sprites = pygame.sprite.Group()

        self.pirates = []
        self.pirate_sprites = pygame.sprite.Group()

        self.titanic = None
        self.titanic_sprite = pygame.sprite.Group()

        self.seagulls = []
        self.seagull_sprites = pygame.sprite.Group()

        self.particles = Particles(self.usealpha)
        self.particle_sprite = pygame.sprite.Group()
        self.particle_sprite.add(self.particles)

        self.mines = []
        self.mine_sprites = pygame.sprite.Group()

        self.score = Score()
        self.score_sprite = pygame.sprite.Group()
        self.score_sprite.add(self.score)

        self.powerups = []
        self.powerup_sprites = pygame.sprite.Group()

        self.level = Level(endless)

        self.lastshot = MIN_FIRE_DELAY + 1

        self.gameover = False
        self.gameover_image = None
        self.gameover_rect = None
        self.done = False

        self.pause = False
        font = util.load_font("Cosmetica", 40) #pygame.font.Font(pygame.font.get_default_font(), 36)
        self.pause_image = font.render("Pause", True, (0,0,0))
        self.pause_rect = self.pause_image.get_rect()
        self.pause_rect.center = self.screen.get_rect().center

    def run(self):
        while not self.done:
            if not self.pause:
                if not self.gameover:
                    self.spawn_enemies()

                self.update_enemies()
                self.player.update()
                self.health.update()
                cloud.update()
                for cb in self.cannonballs:
                    cb.update()
                    if (cb.rect.right < 0 and cb.vect[0] < 0) or (cb.rect.left > SCREEN_WIDTH and cb.vect[0] > 0):
                        self.cannonballs.remove(cb)
                        self.cannonball_sprites.remove(cb)
                self.score.update()

                # Add steam particles
                if not self.noparticles:
                    for i in range(STEAM_3):
                        particle_point = self.player.get_point((5.0 + random.random() * 9.0, 0))
                        particle_point[0] += self.player.rect.centerx
                        particle_point[1] += self.player.rect.centery
                        self.particles.add_steam_particle(particle_point)

                    for i in range(STEAM_3):
                        particle_point = self.player.get_point((19.0 + random.random() * 7.0, 5.0))
                        particle_point[0] += self.player.rect.centerx
                        particle_point[1] += self.player.rect.centery
                        self.particles.add_steam_particle(particle_point)

                    if self.titanic:
                        for j in range(4):
                            for i in range(STEAM_3):
                                particle_point = self.titanic.get_point((49 + random.random() * 9.0 + 28 * j, 25))
                                particle_point[0] += self.titanic.rect.centerx
                                particle_point[1] += self.titanic.rect.centery
                                self.particles.add_steam_particle(particle_point)

                    self.particles.update()

                self.water.update()

                if self.player.splash:
                    if not self.noparticles:
                        for i in range(SPLASH_30):
                            r = random.random()
                            x = int(r * self.player.rect.left + (1.0-r) * self.player.rect.right)
                            point = (x, self.water.get_water_level(x))
                            self.particles.add_water_particle(point)
    
                for powerup in self.powerups:
                    powerup.update()
                    if powerup.picked:
                        self.powerups.remove(powerup)
                        self.powerup_sprites.remove(powerup)

                if not self.gameover:
                    self.check_collisions()

                if self.health.hearts_left == 0 and not self.player.dying:
                    self.player.die()

                if self.player.dying and not self.player.dead:
                    if not self.noparticles:
                        for i in range(BLOOD_3):
                            self.particles.add_explosion_particle((self.player.rect.centerx, self.player.rect.centery))
                            self.particles.add_debris_particle((self.player.rect.centerx, self.player.rect.centery))

                if self.player.dead:
                    #self.done = True
                    self.set_gameover()

                if self.damage_count > 0:
                    self.damage_count -= 1
                self.lastshot += 1
                self.t += 1

            self.draw()

            self.handle_events()


        return self.score.get_score()

    def set_gameover(self, message = "Game Over"):
        self.gameover = True
        images = []
        font = util.load_font("Cosmetica", 40) #pygame.font.Font(pygame.font.get_default_font(), 36)
        height = 0
        width = 0
        for text in message.split("\n"):
            images.append(font.render(text, True, (0,0,0)))
            height += images[-1].get_height()
            if images[-1].get_width() > width:
                width = images[-1].get_width()
        self.gameover_image = pygame.Surface((width, height), SRCALPHA, 32)
        self.gameover_image.fill((0,0,0,0))
        for i in range(len(images)):
            rect = images[i].get_rect()
            rect.top = i * images[i].get_height()
            rect.centerx = width / 2
            self.gameover_image.blit(images[i], rect)

        self.gameover_rect = self.gameover_image.get_rect()
        self.gameover_rect.center = self.screen.get_rect().center
    
    def translate_mouse_event(self, event):
     if event.type in (MOUSEBUTTONDOWN, ):
       rx = event.pos[0] / float(SCREEN_WIDTH)
       ry = event.pos[1] / float(SCREEN_HEIGHT)
       if rx < 0.0:
          key = K_LEFT
       elif rx > 1.0:
          key = K_RIGHT
       elif ry > 0.5:
          key = K_SPACE
       else:
          key = K_UP
       event = pygame.event.Event(KEYUP if event.type == MOUSEBUTTONUP else KEYDOWN, key=key)
     
     self.player.move_left(False)
     self.player.move_right(False)
     return event
    
    def handle_events(self):
        nextframe = False
        framecount = 0
        while not nextframe:
          # wait until there's at least one event in the queue
          pygame.event.post(pygame.event.wait())
          for event in pygame.event.get():
            #event = pygame.event.wait()
            event = self.translate_mouse_event(event)
            if event.type == QUIT or \
               event.type == KEYDOWN and event.key == K_ESCAPE:
                self.done = True
                nextframe = True
            elif event.type == NEXTFRAME:
                nextframe = True
                framecount += 1
            elif self.gameover:
                if event.type == JOYBUTTONDOWN:
                    self.done = True
                    nextframe = True
                elif event.type == KEYDOWN:
                    self.done = True
                    nextframe = True
            elif event.type == MOUSEBUTTONDOWN:
                self.done = True
                nextframe = True
                continue
            elif event.type == JOYAXISMOTION:
                if event.axis == 0:
                    if event.value < -0.5:
                        self.player.move_left(True)
                    elif event.value > 0.5:
                        self.player.move_right(True)
                    else:
                        self.player.move_left(False)
                        self.player.move_right(False)
            elif event.type == JOYBUTTONDOWN:
                if event.button == 0:
                  if not self.pause:
                    self.player.jump()
                elif event.button == 1:
                  if not self.pause:
                    if self.lastshot > MIN_FIRE_DELAY and not self.player.dying:
                        cb = Cannonball(self.player.rect, self.player.angle)
                        self.cannonballs.append(cb)
                        self.cannonball_sprites.add(cb)
                        self.lastshot = 0
                elif event.button == 5:
                    pygame.image.save(self.screen, "sshot.tga")
                    print "Screenshot saved as sshot.tga"
                elif event.button == 8:
                    self.set_pause()
            elif event.type == KEYDOWN:
                if event.key == K_LEFT:
                    self.player.move_left(True)
                elif event.key == K_RIGHT:
                    self.player.move_right(True)
                elif event.key == K_SPACE:
                  if not self.pause:
                    # Only 3 cannonballs at once
                    # Maximum firing rate set at the top
                    if self.lastshot > MIN_FIRE_DELAY and not self.player.dying:
                        cb = Cannonball(self.player.rect, self.player.angle)
                        self.cannonballs.append(cb)
                        self.cannonball_sprites.add(cb)
                        self.lastshot = 0
                elif event.key == K_UP:
                    if not self.pause:
                        self.player.jump()
                elif event.key == K_s:
                    pygame.image.save(self.screen, "sshot.tga")
                    print "Screenshot saved as sshot.tga"
                elif event.key == K_p:
                    self.set_pause()
            elif event.type == KEYUP:
                if event.key == K_LEFT:
                    self.player.move_left(False)
                elif event.key == K_RIGHT:
                    self.player.move_right(False)
        
        tiling = util.get_tiling()
        if tiling == -1:
            self.player.move_left(True)
        elif tiling == 1:
            self.player.move_right(True)
        #if framecount > 1:
        #    print "Missed " + str(framecount - 1) + " frames!"

    def set_pause(self):
        self.pause = not self.pause

    def draw(self):
        self.screen.blit(self.sky, self.screen.get_rect())
        self.health_sprite.draw(self.screen)
        self.score_sprite.draw(self.screen)
        self.player_sprite.draw(self.screen)
        self.powerup_sprites.draw(self.screen)
        self.pirate_sprites.draw(self.screen)
        if self.titanic:
            self.titanic_sprite.draw(self.screen)
        self.seagull_sprites.draw(self.screen)
        cloud.draw(self.screen)
        self.shark_sprites.draw(self.screen)
        self.mine_sprites.draw(self.screen)
        self.cannonball_sprites.draw(self.screen)
        self.water_sprite.draw(self.screen)
        if not self.noparticles:
            self.particle_sprite.draw(self.screen)

        if self.pause:
            self.screen.blit(self.pause_image, self.pause_rect)

        if self.gameover:
            self.screen.blit(self.gameover_image, self.gameover_rect)

        if self.level.t < 120:
            font = util.load_font("Cosmetica", 16)
            image = None
            i = 0
            if self.level.phase < len(self.level.phase_messages):
              for text in self.level.phase_messages[self.level.phase].split("\n"):
                image = font.render(text, True, (0,0,0))
                rect = image.get_rect()
                rect.centerx = self.screen.get_rect().centerx
                rect.top = 100 + rect.height * i
                blit_image = pygame.Surface((image.get_width(), image.get_height()))
                blit_image.fill((166,183,250))
                blit_image.set_colorkey((166,183,250))
                blit_image.blit(image, image.get_rect())
                if self.level.t > 60:
                    blit_image.set_alpha(255 - (self.level.t - 60) * 255 / 60)
                self.screen.blit(blit_image, rect)
                i += 1

        pygame.display.flip()



    def check_collisions(self):
        collisions = PixelPerfect.spritecollide_pp(self.player, self.powerup_sprites, 0)
        for powerup in collisions:
            if not powerup.fading:
                if not self.player.dying:
                    self.health.add()
                    powerup.pickup()

        collisions = PixelPerfect.spritecollide_pp(self.player, self.mine_sprites, 0)

        for mine in collisions:
            if not mine.exploding:
                if not self.player.dying:
                    self.health.damage()
                    mine.explode()

        collisions = PixelPerfect.spritecollide_pp(self.player, self.shark_sprites, 0)

        for shark in collisions:
            if not shark.dying:
                if not self.player.dying:
                    self.health.damage()
                    shark.die()

        collisions = PixelPerfect.spritecollide_pp(self.player, self.cannonball_sprites, 0)

        for cb in collisions:
            if not self.player.dying:
                self.health.damage()
                self.cannonballs.remove(cb)
                self.cannonball_sprites.remove(cb)
                Mine.sound.play() # Umm... the mine has a nice explosion sound.

        collisions = PixelPerfect.groupcollide_pp(self.cannonball_sprites, self.shark_sprites, 0, 0)

        for cb in dict.keys(collisions):
            for shark in collisions[cb]:
                # The test on cb.vect is a rude hack preventing cannonballs from pirate ships from killing sharks.
                if not shark.dying and cb.vect[0] > 0:
                    self.score.add(15)
                    shark.die()
                    self.cannonballs.remove(cb)
                    self.cannonball_sprites.remove(cb)
                    break

        collisions = PixelPerfect.groupcollide_pp(self.cannonball_sprites, self.seagull_sprites, 0, 0)

        for cb in dict.keys(collisions):
            for seagull in collisions[cb]:
                # cb.vect test is a rude hack preventing pirates from killing seagulls
                if not seagull.dying and cb.vect[0] > 0:
                    self.score.add(75)
                    seagull.die()
                    self.cannonballs.remove(cb)
                    self.cannonball_sprites.remove(cb)
                    break

        collisions = PixelPerfect.groupcollide_pp(self.cannonball_sprites, self.pirate_sprites, 0, 0)

        for cb in dict.keys(collisions):
            for pirate in collisions[cb]:
                # cb.vect hack for preventing pirates from killing each other
                if not pirate.dying and cb.vect[0] > 0:
                    Mine.sound.play() # Umm... the mine has a nice sound.
                    self.score.add(25)
                    pirate.damage()
                    self.cannonballs.remove(cb)
                    self.cannonball_sprites.remove(cb)
                    break

        if self.titanic:
            collisions = PixelPerfect.spritecollide_pp(self.titanic, self.cannonball_sprites, 0)
            for cb in collisions:
                if not self.titanic.dying and cb.vect[0] > 0:
                    Mine.sound.play()
                    self.score.add(7)
                    self.titanic.damage()
                    self.cannonballs.remove(cb)
                    self.cannonball_sprites.remove(cb)
                    break

    def update_enemies(self):
        for mine in self.mines:
            mine.update()
            if mine.exploding:
                if mine.explode_frames == 0:
                    self.mines.remove(mine)
                    self.mine_sprites.remove(mine)
                # this should really be done in the Mine class, but oh well, here's some explosion effects:
                if not self.noparticles:
                    for i in range(3):
                        self.particles.add_explosion_particle((mine.rect.centerx, mine.rect.top + mine.image.get_rect().centerx))
                        self.particles.add_debris_particle((mine.rect.centerx, mine.rect.top + mine.image.get_rect().centerx))
            if mine.rect.right < self.screen.get_rect().left:
                self.mines.remove(mine)
                self.mine_sprites.remove(mine)

        for shark in self.sharks:
            shark.update()
            if shark.dying:
                if not self.noparticles:
                    self.particles.add_blood_particle(shark.rect.center)
            if shark.rect.right < self.screen.get_rect().left or shark.dead:
                self.sharks.remove(shark)
                self.shark_sprites.remove(shark)

        for pirate in self.pirates:
            pirate.update()
            if pirate.t % 50 == 0 and not pirate.dying:
                # Pirate shoots, this should probably be handled by the Pirateboat class
                cb = Cannonball(pirate.rect, pirate.angle, left = True)
                self.cannonballs.append(cb)
                self.cannonball_sprites.add(cb)
            if pirate.rect.right < self.screen.get_rect().left or pirate.dead:
                self.pirates.remove(pirate)
                self.pirate_sprites.remove(pirate)
            elif pirate.dying:
                if not self.noparticles:
                    for i in range(3):
                        self.particles.add_explosion_particle((pirate.rect.centerx, pirate.rect.centery))
                        self.particles.add_wood_particle((pirate.rect.centerx, pirate.rect.centery))

        if self.titanic:
            self.titanic.update()
            if self.titanic.t % 100 == 0 and not self.titanic.dying:
                for i in range(3):
                    cb = Cannonball(self.titanic.rect, self.titanic.angle + (i-1)*10 - 50, left = True)
                    self.cannonballs.append(cb)
                    self.cannonball_sprites.add(cb)
            elif self.titanic.t % 100 == 50 and not self.titanic.dying:
                for i in range(3):
                    cb = Cannonball(self.titanic.rect, self.titanic.angle + (i-1)*10 - 60, left = True)
                    self.cannonballs.append(cb)
                    self.cannonball_sprites.add(cb)
            if self.titanic.dead:
                self.set_gameover("Congratulations!\nYou sunk Titanic!")
                self.titanic = None

        for seagull in self.seagulls:
            seagull.update()
            if seagull.rect.right < 0 or seagull.dead:
                self.seagulls.remove(seagull)
                self.seagull_sprites.remove(seagull)

    def spawn_enemies(self):
        spawns = self.level.get_spawns()
        if spawns[Level.SHARKS]:
            # Make a new shark
            self.sharks.append(Shark())
            self.shark_sprites.add(self.sharks[-1])

        if spawns[Level.PIRATES]:
            # Make a new pirate ship
            self.pirates.append(Pirateboat())
            self.pirate_sprites.add(self.pirates[-1])

        if spawns[Level.MINES]:
            self.mines.append(Mine())
            self.mine_sprites.add(self.mines[-1])

        if spawns[Level.SEAGULLS]:
            self.seagulls.append(Seagull())
            self.seagull_sprites.add(self.seagulls[-1])

        if spawns[Level.TITANIC]:
            self.titanic = Titanic()
            self.titanic_sprite.add(self.titanic)

        if spawns[Level.POWERUPS]:
            self.powerups.append(Powerup())
            self.powerup_sprites.add(self.powerups[-1])

