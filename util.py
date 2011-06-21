import pygame

try:
    import android
    import android_mixer as mixer
    android.accelerometer_enable(True)
except ImportError:
    android = None
    from pygame import mixer

# Some general utility functions here

def load_font(name, size):
    return pygame.font.Font("data/" + name + ".ttf", size)

def load_image(name):
    return pygame.image.load("data/" + name + ".png").convert_alpha()

def load_sound(name):
    return mixer.Sound("data/" + name + ".ogg")

def load_music(name):
    # The all-caps ogg is because the original file just happened to be that way
    mixer.music.load("data/" + name + ".ogg")

def android_check_pause():
    if android:
       if android.check_pause():
            android.wait_for_resume()

def get_tiling():
			x, y, z = android.accelerometer_reading()
			xrel = y/10
			if xrel > 0.2: return 1
			elif xrel < 0.2: return -1
			else: return 0
			
if not android:
			def get_tiling():
						return 0



