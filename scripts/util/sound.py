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
# play_sound("jump")

# stopping a sound:
# stop_sound("jump")

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


class _Sound:
    def __init__(self, name, fpath, volume=100):
        """
        Creates a sound object that can be started and stopped at will.

        :param name: string specifying the arbitrary name used to reference to this sound effect
        :param fpath: string specifying the file path to the sound effect file to load
        :param volume: integer ranging from 0 to 100, specifies the volume percentage (defaults to 100%,
        full volume of original sound effect file)
        """

        # setup properties
        self.name = name
        self.fpath = fpath
        self.volume = volume
        self.original_volume = volume
        self.pygameSound = pygame.mixer.Sound(fpath)
        self.pygameSound.set_volume(volume / 100)

        # add this sound to sounds dictionary when created
        sounds[name] = self


def load_sound(name: str, filename: str = None, volume: int = 100) -> _Sound:
    """
    Load a sound if not already loaded.

    If the name assigned has already been loaded, it is retrieved from memory
    instead of reloading it from disk, ignoring the filename.

    :param name: a string assigned to the sound as a shortcut.
    :param filename: a string denoting the path of the target file on disk.
    :param volume: an int denoting initial volume, default to 100.
    :return: the loaded Sound object.
    """

    # Is there already a sound loaded with this name?
    if name in sounds:
        return sounds[name]

    # Was a file specified?
    if filename is None:
        raise Exception(f"No sound registered with {name=}. Provide a filepath to load a sound for this name.")

    # Load sound from disk
    sound = _Sound(name, filename, volume=volume)
    sounds[name] = sound
    return sound


def play_sound(name: str) -> None:
    """Plays the sound with the given name from the beginning."""
    if name not in sounds:
        raise ValueError(
            f"Invalid value given to play_sound(). Sound with {name=} has not been loaded into sounds dictionary.")
    sound_obj = sounds[name]
    pygame.mixer.Sound.play(sound_obj.pygameSound)


def stop_sound(name: str) -> None:
    """Stops a sound with the given name."""
    if name not in sounds:
        raise ValueError(
            f"Invalid value given to stop_sound(). Sound with {name=} has not been loaded into sounds dictionary.")
    sound_obj = sounds[name]
    pygame.mixer.Sound.stop(sound_obj.pygameSound)


def mute_sound(name: str) -> None:
    """Mutes a sound with the given name, so that it can later be resumed/unmuted."""
    if name not in sounds:
        raise ValueError(
            f"Invalid value given to mute_sound(). Sound with {name=} has not been loaded into sounds dictionary.")
    sound_obj = sounds[name]
    sound_obj.original_volume = sound_obj.volume
    sound_obj.volume = 0
    sound_obj.pygameSound.set_volume(sound_obj.volume / 100)


def unmute_sound(name: str) -> None:
    """Unmutes a sound with the given name"""
    if name not in sounds:
        raise ValueError(
            f"Invalid value given to unmute_sound(). Sound with {name=} has not been loaded into sounds dictionary.")
    sound_obj = sounds[name]
    sound_obj.volume = sound_obj.original_volume
    sound_obj.pygameSound.set_volume(sound_obj.volume / 100)
