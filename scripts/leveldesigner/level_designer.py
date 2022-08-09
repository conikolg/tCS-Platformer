import pygame
import csv
from pathlib import Path
import pandas as pd
from scripts.util.simple_platform import Platform


class LevelDesigner:
    def __init__(self, level: int = 1):
        # Collects data from csv files to display objects and obstacles in the level.

        # :param level: Current level csv file to display.
        self.level = level
        self.level_file = Path(f"scripts/leveldesigner/level{self.level}_data.csv")
        self.rows: int = len(pd.read_csv(self.level_file).axes[0]) + 1
        self.cols: int = len(pd.read_csv(self.level_file).axes[1])
        self.level_data = []
        self.create_empty_list()
        self.platform_img = pygame.image.load("assets/platforms/purple_platform.png")
        self.platforms = []

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
                    self.platforms.append(Platform(rect=pygame.Rect(x*64,
                                                                    y*32+150,
                                                                    64,
                                                                    32),
                                                   image=self.platform_img))
