import pygame
import pymunk

from scripts import body, collision_types


class Exit:
    def __init__(self, rect: pygame.rect.Rect, world: pymunk.Space,
                 image: pygame.Surface = pygame.image.load('assets/portal.png')):
        """
        Creates a platform occupying the world at the given rectangle and looks like the image given when rendered.

        :param rect: a Rect that specifies where in the world this platform is.
        :param world: a pymunk Space to which this platform will be added
        :param image: a Surface that the platform will look like. If None, a solid black square is used.
        """

        super().__init__()

        # Create physics body for platform and position it
        self.body = body.Body(body_type=pymunk.Body.STATIC, obj=self)
        self.body.position = rect.center

        # Create physics shape/hitbox
        self.shape = pymunk.Poly.create_box(body=self.body, size=(rect.w, rect.h), radius=1)
        self.shape.collision_type = collision_types.EXIT
        self.shape.elasticity = 0
        self.shape.friction = 0

        # Save image for this platform
        self.image: pygame.Surface = image
        if self.image is None:
            self.image = pygame.Surface(size=(10, 10))
        if self.image.get_size() != rect.size:
            self.image = pygame.transform.scale(self.image, rect.size)

        # Add platform into the world
        world.add(self.body, self.shape)

    def __str__(self):
        return f"Exit({self.body.position=}, {self.shape.bb=})"

    def draw(self, screen: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = False):
        # Update hitbox based on camera offset
        if camera_offset is None:
            camera_offset = pygame.math.Vector2(0, 0)

        # Adjust for pygame screen and camera location
        on_screen_destination = self.image.get_rect()
        on_screen_destination.center = (self.body.position.x, screen.get_height() - self.body.position.y)
        on_screen_destination.move_ip(camera_offset)

        # Draw image
        screen.blit(self.image, dest=on_screen_destination)

        # Draw hitbox
        if show_bounding_box:
            pygame.draw.rect(surface=screen, color=(255, 0, 0), rect=on_screen_destination, width=1)
