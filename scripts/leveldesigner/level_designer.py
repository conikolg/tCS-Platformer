import pygame
import csv
from pathlib import Path


class LevelDesigner:
    def __init__(self, level: int = 1):
        self.level = level
        self.level_file = Path(f"scripts/leveldesigner/level{self.level}_data.csv")
        self.rows = 20
        self.cols = 78
        self.level_data = []
        self.create_empty_list()

        self.level_length = len(self.level_data[0])

    def create_empty_list(self):
        for row in range(self.rows):
            r = [-1] * self.cols
            self.level_data.append(r)

    def get_level_data(self):
        with open(self.level_file, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    self.level_data[x][y] = int(tile)

    def process_data(self):
        for y, row in enumerate(self.level_data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    # Get image and create rect
                    pass
