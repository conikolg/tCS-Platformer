from pathlib import Path

import pygame
import pymunk
import pymunk.pygame_util

from scripts import collision_types as coll_types
from scripts.enemy.basic_enemy import BasicEnemy
from scripts.leveldesigner.level_designer import LevelDesigner
from scripts.player.bullet import Bullet
from scripts.player.player import Player
from scripts.scenes.base_scene import BaseScene
from scripts.scenes.exit import Exit
from scripts.scenes.game_over import GameOverScene
from scripts.ui.ui import UI
from scripts.util import game_time
from scripts.util.camera import Camera, BoundedFollowTarget
from scripts.util.sound import load_sound, sounds, unmute_sound, mute_sound, stop_sound


class LevelOneScene(BaseScene):
    def __init__(self):
        super().__init__()

        # Reset game clock
        game_time.reset()

        # Define identity of this level
        self.level_id = 1

        # Create pymunk simulation space
        self.world = pymunk.Space()
        self.world.gravity = (0, -1500.0)
        pymunk.pygame_util.positive_y_is_up = True

        # Build/populate level
        self.level_designer = LevelDesigner(world=self.world, level=self.level_id)
        self.platforms: list = self.level_designer.platforms
        self.enemies: list = self.level_designer.enemies
        self.exit: Exit = self.level_designer.exit

        # Create player
        self.player = Player("default", rect=pygame.rect.Rect(100, 350, 50, 100), world=self.world)
        self.ui = UI(player=self.player)

        # Attach camera to player TODO: compensate for weirdness with bottom being cut-off on Macs
        self.camera = Camera(
            behavior=BoundedFollowTarget(
                target=self.player,
                horizontal_limits=(0, self.level_designer.max_x),
                vertical_limits=(-self.level_designer.max_y / 2 + 15, self.level_designer.max_y / 2 + 15))
        )

        # Store all layers in a dict with the delta scroll for each layer
        self.scenery: dict[pygame.Surface, float] = self.load_scenery(level=self.level_id)

        # Sounds
        self.sound_enabled = None
        load_sound("levelOneTheme", "assets/sounds/wavFiles/metroid_brinstar_theme.wav", 50)

        # UI toggles
        self.show_controls_help: bool = True
        self.show_hitboxes: bool = True

        def player_bullet_collision(arbiter: pymunk.Arbiter, space, data):
            """ Disable collisions between the player and bullets. """
            return False

        def enemy_bullet_collision(arbiter: pymunk.Arbiter, space, data):
            """ Deals damage to the enemy hit. Despawns the bullet, despawns the enemy if it dies. """
            enemy: BasicEnemy = arbiter.shapes[0].body.obj
            bullet: Bullet = arbiter.shapes[1].body.obj

            # Apply damage
            enemy.take_damage(bullet.damage)

            # Remove enemy if needed
            if not enemy.enabled:
                self.enemies.remove(enemy)

            # Remove bullet if needed
            if bullet.enabled:
                bullet.despawn()
                self.player.bullets.remove(bullet)

            # Do not collide
            return False

        def terrain_bullet_collision(arbiter: pymunk.Arbiter, space, data):
            """ Despawns the bullet. """
            # Make sure bullet can only be deleted once
            bullet = arbiter.shapes[1].body.obj
            if bullet.enabled:
                bullet.despawn()
                self.player.bullets.remove(bullet)

            # Do not collide
            return False

        def player_enemy_collision(arbiter: pymunk.Arbiter, space, data):
            """ Cause the player to take damage. """
            player: Player = arbiter.shapes[0].body.obj

            enemy_dmg: int = 10
            player.health -= enemy_dmg

            return False

        def player_exit_collision(arbiter: pymunk.Arbiter, space, data):
            """ What happens when the player reaches the exit of the map. """

            print("Complete!")
            return False

        # Collision handlers that run on "begin" step, which is start of collision only
        self.world.add_collision_handler(coll_types.PLAYER, coll_types.BULLET).begin = player_bullet_collision
        self.world.add_collision_handler(coll_types.ENEMY, coll_types.BULLET).begin = enemy_bullet_collision
        self.world.add_collision_handler(coll_types.TERRAIN, coll_types.BULLET).begin = terrain_bullet_collision
        # Collision handlers that run on "pre-solve" step, which is every time that two objects are touching
        self.world.add_collision_handler(coll_types.PLAYER, coll_types.ENEMY).pre_solve = player_enemy_collision
        self.world.add_collision_handler(coll_types.PLAYER, coll_types.EXIT).pre_solve = player_exit_collision

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
        Allows everything in the world to have a chance to update. Also checks if player has died.
        """

        # Update player
        self.player.update()

        # Update enemies
        for enemy in self.enemies:
            enemy.update()

        # Tick time and physics
        game_time.tick()
        self.world.step(1.0 / 60)

        # Game over if the player falls out the bottom of the world
        if self.player.body.position.y <= 0:
            self.fail_level()
        # Game over if the player has no health remaining
        elif self.player.health <= 0:
            self.fail_level()

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
        Clears the screen, draws game elements, enemies, bullets, the player, and then the UI/HUD overlay.

        The player should always be centered on the screen because of the camera. The other
        components of the level should appear relative to the player.

        :param screen: the Surface to render on to.
        :return: None
        """

        # White background
        screen.fill((255, 255, 255))
        self.render_scenery(screen=screen)

        # Move the camera
        self.camera.constant = pygame.Vector2(-screen.get_width() / 2, screen.get_height() / 2)
        self.camera.scroll()

        # Draw level elements first
        self.exit.draw(screen=screen, camera_offset=-self.camera.offset, show_bounding_box=self.show_hitboxes)
        for platform in self.platforms:
            platform.draw(screen=screen, camera_offset=-self.camera.offset, show_bounding_box=self.show_hitboxes)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen=screen, camera_offset=-self.camera.offset, show_bounding_box=self.show_hitboxes)

        # Draw bullets
        for bullet in self.player.bullets:
            bullet.draw(screen, camera_offset=-self.camera.offset, show_bounding_box=self.show_hitboxes)

        # Draw player and update sprite animation
        self.player.draw(screen=screen, camera_offset=-self.camera.offset, show_bounding_box=self.show_hitboxes)
        self.player.sword_sprite.draw(screen, camera_offset=-self.camera.offset, show_bounding_box=self.show_hitboxes)

        # Draw UI last
        self.ui.draw(screen, show_controls=self.show_controls_help)

    def update_sounds(self):
        """ Updates sound effects according to whether or not sound is enabled for this scene. """

        for sound_name in sounds.keys():
            if self.sound_enabled:
                unmute_sound(sound_name)
            else:
                mute_sound(sound_name)

    def fail_level(self):
        """ Transitions to the Game Over screen. """

        # Stop title theme
        stop_sound("levelOneTheme")

        # Create level one scene
        game_over_scene = GameOverScene()

        # Make sure game over scene's sound setting matches level one's sound setting
        game_over_scene.sound_enabled = self.sound_enabled
        game_over_scene.update_sounds()

        # Transition to game over scene
        self.scene_manager.go_to(game_over_scene)
