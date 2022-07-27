from collections import defaultdict
from pathlib import Path

import pygame

from scripts.util.custom_sprite import CustomSprite
from scripts.util.healthbar import Healthbar
from scripts.util.platform import Platform


class BasicEnemy(CustomSprite):
    def __init__(self, enemy_type: str, platform: Platform, horizontal_offset: int = 0, 
         hitbox_w_percent: int = 100, hitbox_h_percent: int = 100, hitbox_offset_x: int = 0, hitbox_offset_y: int = 0):
        """
        Creates a basic enemy at a certain position that patrols on a platform.

        :param platform: the Platform on which this enemy will walk back and forth
        :param horizontal_offset: how far from the left edge of the platform the enemy will begin.
        """

        super().__init__(hitbox_w_percent, hitbox_h_percent, hitbox_offset_x, hitbox_offset_y)

        self.platform: Platform = platform
        # self._image: pygame.Surface = pygame.image.load(f"assets/enemy/basic_enemy.png")

        self.speed: float = 1.0
        self.direction: int = 1
        self.healthbar = Healthbar()
        self.horizontal_offset = horizontal_offset
        self.update_time: int = 0
        self.enemy_type = enemy_type
        self.animations: dict[str, list] = self.load_animations(size=(50, 50))
        self.current_animation_frame = [self.enemy_type, 0]

        # This seems a little unnecessary but init first image in anim and scale
        # to get rect values before animation dict is generated and updated.
        self._image: pygame.Surface = pygame.image.load(f"assets/enemy/slime/slime 0.png").convert_alpha()
        self._image = pygame.transform.scale(self._image, (50, 50))

        # enemy hitbox defaults to rect that would naturally encompass image file
        self.rect: pygame.rect.Rect = self._image.get_rect()
        self.init_hitbox()

        # ensure that all of the enemy is on the platform
        if self.rect.left < self.platform.rect.left or self.rect.right > self.platform.rect.right:
            raise Exception("Basic enemies cannot hang off platforms.")
        
    def __str__(self):
        out_str = f"BasicEnemy located at {self.rect.topleft}"
        health_percent = round(self.healthbar.health / self.healthbar.maximum_health * 100, 2)
        out_str += f" with {self.healthbar.health}/{self.healthbar.maximum_health} ({health_percent}%) HP"
        return out_str

    def update(self) -> None:
        # Try going right
        if self.direction == -1:
            # Is there room on this platform to move?
            if self.rect.right < self.platform.rect.right:
                # Move forward
                self.rect.right += self.speed
                self.rect.right = min(self.rect.right, self.platform.rect.right)
            else:
                # Turn around
                self.direction = 1

        # Try going left
        else:
            # Is there room on this platform to move?
            if self.rect.left > self.platform.rect.left:
                # Move forward
                self.rect.left -= self.speed
                self.rect.left = max(self.rect.left, self.platform.rect.left)
            else:
                # Turn around
                self.direction = -1

    @property
    def image(self):
        return pygame.transform.flip(self._image, self.direction == 1, False)

    def draw(self, screen: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = False):
        super(BasicEnemy, self).draw(screen, camera_offset, show_bounding_box)
        screen.blit(source=self.healthbar.render(self.image.get_width(), 8, outline_width=2),
                     dest=self.rect.move(camera_offset).move(0, -8).move(-self.hitbox_offset_x, -self.hitbox_offset_y))

    @staticmethod
    def load_animations(size: tuple) -> dict[str, list]:
        # Create container for animations
        animations: dict[str, list] = defaultdict(lambda: list())
        # Start at content root for this enemy type
        root_animations_dir = Path(f"assets/enemy")

        # Iterate through animation types
        for enemy_type_dir in root_animations_dir.iterdir():
            # Iterate through contents of animation type folder
            for frame in enemy_type_dir.iterdir():
                # Load the frame
                img: pygame.Surface = pygame.image.load(frame).convert_alpha()
                # Scale it
                img = pygame.transform.scale(img, size)
                # Add it to big animation dictionary
                animations[enemy_type_dir.name].append(img)

        return animations

    def init_hitbox(self):
        self.rect.bottom = self.platform.rect.top
        self.rect.left = self.platform.rect.left + self.horizontal_offset
        super().init_hitbox()