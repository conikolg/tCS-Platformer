import pygame


class CustomSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.visible = True

    def draw(self, surface: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = False):
        if camera_offset is None:
            camera_offset = pygame.math.Vector2(0, 0)

        if self.visible:
            surface.blit(self.image, dest=self.rect.move(camera_offset))
            if show_bounding_box:
                pygame.draw.rect(surface=surface, color=(255, 0, 0), rect=self.rect.move(camera_offset), width=1)
