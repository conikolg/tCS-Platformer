import pygame

from scripts.player.sample_player import Player
from scripts.scenes.base_scene import BaseScene


class SampleScene(BaseScene):
    def __init__(self):
        super().__init__()

        self.player = Player("player", 100, 100, 1, 6)

    def handle_events(self, events: list[pygame.event.Event]):
        pass

    def update(self):
        """
        Moves the player based on arrow keys or WASD keys pressed.
        """

        # Get current keyboard state
        keys = pygame.key.get_pressed()

        # Set player movement boolean to key conditional
        self.player.moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        self.player.moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        self.player.jump = keys[pygame.K_w] or keys[pygame.K_SPACE] and self.player.alive

        # Move player
        if self.player.alive:
            if self.player.moving_left or self.player.moving_right:
                self.player.update_action(1)  # 1: run
            else:
                self.player.update_action(0)  # 0: idle
            self.player.move(self.player.moving_left, self.player.moving_right)

    def render(self, screen: pygame.Surface):
        """
        Draws the player character on a white background.
        """

        # White background
        screen.fill((255, 255, 255))

        # Draw player and update sprite animation
        self.player.update_animation()
        self.player.draw(screen)
