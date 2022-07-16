import pygame
from pathlib import Path


class UI:
    def __init__(self, player):
        """
        Class to store all UI images and descriptions of inputs from the player input dict.
        """
        self.x = 25
        self.y = 25
        self.input_keys: dict[pygame.Surface, str] = self.find_binds(player, size=(25, 25))

    # TODO: ErrorHandling to make sure only images that are also input binds are in each directory
    @staticmethod
    def find_binds(player, size: tuple):
        """
        This function will find the player input binds and create a dict
        that stores the image of the key with a description of that key input.
        I don't know how it works
        :param player: Player to use for inputs
        :param size: Size to draw UI on screen
        """

        # Create dict to store input keys
        input_keys: dict[pygame.Surface, str] = dict()

        # Iterate through each type and value in player input
        for input_type, input_value in player.input.items():
            i = 0
            # Path of each input type image folder
            action_path_dir = Path(f"assets/keys/{input_type}")
            # Iterate through each key in each input type folder
            for key_image in sorted(action_path_dir.iterdir()):
                img: pygame.Surface = pygame.image.load(key_image).convert_alpha()
                # Create image from image file name in each input type
                img = pygame.transform.scale(img, size)
                # Add image and description from player input to main dict
                input_keys[img] = list(player.input[input_type].keys())[i].title()
                i += 1

        return input_keys

    def draw(self, screen):
        # No way in hell this is the best way to do it
        # But it works so f*** you
        i = 1
        for image, desc in self.input_keys.items():
            screen.blit(image, (self.x, i*self.y))
            font = pygame.font.Font("assets/dogicapixelbold.ttf", 12)
            text = font.render(desc, True, (255, 255, 255))
            screen.blit(text, dest=(
                self.x + 50,
                i*self.y + text.get_height() / 2))
            i += 1
