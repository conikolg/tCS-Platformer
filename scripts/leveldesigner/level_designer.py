import csv
from pathlib import Path

import pandas as pd
import pygame

from itertools import groupby

from scripts.scenes.simple_platform import Platform
from scripts.enemy.basic_enemy import BasicEnemy


class LevelDesigner:
    def __init__(self, level: int = 1):
        # Collects data from csv files to display objects and obstacles in the level.

        # :param level: Current level csv file to display.
        self.level = level
        self.level_file = Path(f"scripts/leveldesigner/level{self.level}_data.csv")
        self.rows: int = len(pd.read_csv(self.level_file).axes[0]) + 1
        self.cols: int = len(pd.read_csv(self.level_file).axes[1])
        self.level_data: list = []
        self.create_empty_list()
        self.top_ground_img: pygame.Surface = pygame.image.load(
            Path("assets/platforms/Textures-16.png")).convert_alpha().subsurface((32, 0, 16, 16))
        self.ground_img: pygame.surface = pygame.image.load(
            Path("assets/platforms/Textures-16.png")).convert_alpha().subsurface((32, 16, 16, 16))
        self.platforms: list = []
        self.enemies: list = []

        # Enter new letter for each image in sprite sheet
        # Compared to assets/platforms directory.
        self.tilesheet = {
            "a": self.ground_img,
            "b": self.top_ground_img
        }

    def create_empty_list(self):
        """Creates an "empty" list full of -1 values which will not display an object."""
        for row in range(self.rows):
            r = [-1] * self.cols
            self.level_data.append(r)

    def get_level_data(self):
        """Pulls data from csv level file to find x and y position of each element in csv mapped to game."""
        with open(self.level_file, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    self.level_data[x][y] = tile

    @staticmethod
    def process_data(data):
        """
        Counts consecutive same tile values and returns tile and length of each set.
        """
        tile = []
        length = []
        running_count = 1
        for row in range(len(data)):
            for val in range(len(data[row]) - 1):
                if data[row][val] != "-1z":
                    if data[row][val] == data[row][val + 1]:
                        running_count += 1
                    else:
                        length.append(running_count)
                        tile.append(data[row][val])
                        running_count = 1

        if data[row][val] != "-1z":
            tile.append(data[row][val + 1])
            length.append(running_count)

        res = {tile[i]: length[i] for i in range(len(tile))}

        return res

    def generate_platforms(self):
        """
        Calculates x and y position of platform from level data file.
        Processes data to calculate platform length and tile type.
        Creates all of the platforms needed in the game of correct tile type and length.
        """
        tiles_and_lengths = self.process_data(self.level_data)
        tiles = self.process_data(self.level_data).keys()
        lengths = self.process_data(self.level_data).values()

        for x, row in enumerate(self.level_data):
            for y, tile in enumerate(row):
                if tile[-1] in self.tilesheet.keys():
                    self.make_platform(self.level_data[x][y][-1], tiles_and_lengths[tile], y, x)
                    break

    def make_platform(self, tile_type: str, pl: int,
                      x: int, y: int):
        """
        Creates a platform derived from the simple_platform class from the data
        generated in the level data file.

        :param tile_type: Tile string from tile sheet to display
        :param pl: Platform length to make rect hit box
        :param x: Position of platform along the x axis
        :param y: Position of platform along the y axis
        """
        if tile_type in self.tilesheet:
            # Create new surface that is count times bigger than image width
            new_surface = pygame.Surface((self.tilesheet[tile_type].get_width() * pl,
                                          self.tilesheet[tile_type].get_height()),
                                         pygame.SRCALPHA)

            # Iterate for each count of tile to blit image at new X destination
            for offset in range(pl):
                new_surface.blit(self.tilesheet[tile_type],
                                 dest=(self.tilesheet[tile_type].get_width() * offset, 0))

            # Add new surface to platforms and create new platform with new surface image
            self.platforms.append(Platform(rect=pygame.Rect(x * 64,
                                                            y * 64 - 540,
                                                            new_surface.get_width() * 4,
                                                            new_surface.get_height() * 4),
                                           image=new_surface))

    def spawn_enemy(self, enemy_type: str, platform: Platform):
        self.enemies.append(BasicEnemy(enemy_type, platform))
