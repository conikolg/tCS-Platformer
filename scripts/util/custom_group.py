import pygame

from scripts.util.custom_sprite import CustomSprite


class CustomGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def sprites(self) -> list[CustomSprite]:
        return super().sprites()

    def add(self, *sprites) -> None:
        for sprite in sprites:
            if isinstance(sprite, CustomSprite):
                super().add(sprite)
            else:
                raise Exception(f"sprite {sprite} must be an instance of {CustomSprite}")

    def draw(self, surface: pygame.Surface,
             camera_offset: pygame.math.Vector2 = None,
             show_bounding_box: bool = False) -> list[pygame.rect.Rect]:
        for sprite in self.sprites():
            sprite.draw(surface, camera_offset, show_bounding_box)

        # TODO: actually calculate the rectangle that was changed
        return [sprite.rect for sprite in self.sprites()]
