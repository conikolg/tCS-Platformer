import pygame


class Sword:
    def __init__(self, location: tuple):
        """
        Creates a bullet that spawns in a particular location and travels in a particular direction.

        :param location: A tuple containing the starting x and y coordinates of the center of the bullet.
        """

        super().__init__()
        self._image: pygame.Surface = pygame.image.load("assets/sword/cyberSword.png").convert_alpha()
        # self.image = pygame.transform.scale(self.image, (100, 100))
        # self.image = pygame.transform.rotate(self.image, 90)
        self.rect: pygame.rect.Rect = self._image.get_rect()
        self.rect.center = location
        self.sword_swing = False
        self.sword_direction = 1

    @property
    def image(self):
        return pygame.transform.flip(self._image, self.sword_direction == 1, False)

    def draw(self, screen: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = False):
        if not self.sword_swing:
            return

        super(Sword, self).draw(screen, camera_offset, show_bounding_box)
