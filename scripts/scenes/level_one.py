from pathlib import Path

import pygame
import pymunk
import pymunk.pygame_util

from scripts import collision_types
from scripts.leveldesigner.level_designer import LevelDesigner
from scripts.player.player import Player
from scripts.scenes.base_scene import BaseScene
from scripts.scenes.game_over import GameOverScene
from scripts.ui.ui import UI
from scripts.util import game_time
from scripts.util.camera import Camera, BoundedFollowTarget
from scripts.util.custom_group import CustomGroup
from scripts.util.sound import load_sound, sounds, unmute_sound, mute_sound, stop_sound


class LevelOneScene(BaseScene):
    def __init__(self):
        super().__init__()

        # Define identity of this level
        self.level_id = 1

        # Create pymunk simulation space
        self.world = pymunk.Space()
        self.world.gravity = (0, -1500.0)
        pymunk.pygame_util.positive_y_is_up = True

        self.player = Player("default", rect=pygame.rect.Rect(100, 550, 100, 100), world=self.world)
        self.ui = UI(player=self.player)

        # Attach camera to player
        self.camera = Camera(
            behavior=BoundedFollowTarget(
                target=self.player,
                horizontal_limits=(0, 6000),
                vertical_limits=(-7200, 7200)),
            # TODO: compensate for weirdness with bottom being cut-off on Macs
            constant=pygame.math.Vector2(-640 + self.player.w / 2, 360 - self.player.h / 2))

        # Store all layers in a dict with the delta scroll for each layer
        self.scenery: dict[pygame.Surface, float] = self.load_scenery(level=self.level_id)

        # Populate level
        self.level_designer = LevelDesigner(level=self.level_id)
        self.level_designer.get_level_data()
        self.level_designer.generate_platforms(world=self.world)

        # Store platforms
        self.platforms: list = self.level_designer.platforms

        # Store enemies
        self.enemy_group: CustomGroup = CustomGroup()
        self.enemy_group.add(*self.level_designer.enemies)

        # Sounds
        self.sound_enabled = None
        load_sound("levelOneTheme", "assets/sounds/wavFiles/metroid_brinstar_theme.wav", 50)

        # UI toggles
        self.show_controls_help: bool = True
        self.show_hitboxes: bool = True

        # Define collisions between player and bullets
        def player_bullet_collision(arbiter: pymunk.Arbiter, space, data):
            # TODO: Let player handle the hit
            # TODO: Let bullet handle the hit
            return False

        self.world.add_collision_handler(collision_types.PLAYER, collision_types.BULLET).begin = player_bullet_collision

        # Reset game clock
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

        # Update player
        self.player.update()

        # Tick time and physics
        game_time.tick()
        self.world.step(1.0 / 60)

        # TODO: Prevent player from going out of bounds via pymunk
        # if self.player.rect.left < 0:
        #     self.player.rect.left = 0
        # right_bound = self.camera.behavior.horizontal_limits[1]
        # if self.player.rect.right > self.camera.behavior.horizontal_limits[1]:
        #     self.player.rect.right = right_bound
        # # Did player fall out of bounds and die?
        # if self.player.rect.top > self.camera.behavior.vertical_limits[1]:
        #     self.player.healthbar.health = 0

        # TODO: Process player-enemy collisions via pymunk
        # if self.player.vulnerable:
        #     collisions = pygame.sprite.spritecollide(self.player, self.enemy_group, dokill=False)
        #     if len(collisions) > 0:
        #         self.player.take_damage(10)

        # TODO: Did the player fall off something? via pymunk
        # if self.player.is_grounded and self.player.velocity.y < -0.5:
        #     self.player.is_grounded = False

        # TODO: Update bullets via pymunk
        # self.player.bullet_group.update(self.player.rect.x + self.camera.DISPLAY_W / 2,
        #                                 self.player.rect.x - self.camera.DISPLAY_W / 2)

        # TODO: Update enemies via pymunk
        # self.enemy_group.update()

        # Process enemy-bullet collisions
        # NOTE: I (Nathan) am not as familiar with pygame sprite groups
        #       so not sure if this is the way to go here
        # also, are there any issues with deleting the bullet/enemy from the list as we iterate over it?
        # or does .kill() handle this gracefully?
        # BUG: this is causing damage to all enemies. Why? Is this the proper way to interact with health?
        # NOTE: this code technically allows a bullet to collide with multiple enemies on one frame
        # TODO: Bullet collision via pymunk
        # for bullet in self.player.bullet_group:
        #     collisions = pygame.sprite.spritecollide(bullet, self.enemy_group, dokill=False)
        #     for collidedEnemy in collisions:
        #         collidedEnemy.healthbar.health = collidedEnemy.healthbar.health - bullet.damage
        #         bullet.kill()
        #         # check if enemy took enough damage to die
        #         if collidedEnemy.healthbar.health <= 0:
        #             collidedEnemy.kill()

        # Check if the game should end
        # self.game_over_check()

    @staticmethod
    def load_scenery(level: int) -> dict[pygame.Surface, float]:
        # Create container for scenery
        scenery: dict[pygame.Surface, float] = dict()
        # Start at content root
        # Sort path for macOS to read clearly
        root_scenery_dir = sorted(Path(f"assets/scenery/level{level}").iterdir())

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
        for x in range(5):
            for layer, ds in self.scenery.items():
                # In order to account for vertical parallax, the layers have to be displayed at a negative offset
                # Calculate this offset by multiplying the delta scroll by the player height and subtract the
                # difference between the camera offset y times the delta scroll and the player height
                screen.blit(layer, ((x * self.camera.DISPLAY_W) - self.camera.offset.x * ds,
                                    (self.player.h * ds) - 640 - self.camera.offset.y * ds - self.player.h))

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
        for platform in self.platforms:
            platform.draw(screen=screen, camera_offset=-self.camera.offset)

        # Draw enemies
        self.enemy_group.draw(surface=screen, camera_offset=-self.camera.offset, show_bounding_box=self.show_hitboxes)

        # Draw bullets
        for bullet in self.player.bullets:
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
