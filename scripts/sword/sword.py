import pygame


class Sword(pygame.sprite.Sprite):
    def __init__(self, location: tuple):
        """
        Creates a bullet that spawns in a particular location and travels in a particular direction.

        :param location: A tuple containing the starting x and y coordinates of the center of the bullet.
        :param direction: A Vector2 indicating at what angle the bullet should travel.
        """

        super().__init__()
        self.image: pygame.Surface = pygame.image.load("assets/sword/cyberSword.png").convert_alpha()
        # self.image = pygame.transform.scale(self.image, (100, 100))
        # self.image = pygame.transform.rotate(self.image, 90)
        self.rect: pygame.rect.Rect = self.image.get_rect()
        self.rect.center = location
        self.sword_swing = False
        self.sword_direction = 1
        # pygame.rect.Rect(100, 100, 10, 80)

    def draw(self, screen: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = False):
        if self.sword_swing:
            if camera_offset is None:
                camera_offset = pygame.math.Vector2(*self.rect.center)

            screen.blit(source=pygame.transform.flip(self.image, self.sword_direction, False),
                        dest=self.rect.move(camera_offset))

            if show_bounding_box:
                pygame.draw.rect(surface=screen, color=(255, 0, 0), rect=self.rect.move(camera_offset), width=1)
        else:
            if camera_offset is None:
                camera_offset = pygame.math.Vector2(*self.rect.center)

            # if show_bounding_box:
            # pygame.draw.rect(surface=screen, color=(255, 0, 0), rect=self.rect.move(camera_offset), width=1)
