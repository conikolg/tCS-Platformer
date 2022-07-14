import os, platform

import pygame
from pathlib import Path

# from scripts.player.sample_player import Player
from scripts.player.player import Player
from scripts.scenes.base_scene import BaseScene
from scripts.util.camera import Camera, BoundedFollowTarget


class LevelOneScene(BaseScene):
    def __init__(self):
        super().__init__()

        # self.player = Player("player", 50, 650, 1, 10)
        self.player = Player("player", rect=pygame.rect.Rect(600, 550, 100, 100))
        self.platform = pygame.rect.Rect(-300, 200, 600, 50)
        self.ground = pygame.rect.Rect(-1000, 700, 2000, 50)

        # Length of level used in render method
        self.length = 5

        self.camera = Camera(behavior=BoundedFollowTarget(target=self.player,
                                                          horizontal_limits=(0, 6000),
                                                          vertical_limits=(-100, 0)),
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
            Platform(rect=pygame.rect.Rect(1175, 500, 100, 10)),
            Platform(rect=pygame.rect.Rect(1400, 575, 100, 10)),
            Platform(rect=pygame.rect.Rect(1525, 575, 100, 10)),

            Platform(rect=pygame.rect.Rect(1650, 200, 100, 10)),
            Platform(rect=pygame.rect.Rect(1750, 200, 100, 10)),
            Platform(rect=pygame.rect.Rect(1850, 200, 100, 10)),
            Platform(rect=pygame.rect.Rect(1950, 200, 100, 10)),
            Platform(rect=pygame.rect.Rect(2050, 200, 100, 10)),


            Platform(rect=pygame.rect.Rect(1650, 80, 100, 10)),
            Platform(rect=pygame.rect.Rect(1750, 80, 100, 10)),  
            Platform(rect=pygame.rect.Rect(1850, 80, 100, 10)), 
            Platform(rect=pygame.rect.Rect(1950, 80, 100, 10)),
            Platform(rect=pygame.rect.Rect(2050, 80, 100, 10)),

            Platform()

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

    def load_scenery(self, size: tuple) -> dict[pygame.Surface, float]:
        # Create container for scenery
        scenery: dict[pygame.Surface, float] = dict()
        # Start at content root
        # Sort path for MacOS to read clearly
        root_scenery_dir = sorted(Path("assets/scenery").iterdir())

        # Delta scrolls for each layer
        ds = 0.5

        for layer in root_scenery_dir:
            # Load the image
            img: pygame.Surface = pygame.image.load(layer).convert_alpha()
            # Scale it
            img = pygame.transform.scale(img, size)
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

        # Iterate through scenery dict and display
        for x in range(self.length):
            for layer, ds in self.scenery.items():
                # In order to account for vertical parallax, the layers have to be displayed at a negative offset
                # Calculate this offset by multiplying the delta scroll by the player height and subtract the
                # difference between the camera offset y times the delta scroll and the player height
                screen.blit(layer, ((x * self.camera.DISPLAY_W) - self.camera.offset.x * ds,
                                    (self.player.rect.h * ds) - self.camera.offset.y * ds - self.player.rect.h))

        # Move the camera
        self.camera.scroll()

        # Draw static objects
        # pygame.draw.rect(screen, (0, 0, 0), self.platform.move(*-self.camera.offset))
        # pygame.draw.rect(screen, (0, 0, 0), self.ground.move(*-self.camera.offset))

        # Draw player and update sprite animation
        self.player.update_animation()
        self.player.draw(screen=screen, camera_offset=-self.camera.offset)

        if self.player.bullet_group:
            for bullet in self.player.bullet_group:
                bullet.draw(screen, camera_offset=-self.camera.offset)
