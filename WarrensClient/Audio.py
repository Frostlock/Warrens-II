"""
This module contains utility functions related to the GUI audio.
Loading music & sound effects and managing playback.
"""
import pygame
import os

from WarrensClient.CONFIG import AUDIO

sounds = None


def init_audio():
    if pygame.mixer.get_init() is None:
        print("Warning: pygame mixer not properly initialized. Audio will be disabled.")
        AUDIO.ENABLED = False
    else:
        # Load music
        pygame.mixer.music.load(AUDIO.MUSIC)
        # Load sound effects
        global sounds
        sounds = {}
        # r=root, d=directories, f = files
        for r, d, f in os.walk(AUDIO.SFX):
            for file in f:
                if file[-4:].upper() == ".WAV":
                    sounds[file[:-4].upper()] = pygame.mixer.Sound(os.path.join(r, file))


def start_music():
    pygame.mixer.music.play()


def play_sound(sound_name):
    global sounds
    try:
        sounds[sound_name.upper()].play()
    except KeyError:
        print("Warning: Failed to play sound " + sound_name)

