import pygame

from scenes.base_scene import BaseScene


class SampleScene(BaseScene):
    def __init__(self):
        super().__init__()

        # Declare any state information for the scene here
        self.player_hitbox: pygame.rect.Rect = None
        self.player_directional_speed = 7

        # Perform any one-off operations here
        self.reset()

    def reset(self):
        """
        Puts the player in the starting location.

        Custom function specific to this scene.
        :return: None
        """

        self.player_hitbox = pygame.rect.Rect(50, 50, 50, 50)

    def handle_events(self, events: list[pygame.event.Event]):
        """
        Returns the player to the starting location every time the space bar is pressed.
        """

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.reset()

    def update(self):
        """
        Moves the player based on arrow keys or WASD keys pressed.
        """

        # Get current keyboard state
        keys = pygame.key.get_pressed()

        # Move player (standard coordinate plane)
        dx, dy = 0, 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy += self.player_directional_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy -= self.player_directional_speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.player_directional_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.player_directional_speed

        # Apply standard coordinate plane deltas to pygame coordinate plane
        self.player_hitbox.move_ip(dx, -dy)

    def render(self, screen: pygame.Surface):
        """
        Draws the player character on a white background.
        """

        # White background
        screen.fill((255, 255, 255))

        # Draw player as a box with a few colors
        pygame.draw.rect(
            surface=screen, color=(59, 137, 255),  # Blue top-left quarter box
            rect=(self.player_hitbox.left, self.player_hitbox.top,
                  self.player_hitbox.width / 2, self.player_hitbox.height / 2))
        pygame.draw.rect(
            surface=screen, color=(33, 255, 118),  # Green top-right quarter box
            rect=(self.player_hitbox.centerx, self.player_hitbox.top,
                  self.player_hitbox.width / 2, self.player_hitbox.height / 2))
        pygame.draw.rect(
            surface=screen, color=(240, 118, 48),  # Orange bottom half box
            rect=(self.player_hitbox.left, self.player_hitbox.centery,
                  self.player_hitbox.width, self.player_hitbox.height / 2))
