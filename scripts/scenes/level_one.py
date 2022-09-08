from pathlib import Path

import pygame

from scripts.enemy.basic_enemy import BasicEnemy
from scripts.enemy.slime import Slime
from scripts.leveldesigner.level_designer import LevelDesigner
from scripts.player.player import Player
from scripts.scenes.base_scene import BaseScene
from scripts.scenes.game_over import GameOverScene
from scripts.scenes.simple_platform import Platform
from scripts.ui.ui import UI
from scripts.util import physics, game_time
from scripts.util.camera import Camera, BoundedFollowTarget
from scripts.util.custom_group import CustomGroup
from scripts.util.sound import *


class LevelOneScene(BaseScene):
    def __init__(self):
        super().__init__()

        self.player = Player("default", rect=pygame.rect.Rect(100, 250, 100, 100))
        self.ui = UI(player=self.player)

        # Length of level used in render method
        self.length = 5

        self.camera = Camera(
            behavior=BoundedFollowTarget(
                target=self.player,
                horizontal_limits=(0, 6000),
                vertical_limits=(-720, 720)),
            # TODO: compensate for weirdness with bottom being cut-off on Macs
            constant=pygame.math.Vector2(-640 + self.player.rect.w / 2, -self.player.rect.top))

        # Store all layers in a dict with the delta scroll for each layer
        self.scenery: dict[pygame.Surface, float] = self.load_scenery()

        self.level_designer = LevelDesigner(level=1)
        self.level_designer.get_level_data()
        self.level_designer.generate_platforms()

        # platform_image = pygame.image.load("assets/platforms/purple_platform.png")

        # Create all active platforms in this level
        self.platforms: CustomGroup = CustomGroup()

        # platforms = [
        #     # Little obstacle course
        #     Platform(rect=pygame.rect.Rect(800, 600, 64, 32), image=platform_image),
        #     Platform(rect=pygame.rect.Rect(900, 550, 64, 32), image=platform_image),
        #     Platform(rect=pygame.rect.Rect(1000, 500, 64, 32), image=platform_image),
        #     Platform(rect=pygame.rect.Rect(1100, 450, 64, 32), image=platform_image),
        #     Platform(rect=pygame.rect.Rect(1175, 500, 64, 32), image=platform_image),
        #     Platform(rect=pygame.rect.Rect(1400, 575, 64, 32), image=platform_image),
        #     Platform(rect=pygame.rect.Rect(1525, 575, 64, 32), image=platform_image),
        #
        #     # Long tunnel
        #     Platform(rect=pygame.rect.Rect(1650, 200, 800, 10)),
        #     Platform(rect=pygame.rect.Rect(1650, 80, 800, 10))
        # ]
        # self.platforms.add(*platforms)
        # Eventually we will remove all platforms above in replace for level designer platforms below. - Jared
        # platforms = [*self.level_designer.platforms]
        # Enemy type selection is not working because the level designer
        # Finds the enemy first and can not instantiate on platform since it doesnt exist yet

        self.platforms.add(*self.level_designer.platforms)
        print(f"Platforms: {len(self.platforms)}")
        for platform in self.platforms:
            print(platform.rect.w, platform.rect.h)

        # Create enemies
        self.enemy_group: CustomGroup = CustomGroup()
        # enemies = [
        #     # Enemy on the first platform
        #     Slime(platform=platforms[0], horizontal_offset=0),
        #
        #     # # Enemies inside the tunnel
        #     BasicEnemy(enemy_type="scorpion", platform=platforms[8], horizontal_offset=10),
        #     BasicEnemy(enemy_type="frog", platform=platforms[8], horizontal_offset=100),
        # ]
        self.enemy_group.add(*self.level_designer.enemies)

        # Level 1 sound
        self.sound_enabled = None
        load_sound("levelOneTheme", "assets/sounds/wavFiles/metroid_brinstar_theme.wav", 50)
        # play_sound("levelOneTheme")

        # Show Controls
        self.show_controls_help: bool = True

        # Show hitboxes
        self.show_hitboxes: bool = False

        # Reset clock when this level begins
        game_time.reset()

    def handle_events(self, events: list[pygame.event.Event]):
        """
        Allows the player to move up and down, to help test the camera system.

        :param events: a list of pygame events.
        :return: None
        """

        # Handle key events related to UI control
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                self.show_controls_help = not self.show_controls_help
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F9:
                self.show_hitboxes = not self.show_hitboxes
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.sound_enabled = not self.sound_enabled
                self.update_sounds()

                # Handle key events related to player control
        self.player.handle_events(events)

    def update(self):
        """
        Moves the player based on arrow keys or WASD keys pressed.
        """

        # Tick time
        game_time.tick()

        # Update player
        self.player.update()

        # Prevent player from going out of bounds
        if self.player.rect.left < 0:
            self.player.rect.left = 0
        right_bound = self.camera.behavior.horizontal_limits[1]
        if self.player.rect.right > self.camera.behavior.horizontal_limits[1]:
            self.player.rect.right = right_bound
        # Did player fall out of bounds and die?
        if self.player.rect.top > self.camera.behavior.vertical_limits[1]:
            self.player.healthbar.health = 0

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

        # Process player-enemy collisions
        if self.player.vulnerable:
            collisions = pygame.sprite.spritecollide(self.player, self.enemy_group, dokill=False)
            if len(collisions) > 0:
                self.player.take_damage(10)

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

        # Check if the game should end
        self.game_over_check()

    @staticmethod
    def load_scenery() -> dict[pygame.Surface, float]:
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
            img = pygame.transform.scale(img, size=(1280, 2880))
            # Create img layer key and assign ds value
            scenery[img] = round(ds, 1)
            # Increment by 0.1 for each layer
            ds += 0.1

        return scenery

    def render_scenery(self, screen: pygame.Surface):
        # Iterate through scenery dict and display
        for x in range(self.length):
            for layer, ds in self.scenery.items():
                # In order to account for vertical parallax, the layers have to be displayed at a negative offset
                # Calculate this offset by multiplying the delta scroll by the player height and subtract the
                # difference between the camera offset y times the delta scroll and the player height
                screen.blit(layer, ((x * self.camera.DISPLAY_W) - self.camera.offset.x * ds,
                                    (self.player.rect.h * ds) - 640 - self.camera.offset.y * ds - self.player.rect.h))

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

        self.render_scenery(screen=screen)

        # Move the camera
        self.camera.scroll()

        # Draw level elements first
        self.platforms.draw(surface=screen, camera_offset=-self.camera.offset, show_bounding_box=self.show_hitboxes)

        # Draw enemies
        self.enemy_group.draw(surface=screen, camera_offset=-self.camera.offset, show_bounding_box=self.show_hitboxes)

        # Draw bullets
        if self.player.bullet_group:
            for bullet in self.player.bullet_group:
                bullet.draw(screen, camera_offset=-self.camera.offset, show_bounding_box=self.show_hitboxes)

        # Draw player and update sprite animation
        self.player.draw(screen=screen, camera_offset=-self.camera.offset, show_bounding_box=self.show_hitboxes)
        self.player.sword_sprite.draw(screen, camera_offset=-self.camera.offset, show_bounding_box=self.show_hitboxes)

        # Draw UI last
        # @Jared - Just track the show/hide status in this file, not player.py. Also, if we have different
        # components of the UI, you can create a param for each component and set them like this. So maybe
        # later have a param like show_cooldowns=self.show_cooldowns, show_ammo=self.show_ammo, etc.
        self.ui.draw(screen, show_controls=self.show_controls_help)

    # Updates sound effects according to whether or not sound is enabled for this scene
    def update_sounds(self):
        if self.sound_enabled:
            for sound_name in sounds.keys():
                unmute_sound(sound_name)
        else:
            for sound_name in sounds.keys():
                mute_sound(sound_name)

    # Check if the game should end due to player's health falling below, falling off the level, etc.
    def game_over_check(self):
        if self.player.healthbar.health <= 0:
            self.fail_level()

    # Transition to Game Over scene
    def fail_level(self):

        # Stop title theme
        stop_sound("levelOneTheme")

        # Create level one scene
        game_over_scene = GameOverScene()

        # Make sure game over scene's sound setting matches level one's sound setting
        game_over_scene.sound_enabled = self.sound_enabled
        game_over_scene.update_sounds()

        # Transition to game over scene    
        self.scene_manager.go_to(game_over_scene)
