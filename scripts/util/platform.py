import pygame

from scripts.util.custom_sprite import CustomSprite


class Platform(CustomSprite):
    def __init__(self, rect: pygame.rect.Rect, image: pygame.Surface = None):
        """
        Creates a platform occupying the world at the given rectangle and looks like the image given when rendered.

        :param rect: a Rect that specifies where in the world this platform is.
        :param image: a Surface that the platform will look like. If None, a solid black square is used.
        """

        super().__init__()

        self.rect: pygame.rect.Rect = rect
        self.image: pygame.Surface = image

        if self.image is None:
            self.image = pygame.Surface(size=(10, 10))
        if self.image.get_size() != self.rect.size:
            self.image = pygame.transform.scale(self.image, rect.size)