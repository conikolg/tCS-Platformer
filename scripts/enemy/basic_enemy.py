import random
from collections import defaultdict
from datetime import timedelta
from pathlib import Path

import pygame
import pymunk

from scripts import body, collision_types
from scripts.ui.healthbar import Healthbar
from scripts.util import game_time


class BasicEnemy:
    def __init__(self, enemy_type: str, rect: pygame.rect.Rect, world: pymunk.Space):
        """
        Creates a basic enemy at a certain position that patrols on a platform.

        :param enemy_type: denotes what image/animations to use for this enemy.
        :param rect: denotes the location and size of the enemy
        :param world: the greater pymunk simulation space
        """

        # Save the world. Needed for spawning bullets
        self.world: pymunk.Space = world

        # Enemy visuals
        enemy_types = ["frog", "slime", "scorpion"]
        self.enemy_type = enemy_type if enemy_type in enemy_types else random.choice(enemy_types)
        self.animations: dict[str, list] = self.load_animations(size=(rect.w, rect.h))
        self.current_animation_frame = [self.enemy_type, 0]

        # Create physics body with (infinite moment of inertia to disable rotation)
        self.body = body.Body(mass=10, moment=float("inf"), body_type=pymunk.Body.DYNAMIC, obj=self)
        self.body.position = rect.center

        # Create physics shape/hitbox
        self.shape = pymunk.Poly.create_box(body=self.body, size=(rect.w, rect.h), radius=1)
        self.shape.collision_type = collision_types.ENEMY
        self.shape.elasticity = 0.1
        self.shape.friction = 0.9
        world.add(self.body, self.shape)

        # Enemy attributes
        self.speed: float = 50.0
        self.direction = pymunk.Vec2d(-1, 0)
        self.healthbar = Healthbar()
        self._is_grounded: bool = True
        self._can_turn: bool = True
        self._can_turn_timeout: float = timedelta(milliseconds=100).total_seconds()

    def __str__(self):
        health_percent = round(self.healthbar.health / self.healthbar.maximum_health * 100, 2)
        return f"BasicEnemy({self.body.position=}, {self.body.velocity=}, " \
               f"health={self.healthbar.health}/{self.healthbar.maximum_health} ({health_percent}%))"

    def update(self) -> None:
        def check_if_grounded(arbiter: pymunk.Arbiter):
            if arbiter.normal.y == -1:
                self._is_grounded = True

        # Check if the enemy is grounded
        self._is_grounded = False
        self.body.each_arbiter(check_if_grounded)

        # Move forward if the enemy is grounded on something
        self.shape.surface_velocity = (0, 0)
        if self._is_grounded:
            # Move to the right
            if self.direction.x > 0:
                self.shape.surface_velocity -= (self.speed, 0)
            # Move to the left
            else:
                self.shape.surface_velocity += (self.speed, 0)

        def turn_if_at_edge(arbiter: pymunk.Arbiter):
            points: list[pymunk.Vec2d] = self.shape.get_vertices()
            min_y = min([p.y for p in points])
            bottom_points: list[pymunk.Vec2d] = sorted([p + self.body.position for p in points if p.y == min_y],
                                                       key=lambda p: p.x)
            contact_points: list[pymunk.Vec2d] = sorted([p.point_b for p in arbiter.contact_point_set.points],
                                                        key=lambda p: p.x)

            # If any contact points are more than 1 unit away from own ground vertices, assume enemy is at an edge
            at_edge = False
            for p1 in bottom_points:
                p2 = min(contact_points, key=lambda p: p1.get_dist_sqrd(p))
                if p1.get_dist_sqrd(p2) > 1:
                    at_edge = True
                    break

            if at_edge:
                # Turn and disable turning for some time
                self.direction *= -1
                self.body.velocity = (0, 0)
                self._can_turn = False

                def enable_turn():
                    self._can_turn = True

                game_time.schedule(enable_turn, self._can_turn_timeout)

        # Turn around if reached the edge of current platform
        if self._can_turn:
            self.body.each_arbiter(turn_if_at_edge)

    @property
    def image(self):
        image: pygame.Surface = self.animations[self.current_animation_frame[0]][self.current_animation_frame[1]]
        return pygame.transform.flip(image, self.direction.x < 0, False)

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

    @staticmethod
    def load_animations(size: tuple) -> dict[str, list]:
        # Create container for animations
        animations: dict[str, list] = defaultdict(lambda: list())
        # Start at content root for this enemy type
        root_animations_dir = Path(f"assets/enemy")

        # Iterate through animation types
        for enemy_type_dir in root_animations_dir.iterdir():
            # Iterate through contents of animation type folder
            for frame in enemy_type_dir.iterdir():
                # Load the frame
                img: pygame.Surface = pygame.image.load(frame).convert_alpha()
                # Scale it
                img = pygame.transform.scale(img, size)
                # Add it to big animation dictionary
                animations[enemy_type_dir.name].append(img)

        return animations
