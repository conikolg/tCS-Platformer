import pygame

from scripts.util.custom_sprite import CustomSprite
from scripts.util.healthbar import Healthbar
from scripts.util.platform import Platform


class BasicEnemy(CustomSprite):
    def __init__(self, platform: Platform, horizontal_offset: int = 0):
        """
        Creates a basic enemy at a certain position that patrols on a platform.

        :param platform: the Platform on which this enemy will walk back and forth
        :param horizontal_offset: how far from the left edge of the platform the enemy will begin.
        """

        super().__init__()

        self.platform: Platform = platform
        self._image: pygame.Surface = pygame.image.load(f"assets/enemy/basic_enemy.png")
        self.rect: pygame.rect.Rect = self._image.get_rect()
        self.rect.bottom = self.platform.rect.top
        self.rect.left = self.platform.rect.left + horizontal_offset

        if self.rect.left < self.platform.rect.left or self.rect.right > self.platform.rect.right:
            raise Exception("Basic enemies cannot hang off platforms.")

        self.speed: float = 1.0
        self.direction: int = 1
        self.healthbar = Healthbar()

    def update(self) -> None:
        # Try going right
        if self.direction == 1:
            # Is there room on this platform to move?
            if self.rect.right < self.platform.rect.right:
                # Move forward
                self.rect.right += self.speed
                self.rect.right = min(self.rect.right, self.platform.rect.right)
            else:
                # Turn around
                self.direction = -1

        # Try going left
        else:
            # Is there room on this platform to move?
            if self.rect.left > self.platform.rect.left:
                # Move forward
                self.rect.left -= self.speed
                self.rect.left = max(self.rect.left, self.platform.rect.left)
            else:
                # Turn around
                self.direction = 1

    @property
    def image(self):
        return pygame.transform.flip(self._image, flip_x=self.direction == 1, flip_y=False)

    def draw(self, surface: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = False):
        super(BasicEnemy, self).draw(surface, camera_offset, show_bounding_box)

        surface.blit(source=self.healthbar.render(self.image.get_width(), 8, outline_width=2),
                     dest=self.rect.move(camera_offset).move(0, -8))
