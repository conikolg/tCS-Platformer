import pygame

from scripts.util.custom_sprite import CustomSprite


class Bullet(CustomSprite):
    def __init__(self, location: tuple, direction: pygame.math.Vector2, damage: int):
        """
        Creates a bullet that spawns in a particular location and travels in a particular direction.

        :param location: A tuple containing the starting x and y coordinates of the center of the bullet.
        :param direction: A Vector2 indicating at what angle the bullet should travel.
        """

        super().__init__(hitbox_w_percent=80, hitbox_h_percent=30, hitbox_offset_x=10, hitbox_offset_y=35)
        self.speed: int = 10
        self.direction: pygame.math.Vector2 = direction.normalize()

        self._image: pygame.Surface = pygame.image.load("assets/bullet/bullet.png").convert_alpha()
        self._image = pygame.transform.scale(self._image, (100, 100))
        self.rect: pygame.rect.Rect = self.image.get_rect()
        self.rect.center = location
        self.damage = damage
        self.init_hitbox()

    def __str__(self):
        return f"Bullet located at {self.rect.topleft} with speed {self.speed} and {self.damage} damage"

    # should a bullet disappear going off-screen?
    # technically it still physically exists, allowing us to shoot off-screen enemies or obstacles...
    def update(self, right_bound, left_bound):
        self.rect.move_ip(self.speed * self.direction.x, self.speed * self.direction.y)
        if self.rect.right < left_bound or self.rect.left > right_bound:
            self.kill()

    @property
    def image(self):
        return pygame.transform.flip(self._image, self.direction.x == -1, False)
