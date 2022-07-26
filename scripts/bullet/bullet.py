import pygame


# NOTE: Bullet is inheriting from pygame.sprite.Sprite whereas some other classes inherit from CustomSprite
# which should it be?
class Bullet(pygame.sprite.Sprite):
    def __init__(self, location: tuple, direction: pygame.math.Vector2, damage: int):
        """
        Creates a bullet that spawns in a particular location and travels in a particular direction.

        :param location: A tuple containing the starting x and y coordinates of the center of the bullet.
        :param direction: A Vector2 indicating at what angle the bullet should travel.
        """

        super().__init__()
        self.speed: int = 10
        self.direction: pygame.math.Vector2 = direction.normalize()

        self.image: pygame.Surface = pygame.image.load("assets/bullet/bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect: pygame.rect.Rect = self.image.get_rect()
        self.rect.center = location
        self.damage = damage

    def __str__(self):
        return f"Bullet located at {self.rect.topleft} with speed {self.speed} and {self.damage} damage"

    # should a bullet disappear going off screen?
    # technically it still physically exists, allowing us to shoot offscreen enemies or obstacles...
    def update(self, right_bound, left_bound):
        self.rect.move_ip(self.speed * self.direction.x, self.speed * self.direction.y)
        if self.rect.right < left_bound or self.rect.left > right_bound:
            self.kill()

    def draw(self, screen: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = False):
        if camera_offset is None:
            camera_offset = pygame.math.Vector2(*self.rect.center)

        screen.blit(source=pygame.transform.flip(self.image, self.direction.x < 0, False),
                    dest=self.rect.move(camera_offset))

        if show_bounding_box:
            pygame.draw.rect(surface=screen, color=(255, 0, 0), rect=self.rect.move(camera_offset), width=1)
