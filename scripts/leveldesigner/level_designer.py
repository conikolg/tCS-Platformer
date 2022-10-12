import csv
from pathlib import Path

import pandas as pd
import pygame
import pymunk

from scripts.enemy.basic_enemy import BasicEnemy
from scripts.scenes.exit import Exit
from scripts.scenes.simple_platform import Platform


class LevelDesigner:
    def __init__(self, world: pymunk.Space, level: int = 1):
        """
        Collects data from csv files to display objects and obstacles in the level.

        :param level: Current level csv file to display.
        """

        self.level = level
        self.world = world

        # Level layout File resources
        self.level_file_xlsx = pd.read_excel(Path("scripts/leveldesigner/level_data.xlsx"),
                                             sheet_name=f"level{self.level}_data", header=None)
        self.level_file_xlsx.to_csv(f"scripts/leveldesigner/level{self.level}_data.csv", index=False,
                                    header=False)
        self.level_file_csv = Path(f"scripts/leveldesigner/level{self.level}_data.csv")

        # Level layout initialization
        self.rows: int = len(pd.read_csv(self.level_file_csv).axes[0]) + 1
        self.cols: int = len(pd.read_csv(self.level_file_csv).axes[1])
        self.tile_size: int = 64
        self.level_data: list = [[-1] * self.cols for row in range(self.rows)]
        self.max_y = self.tile_size * len(self.level_data)
        self.max_x = self.tile_size * len(self.level_data[0])

        # Preparing ground assets
        self.top_ground_img: pygame.Surface = pygame.image.load(
            Path("assets/platforms/Textures-16.png")).convert_alpha().subsurface((32, 0, 16, 16))
        self.top_ground_img = pygame.transform.scale(self.top_ground_img, (self.tile_size, self.tile_size))

        self.ground_img: pygame.Surface = pygame.image.load(
            Path("assets/platforms/Textures-16.png")).convert_alpha().subsurface((32, 16, 16, 16))
        self.ground_img = pygame.transform.scale(self.ground_img, (self.tile_size, self.tile_size))

        # Completed entities
        self.platforms: list = []
        self.enemies: list = []
        self.exit: Exit = None

        # Enter new letter for each image in sprite sheet
        # Compared to assets/platforms directory.
        self.tilesheet = {
            "a": self.ground_img,
            "b": self.top_ground_img
        }

        with open(self.level_file_csv, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for i, row in enumerate(reader):
                for j, tile in enumerate(row):
                    self.level_data[i][j] = tile

        self.build_level()

    def build_level(self):
        """
        Calculates x and y position of platform from level data file.
        Processes data to calculate platform length and tile type.
        Creates all the platforms needed in the game of correct tile type and length.
        """

        for y, row in enumerate(self.level_data):
            platform_length = 1
            for x, tile in enumerate(row):
                # If the current tile is some sort of ground block
                if tile in self.tilesheet.keys():
                    if x + 1 < len(row):
                        # If the next tile is the same, extend length
                        if self.level_data[y][x] == self.level_data[y][x + 1]:
                            platform_length += 1
                        # Otherwise, create a platform of recorded length so far
                        else:
                            self.make_platform(tile, platform_length, x - (platform_length - 1), y, self.world)
                            platform_length = 1
                    # Otherwise, create platform here if no next tile exists
                    else:
                        self.make_platform(tile, platform_length, x - (platform_length - 1), y, self.world)

                # Otherwise, if the current tile is some sort of ground block
                elif tile == 'e':
                    self.enemies.append(BasicEnemy(
                        enemy_type='',
                        rect=pygame.Rect(x * self.tile_size, (len(self.level_data) - y) * self.tile_size, 48, 48),
                        world=self.world
                    ))

                elif tile == 'p':
                    self.exit = Exit(
                        rect=pygame.Rect(x * self.tile_size, (len(self.level_data) - y) * self.tile_size, 128, 128),
                        world=self.world
                    )

    def make_platform(self, tile_type: str, pl: int, x: int, y: int, world: pymunk.Space):
        """
        Creates a platform derived from the simple_platform class from the data
        generated in the level data file.

        NOTE: THIS VERSION WORKS AND I AM NOT FIXING IT IF IT BREAKS. - JARED

        :param tile_type: Tile string from tile sheet to display
        :param pl: Platform length to make rect hit box
        :param x: Position of platform along the x-axis
        :param y: Position of platform along the y-axis
        :param world: a pymunk Space to which platforms will be added
        """

        if tile_type in self.tilesheet:
            # Create new surface of correct dimensions
            new_surface = pygame.Surface((self.tilesheet[tile_type].get_width() * pl,
                                          self.tilesheet[tile_type].get_height()))
            # Create a sequence of images to display on new surface
            seq = [(self.tilesheet[tile_type], (self.tilesheet[tile_type].get_width() * offset, 0))
                   for offset in range(pl)]
            # Blit sequence to new surface
            new_surface.blits(blit_sequence=seq)

            # Compute rect of the platform in standard x/y grid (not pygame's inverted y-axis)
            rect = pygame.Rect(x * self.tilesheet[tile_type].get_width(),
                               self.tile_size * len(self.level_data) - y * self.tilesheet[tile_type].get_height(),
                               new_surface.get_width(),
                               new_surface.get_height())

            # Add new surface to platforms and create new platform with new surface image
            self.platforms.append(Platform(rect=rect, image=new_surface, world=world))
