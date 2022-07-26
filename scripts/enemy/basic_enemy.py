import pygame
from pathlib import Path
from collections import defaultdict

from scripts.util.custom_sprite import CustomSprite
from scripts.util.healthbar import Healthbar
from scripts.util.platform import Platform


class BasicEnemy(CustomSprite):
    def __init__(self, enemy_type: str, platform: Platform, horizontal_offset: int = 0):
        """
        Creates a basic enemy at a certain position that patrols on a platform.

        :param platform: the Platform on which this enemy will walk back and forth
        :param horizontal_offset: how far from the left edge of the platform the enemy will begin.
        """

        super().__init__()

        self.platform: Platform = platform
        # self._image: pygame.Surface = pygame.image.load(f"assets/enemy/basic_enemy.png")

        self.speed: float = 1.0
        self.direction: int = 1
        self.healthbar = Healthbar()

        self.update_time: int = 0
        self.enemy_type = enemy_type
        self.animations: dict[str, list] = self.load_animations(size=(50, 50))
        self.current_animation_frame = [self.enemy_type, 0]

        # This seems a little unnecessary but init first image in anim and scale
        # to get rect values before animation dict is generated and updated.
        self._image: pygame.Surface = pygame.image.load(f"assets/enemy/slime/slime 0.png").convert_alpha()
        self._image = pygame.transform.scale(self._image, (50, 50))

        self.rect: pygame.rect.Rect = self._image.get_rect()
        self.rect.bottom = self.platform.rect.top
        self.rect.left = self.platform.rect.left + horizontal_offset

        if self.rect.left < self.platform.rect.left or self.rect.right > self.platform.rect.right:
            raise Exception("Basic enemies cannot hang off platforms.")

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

        # Note from Nathan: As of 7/25/22 6:24 PM this was generating an error. Previously the line of code was: 
        # return pygame.transform.flip(self._image, flip_x=self.direction == 1, flip_y=False)
        # the error we were getting was: TypeError: flip() takes no keyword arguments
        # so after looking up a reference on pygame.transform.flip(), I just removed the positional arguments and it seems to work
        # (I know a lot of this would show up in the revision history but whatever)

        return pygame.transform.flip(self._image, self.direction == 1, False)

    def draw(self, surface: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = False):
        super(BasicEnemy, self).draw(surface, camera_offset, show_bounding_box)
        self.update_animation()
        surface.blit(source=self.healthbar.render(self.image.get_width(), 8, outline_width=2),
                     dest=self.rect.move(camera_offset).move(0, -8))

    def update_animation(self):
        animation_cooldown = 100
        self._image = self.animations[self.current_animation_frame[0]][self.current_animation_frame[1]]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.current_animation_frame[1] += 1

        if self.current_animation_frame[1] >= len(self.animations[self.current_animation_frame[0]]):
            self.current_animation_frame[1] = 0

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
