from collections import defaultdict
from pathlib import Path

import pygame.mask
import pymunk

from scripts import body, collision_types
from scripts.player.bullet import Bullet
from scripts.player.sword import Sword
from scripts.ui.healthbar import Healthbar
from scripts.util import coloring, game_time
from scripts.util.image_utils import auto_crop
from scripts.util.sound import *


class Player:
    def __init__(self, char_type: str, rect: pygame.rect.Rect, world: pymunk.Space):
        """
        Class for initializing a player.

        :param char_type: A str to indicate which type of character is to be displayed
        :param rect: A rect to position and size the player
        :param world: A pymunk Space, to which the player will be added and will interact with other objects
        """

        # Save the world. Needed for spawning bullets
        self.world: pymunk.Space = world

        # Define visual attributes
        self.char_type: str = char_type
        self.outfits = {
            "default": {
                "shirt_main": (227, 224, 224),
                "shirt_shadow": (184, 177, 177),
                "skin_main": (193, 136, 103),
                "skin_shadow": (153, 104, 76),
                "hair": (71, 45, 60),
                "belt": (0, 162, 157),
                "pants_main": (47, 43, 92),
                "pants_shadow": (0, 33, 59)
            },

            "jared": {
                "shirt_main": (40, 40, 40),
                "shirt_shadow": (20, 20, 20),
                "skin_main": (196, 148, 130),
                "skin_shadow": (162, 116, 95),
                "hair": (39, 22, 19),
                "belt": (103, 21, 16),
                "pants_main": (44, 36, 60),
                "pants_shadow": (4, 36, 60)
            },

            # "usman": {
            #     "shirt_main": (218, 65, 103),
            #     "shirt_shadow": (131, 33, 97),
            #     "skin_main": (167, 108, 71),
            #     "skin_shadow": (159, 112, 90),
            #     "hair": (39, 22, 19)
            # }
        }
        self.animations: dict[str, list] = self.load_animations(size=(rect.w, rect.h))
        self.direction = pymunk.Vec2d(1, 0)

        # Create physics body with (infinite moment of inertia to disable rotation)
        self.body = body.Body(mass=10, moment=float("inf"), body_type=pymunk.Body.DYNAMIC, obj=self)
        self.body.position = rect.center

        # Create physics shape/hitbox
        self.shape = pymunk.Poly.create_box(body=self.body, size=(rect.w, rect.h), radius=1)
        self.shape.collision_type = collision_types.PLAYER
        self.shape.elasticity = 0.1
        self.shape.friction = 0.9

        # Add to world
        self.world.add(self.body, self.shape)

        # Health
        self._healthbar = Healthbar()

        # Constants
        self.jump_speed: float = 800
        self.super_jump_speed: float = self.jump_speed * 1.6
        self.walk_acceleration: float = 50
        self.top_walk_speed: float = 500
        self.sprint_speed: float = 8.0

        # Nested dict to store all player input key binds
        # Allow us to easily remap keys as features are created
        # WARNING: Do not make changes to this dict without also adding the image bind to assets/keys
        self.input = {
            "movement": {
                "left": [pygame.K_LEFT, pygame.K_a],
                "right": [pygame.K_RIGHT, pygame.K_d],
                "sprint": [pygame.K_LSHIFT, pygame.K_RSHIFT],
                "jump": [pygame.K_UP, pygame.K_w]
            },
            "abilities": {
                "super jump": [pygame.K_p],
                "shoot": [pygame.K_SPACE]
            },
            # NOTE: We probably ought to make UI controls distinct from the player,
            #       but this is a quick way to get the keys to show up in the controls menu.
            "ui": {
                "show controls": [pygame.K_F1],
                "show hitboxes": [pygame.K_F9],
                "toggle sound": [pygame.K_m],
            }
        }

        self.shoot_cooldown = 0.5  # Minimum time between new bullets, in seconds
        self.can_shoot = True

        self._is_grounded: bool = True
        self.is_sprinting: bool = False
        self.current_animation_frame = ["idle", 0]

        self.bullets: list = []
        self.sword_sprite = Sword(location=(self.body.position.x + 24, self.body.position.y - 18))

        self.set_animation("jump")
        game_time.schedule(self.update_animation, 0.1, repeating=True)

        self.vulnerable = True
        self.recovering = False  # if the player is currently "recovering" from being damaged
        self.invulnerability_duration = 100  # how long invulnerability should last during recovery (in frames units)
        self.invulnerability_frame = 0  # how long the player has been invulnerable (in frames units)
        self.harm_flash_on = False  # if the flash is currently on or off
        self.harm_flash_duration = 2  # how long a flash (on or off) should last (in frames units)
        self.harm_flash_frame = 0  # how long the player has been in the current flash state (on/off; in frames units)

        # Load sounds that are associated with the player
        load_sound("laser", "assets/sounds/sfx/laser.wav")
        load_sound("jump", "assets/sounds/sfx/metroid_jump.wav", volume=40)

    @property
    def w(self) -> float:
        return self.shape.bb.right - self.shape.bb.left

    @property
    def h(self) -> float:
        return self.shape.bb.top - self.shape.bb.bottom

    def __str__(self):
        health_percent = round(self._healthbar.health / self._healthbar.maximum_health * 100, 2)
        return f"Player({self.body.position=}, {self.body.velocity=}, " \
               f"health={self._healthbar.health}/{self._healthbar.maximum_health} ({health_percent}%))"

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in self.input["movement"]["jump"]:
                    self._jump()
                if event.key in self.input["abilities"]["shoot"]:
                    # If possible, shoot and begin cooldown for next shot
                    if self.can_shoot:
                        self._shoot()
                        self._toggle_shoot(False)
                        game_time.schedule(self._toggle_shoot, self.shoot_cooldown, cb_args=(True,))
                if event.key in self.input["abilities"]["super jump"]:
                    self._super_jump()
                # if event.key in self.input["movement"]["sprint"]:
                #     self._sprint()

    def update(self) -> None:
        keys = pygame.key.get_pressed()

        pressing_key_right: bool = any(keys[key] for key in self.input["movement"]["right"])
        pressing_key_left: bool = any(keys[key] for key in self.input["movement"]["left"])

        # Move left/right
        self.shape.surface_velocity = 0, 0
        # Affect surface velocity if grounded
        if self._is_grounded:
            if pressing_key_right:
                self.shape.surface_velocity -= (self.top_walk_speed, 0)
            if pressing_key_left:
                self.shape.surface_velocity += (self.top_walk_speed, 0)
        # Else affect body directly at lesser strength
        else:
            # Move in the air
            if pressing_key_right:
                self.body.apply_force_at_local_point((self.top_walk_speed * 10, 0))
            if pressing_key_left:
                self.body.apply_force_at_local_point((-self.top_walk_speed * 10, 0))

            # If not attempting to move, apply air drag
            if not pressing_key_right and not pressing_key_left:
                self.body.velocity = (self.body.velocity.x * 0.97, self.body.velocity.y)
            # Else, ensure lack of friction is not exceeding walk limit
            else:
                self.body.velocity = (min(self.body.velocity.x, self.top_walk_speed), self.body.velocity.y)
                self.body.velocity = (max(self.body.velocity.x, -self.top_walk_speed), self.body.velocity.y)

        # Update direction the player is facing
        if pressing_key_right and not pressing_key_left:
            self.direction = pymunk.Vec2d(1, 0)
        elif not pressing_key_right and pressing_key_left:
            self.direction = pymunk.Vec2d(-1, 0)

        # Check if the player is grounded
        def check_if_grounded(arbiter: pymunk.Arbiter):
            if arbiter.normal.y == -1:
                self._is_grounded = True

        self._is_grounded = False
        self.body.each_arbiter(check_if_grounded)
        # TODO: Big loss of horizontal speed / kinetic energy on higher falls - fix it

        # Update animation state
        if not self._is_grounded:
            if self.body.velocity.y >= 0:
                self.set_animation("jump")
            else:
                self.set_animation("fall")
        elif abs(self.body.velocity.x) > 2:
            self.set_animation("run")
        else:
            self.set_animation("idle")

        # Update vulnerability state and flash effect
        self.update_vulnerability()

    def _jump(self):
        # Ignore if not currently grounded
        if self._is_grounded:
            # Apply jump force
            self.body.apply_impulse_at_local_point((0, self.jump_speed * self.body.mass))
            # Sound effect
            play_sound("jump")

    def _sprint(self):
        self.is_sprinting = True

    def _super_jump(self):
        if self._is_grounded:
            self.body.apply_impulse_at_local_point((0, self.super_jump_speed * self.body.mass))

        # Sound effect
        play_sound("jump")

    def _toggle_shoot(self, override: bool = None):
        """ Changes whether the player can or cannot shoot. """
        self.can_shoot = not self.can_shoot if override is None else override

    def _shoot(self):
        """ Creates a bullet with correct direction/positioning. """

        new_bullet = Bullet(
            location=self.body.position + tuple(self.direction.normalized() * self.w / 2),
            direction=self.direction,
            damage=50,
            world=self.world)
        self.bullets.append(new_bullet)

        # Play sound
        play_sound("laser")

    def _move_sword(self):
        raise Exception("Sword movement needs to be reimplemented!")

    def _sword_swing(self):
        raise Exception("Sword swing needs to be reimplemented!")

    def _sword_away(self):
        raise Exception("Sword sheathe needs to be reimplemented!")

    def set_animation(self, animation: str):
        """ Sets the current animation of the player. """

        if self.current_animation_frame[0] == animation:
            return
        self.current_animation_frame = [animation, 0]

    def update_animation(self):
        """ Advances the current animation to the next frame, looping back to the beginning if necessary. """

        self.current_animation_frame[1] += 1
        if self.current_animation_frame[1] == len(self.animations[self.current_animation_frame[0]]):
            self.current_animation_frame[1] = 0

    def load_animations(self, size: tuple) -> dict[str, list]:
        # Create container for animations
        animations: dict[str, list] = defaultdict(lambda: list())
        # Start at content root for this character type
        root_animations_dir = Path(f"assets/player/animations")

        # Iterate through animation types. TODO: overlay all animations together before cropping/scaling
        for animation_type_dir in root_animations_dir.iterdir():
            # Load all frames in the folder
            frames: list[pygame.Surface] = [pygame.image.load(frame).convert_alpha() for frame in
                                            animation_type_dir.iterdir()]
            # Automatically crop and scale them to just the occupied pixel portion
            frames: list[pygame.Surface] = auto_crop(images=frames, size=size)

            # Recolor
            for frame in frames:
                # Shift color values of image
                # self.shift_color(img=img, color_shift=0)
                for char, colors in self.outfits.items():
                    for color_name, color_value in colors.items():
                        coloring.recolor(frame, self.outfits["default"][color_name],
                                         self.outfits[self.char_type][color_name])

            # Assign frames to animation
            animations[animation_type_dir.name] = frames

        return animations

    @property
    def image(self):
        image: pygame.Surface = self.animations[self.current_animation_frame[0]][self.current_animation_frame[1]]
        return pygame.transform.flip(image, self.direction.x == -1, False)

    def draw(self, screen: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = False):
        # Update hitbox based on camera offset
        if camera_offset is None:
            camera_offset = pygame.math.Vector2(0, 0)

        # Adjust for pygame screen and camera location
        on_screen_destination = self.image.get_rect()
        on_screen_destination.center = (self.body.position.x, screen.get_height() - self.body.position.y)
        on_screen_destination.move_ip(camera_offset)

        # Draw image, if vulnerable and/or during flash-on while invulnerable
        if not self.harm_flash_on:
            screen.blit(self.image, dest=on_screen_destination)
        # Draw healthbar regardless
        screen.blit(self._healthbar.render(int(self.w)), dest=on_screen_destination.move(0, -12))

        # Draw hitbox
        if show_bounding_box:
            pygame.draw.rect(surface=screen, color=(255, 0, 0), rect=on_screen_destination, width=1)

    @property
    def health(self):
        """ The current health of the player. """
        return self._healthbar.health

    @health.setter
    def health(self, new_health):
        """ Handles any after effects due to health changes. """

        # Do nothing if no change
        if new_health == self.health:
            return

        # Damage taken
        if new_health < self.health:
            # Ignore if invulnerable
            if not self.vulnerable:
                return
            # Adjust health and trigger invulnerability grace period
            self._healthbar.health = new_health
            self.vulnerable = False
            self.harm_flash_on = True
            self.recovering = True

        # Healed
        else:
            self._healthbar.health = new_health

    def update_vulnerability(self):
        """ Updates the player's vulnerability state and flash effect, to indicate invulnerability. """

        # Flash effect only matters if we are in recovering state
        if not self.recovering:
            return

        # Advance frame counts
        self.harm_flash_frame += 1
        self.invulnerability_frame += 1

        # Check if we should flip the "flash" on or off 
        if self.harm_flash_frame >= self.harm_flash_duration:
            self.harm_flash_on = not self.harm_flash_on
            self.harm_flash_frame = 0

        # Check if we should end the invulnerability state
        if self.invulnerability_frame >= self.invulnerability_duration:
            self.vulnerable = True
            self.recovering = False
            self.invulnerability_frame = 0
            self.harm_flash_on = False
            self.harm_flash_frame = 0
