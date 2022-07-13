from pathlib import Path

import pygame

from scripts.platform import Platform
from scripts.player.player import Player
from scripts.scenes.base_scene import BaseScene
from scripts.util.camera import Camera, BoundedFollowTarget
from scripts.util.custom_group import CustomGroup


class LevelOneScene(BaseScene):
    def __init__(self):
        super().__init__()

        # self.player = Player("player", 50, 650, 1, 10)
        self.player = Player("player", rect=pygame.rect.Rect(600, 550, 100, 100))

        # Length of level used in render method
        self.length = 5

        # Create the camera targeting the player
        self.camera = Camera(
            behavior=BoundedFollowTarget(target=self.player, horizontal_limits=(0, 6000), vertical_limits=(-100, 0)),
            # TODO: compensate for weirdness with bottom being cut-off on Macs
            constant=pygame.math.Vector2(-640 + self.player.rect.w / 2, -self.player.rect.top))

        # Store all layers in a dict with the delta scroll for each layer
        self.scenery: dict[pygame.Surface, float] = self.load_scenery(size=(self.camera.DISPLAY_W,
                                                                            self.camera.DISPLAY_H))

        # Create all active platforms in this level
        self.platforms: CustomGroup = CustomGroup()
        self.platforms.add(
            Platform(rect=pygame.rect.Rect(800, 600, 100, 10)),
            Platform(rect=pygame.rect.Rect(900, 550, 100, 10)),
            Platform(rect=pygame.rect.Rect(1000, 500, 100, 10)),
            Platform(rect=pygame.rect.Rect(1100, 450, 100, 10)),
        )

    def handle_events(self, events: list[pygame.event.Event]):
        """
        Allows the player to move up and down, to help test the camera system.

        :param events: a list of pygame events.
        :return: None
        """

        self.player.handle_events(events)

    def update(self):
        """
        Moves the player based on arrow keys or WASD keys pressed.
        """

        # Update player
        self.player.update()

        # Update bullets
        self.player.bullet_group.update(self.player.rect.x + self.camera.DISPLAY_W / 2,
                                        self.player.rect.x - self.camera.DISPLAY_W / 2)

    @staticmethod
    def load_scenery(size: tuple) -> dict[pygame.Surface, float]:
        # Create container for scenery
        scenery: dict[pygame.Surface, float] = dict()
        # Start at content root
        root_scenery_dir = Path("assets/scenery")

        # Delta scrolls for each layer
        ds = 0.5

        for layer in root_scenery_dir.iterdir():
            # Load the image
            img: pygame.Surface = pygame.image.load(layer).convert_alpha()
            # Scale it
            img = pygame.transform.scale(surface=img, size=size)
            # Create img layer key and assign ds value
            scenery[img] = round(ds, 1)
            # Increment by 0.1 for each layer
            ds += 0.1

        return scenery

    def render(self, screen: pygame.Surface):
        """
        Clears the screen, then draws a floating platform, the ground, and the player.

        The player should always be centered on the screen because of the camera. The other
        components of the level should appear relative to the player.

        :param screen: the Surface to render on to.
        :return: None
        """

        # White background
        screen.fill((255, 255, 255))

        # Move the camera
        self.camera.scroll()

        # Iterate through scenery dict and display
        for x in range(self.length):
            for layer, ds in self.scenery.items():
                # In order to account for vertical parallax, the layers have to be displayed at a negative offset
                # Calculate this offset by multiplying the delta scroll by the player height and subtract the
                # difference between the camera offset y times the delta scroll and the player height
                # TODO: start each layer in the negative x direction and bound camera from moving outside of level limit
                screen.blit(layer, ((x * self.camera.DISPLAY_W) - self.camera.offset.x * ds,
                                    (self.player.rect.h * ds) - self.camera.offset.y * ds - self.player.rect.h))

        # Draw game objects
        self.platforms.draw(surface=screen, camera_offset=-self.camera.offset)

        # Draw player and update sprite animation
        self.player.update_animation()
        self.player.draw(screen=screen, camera_offset=-self.camera.offset)

        if self.player.bullet_group:
            for bullet in self.player.bullet_group:
                bullet.draw(screen, camera_offset=-self.camera.offset)
