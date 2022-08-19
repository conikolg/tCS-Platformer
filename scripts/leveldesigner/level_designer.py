import csv
from pathlib import Path

import pandas as pd
import pygame

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
        self.top_ground_img: pygame.Surface = pygame.image.load(Path("assets/platforms/Textures-16.png")).convert_alpha().subsurface((32, 0, 16, 16))
        self.ground_img: pygame.surface = pygame.image.load(Path("assets/platforms/Textures-16.png")).convert_alpha().subsurface((32, 16, 16, 16))
        self.platforms: list = []
        self.enemies: list = []

    def create_empty_list(self):
        # Creates an "empty" list full of -1 values which will not display an object.
        for row in range(self.rows):
            r = [-1] * self.cols
            self.level_data.append(r)

    def get_level_data(self):
        # Pulls data from csv level file to find x and y position of each element in csv mapped to game.
        with open(self.level_file, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    self.level_data[x][y] = int(tile)

    def process_data(self):
        # Displays data from csv level file onto the game screen.
        for y, row in enumerate(self.level_data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    # Get image and create rect
                    # TODO: Add multiple conditions for each piece of data to display.
                    # -1: None
                    # 0: Platform
                    # 1: Enemy
                    # etc.
                    if tile == 0:
                        self.platforms.append(
                            Platform(rect=pygame.Rect(x * 32, y * 32, 32, 32), image=self.ground_img))
                    elif tile == 1:
                        self.platforms.append(
                            Platform(rect=pygame.Rect(x * 32, y * 32, 32, 32), image=self.top_ground_img))
                    elif tile == 2:
                        self.platforms.append(
                            Platform(rect=pygame.Rect(x * 32, y * 32, 32*5, 32), image=self.ground_img))
                    elif tile == 3:
                        print(len(self.platforms))
                        self.enemies.append(
                            BasicEnemy("frog", self.platforms[8]))
