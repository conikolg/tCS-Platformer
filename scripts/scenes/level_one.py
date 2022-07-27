from pathlib import Path

from scripts.enemy.basic_enemy import BasicEnemy
from scripts.enemy.slime import Slime
from scripts.player.player import Player
from scripts.scenes.base_scene import BaseScene
from scripts.ui.ui import UI
from scripts.util import physics
from scripts.util.camera import Camera, BoundedFollowTarget
from scripts.util.custom_group import CustomGroup
from scripts.util.platform import Platform
from scripts.util.sound import *


class LevelOneScene(BaseScene):
    def __init__(self):
        super().__init__()

        self.player = Player("player", rect=pygame.rect.Rect(600, 550, 100, 100))
        self.ui = UI(player=self.player)

        # Length of level used in render method
        self.length = 5

        self.camera = Camera(
            behavior=BoundedFollowTarget(
                target=self.player,
                horizontal_limits=(0, 6000),
                vertical_limits=(-100, 0)),
            # TODO: compensate for weirdness with bottom being cut-off on Macs
            constant=pygame.math.Vector2(-640 + self.player.rect.w / 2, -self.player.rect.top))

        # Store all layers in a dict with the delta scroll for each layer
        self.scenery: dict[pygame.Surface, float] = self.load_scenery(size=(self.camera.DISPLAY_W,
                                                                            self.camera.DISPLAY_H))

        # Create all active platforms in this level
        self.platforms: CustomGroup = CustomGroup()
        platforms = [
            # Little obstacle course
            Platform(rect=pygame.rect.Rect(800, 600, 100, 10)),
            Platform(rect=pygame.rect.Rect(900, 550, 100, 10)),
            Platform(rect=pygame.rect.Rect(1000, 500, 100, 10)),
            Platform(rect=pygame.rect.Rect(1100, 450, 100, 10)),
            Platform(rect=pygame.rect.Rect(1175, 500, 100, 10)),
            Platform(rect=pygame.rect.Rect(1400, 575, 100, 10)),
            Platform(rect=pygame.rect.Rect(1525, 575, 100, 10)),

            # Long tunnel
            Platform(rect=pygame.rect.Rect(1650, 200, 800, 10)),
            Platform(rect=pygame.rect.Rect(1650, 80, 800, 10))
        ]
        self.platforms.add(*platforms)

        # Create enemies
        self.enemy_group: CustomGroup = CustomGroup()
        enemies = [

            # Enemy on the first platform
            Slime(platform=platforms[0], horizontal_offset=0),

            # # Enemies inside the tunnel
            BasicEnemy(enemy_type="scorpion", platform=platforms[8], horizontal_offset=10),
            BasicEnemy(enemy_type="frog", platform=platforms[8], horizontal_offset=100),

            # unused enemeis
            # BasicEnemy(platform=platforms[8], horizontal_offset=500),
            # BasicEnemy(platform=platforms[7], horizontal_offset=75),
            # BasicEnemy(platform=platforms[7], horizontal_offset=345),
            # BasicEnemy(platform=platforms[7], horizontal_offset=740),
        ]
        self.enemy_group.add(*enemies)

        # Create Sound objects used in level 1 (see sound.py for more info)
        Sound("levelOneTheme", "assets/sounds/music/metroid_brinstar_theme.mp3", 50)
        Sound("jump", "assets/sounds/sfx/mario_jump.mp3", 10)

        # Start level 1 music
        play_sound("levelOneTheme")

        # Show Controls
        self.show_controls_help: bool = True

    def handle_events(self, events: list[pygame.event.Event]):
        """
        Allows the player to move up and down, to help test the camera system.

        :param events: a list of pygame events.
        :return: None
        """

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                self.show_controls_help = not self.show_controls_help

        self.player.handle_events(events)

    def update(self):
        """
        Moves the player based on arrow keys or WASD keys pressed.
        """

        # Update player
        self.player.update()

        # Process player-platform collisions
        collisions = pygame.sprite.spritecollide(self.player, self.platforms, dokill=False)
        for collision in collisions:
            collision_side = physics.get_collision_side(collision.rect, self.player.rect)
            # Land on the platform
            if collision_side == "bottom" and self.player.velocity.y < 0:
                self.player.is_grounded = True
                self.player.rect.bottom = collision.rect.top
            # Bump head on a platform
            elif collision_side == "top" and self.player.velocity.y > 0:
                self.player.velocity.y = 0
            # Run into a platform moving left to right
            elif collision_side == "right":
                self.player.rect.right = collision.rect.left
            # Run into a platform moving right to left
            elif collision_side == "left":
                self.player.rect.left = collision.rect.right

        # Did the player fall off something?
        if self.player.is_grounded and self.player.velocity.y < -0.5:
            self.player.is_grounded = False

        # Update bullets
        self.player.bullet_group.update(self.player.rect.x + self.camera.DISPLAY_W / 2,
                                        self.player.rect.x - self.camera.DISPLAY_W / 2)

        # Update enemies
        self.enemy_group.update()

        # Process enemy-bullet collisions
        # NOTE: I (Nathan) am not as familiar with pygame sprite groups 
        #       so not sure if this is the way to go here
        # also, are there any issues with deleting the bullet/enemy from the list as we iterate over it? 
        # or does .kill() handle this gracefully?
        # BUG: this is causing damage to all enemies. Why? Is this the proper way to interact with health?
        # NOTE: this code technically allows a bullet to collide with multiple enemies on one frame
        for bullet in self.player.bullet_group:
            collisions = pygame.sprite.spritecollide(bullet, self.enemy_group, dokill=False)
            for collidedEnemy in collisions:
                collidedEnemy.healthbar.health = collidedEnemy.healthbar.health - bullet.damage
                bullet.kill()
                # check if enemy took enough damage to die
                if collidedEnemy.healthbar.health <= 0:
                    collidedEnemy.kill()

    @staticmethod
    def load_scenery(size: tuple) -> dict[pygame.Surface, float]:
        # Create container for scenery
        scenery: dict[pygame.Surface, float] = dict()
        # Start at content root
        # Sort path for macOS to read clearly
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

        # Draw level elements first
        self.platforms.draw(surface=screen, camera_offset=-self.camera.offset, show_bounding_box=True)

        # Draw enemies
        self.enemy_group.draw(surface=screen, camera_offset=-self.camera.offset, show_bounding_box=True)

        # Draw bullets
        if self.player.bullet_group:
            for bullet in self.player.bullet_group:
                bullet.draw(screen, camera_offset=-self.camera.offset)
                bullet.draw(screen, camera_offset=-self.camera.offset, show_bounding_box=True)

        # Draw player and update sprite animation
        self.player.update_animation()
        self.player.draw(screen=screen, camera_offset=-self.camera.offset, show_bounding_box=True)
        self.player.sword_sprite.draw(screen, camera_offset=-self.camera.offset, show_bounding_box=True)

        # Draw UI last
        # @Jared - Just track the show/hide status in this file, not player.py. Also, if we have different
        # components of the UI, you can create a param for each component and set them like this. So maybe
        # later have a param like show_cooldowns=self.show_cooldowns, show_ammo=self.show_ammo, etc.
        self.ui.draw(screen, show_controls=self.show_controls_help)
