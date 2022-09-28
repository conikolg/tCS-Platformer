import pygame
import pymunk

from scripts import body, collision_types
from scripts.util.image_utils import auto_crop


class Bullet:
    def __init__(self, location: pymunk.Vec2d, direction: pymunk.Vec2d, damage: int, world: pymunk.Space):
        """
        Creates a bullet that spawns in a particular location and travels in a particular direction.

        :param location: A tuple containing the starting x and y coordinates of the center of the bullet.
        :param direction: A Vector2 indicating at what angle the bullet should travel.
        """

        super().__init__()

        # Save the world. Needed for spawning bullets
        self.world: pymunk.Space = world

        # Create physics body for platform and position it
        self.body = body.Body(body_type=pymunk.Body.KINEMATIC, obj=self)
        self.body.position = location

        # Create physics shape/hitbox
        self.shape = pymunk.Poly.create_box(body=self.body, size=(100, 50), radius=1)
        self.shape.collision_type = collision_types.BULLET

        # Graphics assets
        self._image: pygame.Surface = pygame.image.load("assets/bullet/bullet.png").convert_alpha()
        # Automatically crop and scale them to just the occupied pixel portion
        self._image: pygame.Surface = auto_crop(images=[self._image], size=(100, 50))[0]

        # Behavioral attributes
        self.body.velocity = tuple(direction.normalized() * 1250)

        # Damage
        self.damage = damage

        # Add to world
        self.world.add(self.body, self.shape)

    def __str__(self):
        return f"Bullet({self.body.position=}, {self.body.velocity=}, {self.damage=})"

    # should a bullet disappear going off-screen?
    # technically it still physically exists, allowing us to shoot off-screen enemies or obstacles...
    def update(self, right_bound, left_bound):
        if not (left_bound <= self.body.position.x <= right_bound):
            self.world.remove(self.body, self.shape)

    @property
    def image(self):
        return pygame.transform.flip(self._image, self.body.velocity.x < 0, False)

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
