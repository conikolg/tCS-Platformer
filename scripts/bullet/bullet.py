import pygame


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed: int = 10
        self.image = pygame.image.load("assets/bullet/bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed)
        # TODO: replace right and left bounds for camera
        if self.rect.right < 0 or self.rect.left > 640:
            self.kill()
