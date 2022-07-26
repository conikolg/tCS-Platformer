# --- NOTES ---

# created 7/25/22 6:30 pm
# starting with https://pythonprogramming.net/adding-sounds-music-pygame/ as a guide

# this class is mostly a wrapper for the pygame.mixer.Sound class
# my idea was that sounds will mostly be managed with helper functions and simple names
# rather than having to deal with the Sound objects directly

# example usage:

# creating a sound:
# Sound("jump", "assets/sounds/jump.mp3") 

# playing a sound:
# playSound("jump")

# stopping a sound:
# stopSound("jump")

# --- CODE ---

import pygame

# sounds dictionary which maps sound names (strings) to Sound objects
sounds = {}

"""
# controls the volume of the entire game, independent of the volume property of each sound effect
# integer ranging from 0 to 100 representing a percentage
# (in other words you can tune the game's volume level and a sound's volume level independently)
GAME_VOLUME = 100
"""


class Sound:
    def __init__(self, name, fpath, volume=100):
        """
        Creates a sound object that can be started and stopped at will.

        :param name: string specifying the arbitrary name used to reference to this sound effect
        :param fpath: string specifying the file path to the sound effect file to load
        :param volume: integer ranging from 0 to 100, specifies the volume percentage (defaults to 100%, full volume of original sound effect file)
        """

        # setup properties
        self.name = name
        self.fpath = fpath
        self.volume = volume
        self.pygameSound = pygame.mixer.Sound(fpath)
        self.pygameSound.set_volume(volume / 100)

        # add this sound to sounds dictionary when created
        sounds[name] = self


# plays the sound with the given name
# when a sound is played, it will start from where it last paused
# if it hasn't been played yet, it simply starts from the beginning
# if a sound was previously played until completion, this will restart it
def play_sound(name):
    if name not in sounds:
        raise ValueError(
            f"Invalid value given to play_sound(). Sound with name {name} has not been loaded into sounds dictionary.")
    sound_obj = sounds[name]
    pygame.mixer.Sound.play(sound_obj.pygameSound)


# stops a sound with the given name so that it stops producing noise
# unlike pause_sound, this will cause the sound to restart from the beginning when it is played next
def stop_sound(name):
    if name not in sounds:
        raise ValueError(
            f"Invalid value given to stop_sound(). Sound with name {name} has not been loaded into sounds dictionary.")
    sound_obj = sounds[name]
    pygame.mixer.Sound.stop(sound_obj.pygameSound)


"""
# NOT YET IMPLEMENTED
# pauses a sound with the given name so that it stops producing noise
# unlike stop_sound, this will cause the sound to start from where it paused when it is played next
def pause_sound(name):
    if name not in sounds:
        raise ValueError(
            f"Invalid value given to pause_sound(). Sound with name {name} has not been loaded into sounds dictionary.")
    sound_obj = sounds[name]
    pygame.mixer.Sound.pause(sound_obj.pygameSound)
"""
