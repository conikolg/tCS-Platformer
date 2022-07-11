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

    def update(self, right_bound, left_bound):
        self.rect.x += self.speed * self.direction
        if self.rect.right < left_bound or self.rect.left > right_bound:
            self.kill()

    def draw(self, screen: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = True):
        if camera_offset is None:
            camera_offset = pygame.math.Vector2(*self.rect.center)

        screen.blit(source=pygame.transform.flip(self.image, self.direction == -1, False),
                    dest=self.rect.move(camera_offset))

        if show_bounding_box:
            pygame.draw.rect(surface=screen, color=(255, 0, 0), rect=self.rect.move(camera_offset), width=1)
