import pygame

from scripts.player.sample_player import Player
from scripts.scenes.base_scene import BaseScene
from scripts.util.camera import Camera, FollowTarget


class LevelOneScene(BaseScene):
    def __init__(self):
        super().__init__()

        self.player = Player("player", 50, 650, 1, 10)
        self.platform = pygame.rect.Rect(-300, 200, 600, 50)
        self.ground = pygame.rect.Rect(-1000, 700, 2000, 50)

        self.camera = Camera(behavior=FollowTarget(target=self.player),
                             constant=pygame.math.Vector2(-640 + self.player.rect.w / 2, -self.player.rect.top))

        self.bg_scroll = 0
        self.sky_img = pygame.image.load("assets/scenery/5.png").convert_alpha()
        self.sky_img = pygame.transform.scale(self.sky_img, (1280, 720))
        self.planets_img = pygame.image.load("assets/scenery/4.png").convert_alpha()
        self.planets_img = pygame.transform.scale(self.planets_img, (1280, 720))
        self.mountain_img = pygame.image.load("assets/scenery/3.png").convert_alpha()
        self.mountain_img = pygame.transform.scale(self.mountain_img, (1280, 720))
        self.hills_img = pygame.image.load("assets/scenery/2.png").convert_alpha()
        self.hills_img = pygame.transform.scale(self.hills_img, (1280, 720))

    def handle_events(self, events: list[pygame.event.Event]):
        """
        Allows the player to move up and down, to help test the camera system.

        :param events: a list of pygame events.
        :return: None
        """

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player.rect.move_ip(0, -10)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.player.rect.move_ip(0, 10)

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
            if self.player.in_air:
                self.player.update_action(2)  # 2: jump
            elif self.player.moving_left or self.player.moving_right:
                self.player.update_action(1)  # 1: run
            else:
                self.player.update_action(0)  # 0: idle
            self.player.move(self.player.moving_left, self.player.moving_right)

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

        width = self.sky_img.get_width()
        w, h = screen.get_size()
        for x in range(5):
            screen.blit(self.sky_img, ((x * width) - self.bg_scroll * 0.5, 0))
            screen.blit(self.planets_img, ((x * width) - self.bg_scroll * 0.6, 0))
            screen.blit(self.mountain_img, ((x * width) - self.bg_scroll * 0.7, 0))
            screen.blit(self.hills_img, ((x * width) - self.bg_scroll * 0.8, 0))

        # Move the camera
        self.camera.scroll()

        # Draw static objects
        pygame.draw.rect(screen, (0, 0, 0), self.platform.move(-self.camera.offset.x, -self.camera.offset.y))
        pygame.draw.rect(screen, (0, 0, 0), self.ground.move(-self.camera.offset.x, -self.camera.offset.y))

        # Draw player and update sprite animation
        self.player.update_animation()
        self.player.draw(screen=screen, camera_offset=-self.camera.offset)
