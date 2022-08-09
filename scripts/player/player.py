from collections import defaultdict
from pathlib import Path

from scripts.player.bullet import Bullet
from scripts.player.sword import Sword
from scripts.ui.healthbar import Healthbar
from scripts.util import game_time, coloring
from scripts.util.custom_sprite import CustomSprite
from scripts.util.sound import *


class Player(CustomSprite):
    """
    Class for initializing a player and controller.

    :param char_type: A str to indicate which type of character is to be displayed
    :param rect: A rect to display the player image
    """

    def __init__(self, char_type: str, rect: pygame.rect.Rect):
        super().__init__(hitbox_w_percent=50, hitbox_h_percent=100, hitbox_offset_x=25, hitbox_offset_y=0)

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

        self.rect: pygame.rect.Rect = rect

        self.animations: dict[str, list] = self.load_animations(size=(self.rect.w, self.rect.h))
        self.healthbar = Healthbar()
        self.velocity = pygame.math.Vector2(0, 0)
        self.direction = pygame.math.Vector2(1, 0)
        self.gravity: float = 0.5

        self.jump_speed: float = 12.0
        self.super_jump_speed: float = 20.0
        self.walk_speed: float = 5.0
        self.sprint_speed: float = 8.0

        # hitbox should be initialized after animation is loaded so that animation images have the original size
        super().init_hitbox()

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

        self.bullet_group = pygame.sprite.Group()
        self.sword_sprite = Sword(location=(self.rect.centerx + 24, self.rect.centery - 18))

        self._image = None

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

    def __str__(self):
        out_str = f"Player sprite located @ {self.rect.topleft}"
        health_percent = round(self.healthbar.health / self.healthbar.maximum_health * 100, 2)
        out_str += f" with {self.healthbar.health}/{self.healthbar.maximum_health} ({health_percent}%) HP"
        return out_str

    @property
    def is_grounded(self) -> bool:
        """ Returns True if the player is grounded (not falling), False otherwise. """
        return self._is_grounded

    @is_grounded.setter
    def is_grounded(self, grounded: bool):
        """
        Makes the player grounded (no longer falling) and sets y_speed to zero.

        :param grounded: A bool - True if the player is grounded on something, False otherwise.
        :return: None
        """
        self._is_grounded = grounded
        if self._is_grounded:
            self.velocity.y = 0

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in self.input["movement"]["jump"]:
                    if self._is_grounded:
                        self._jump()
                if event.key in self.input["abilities"]["shoot"]:
                    # If possible, shoot and begin cooldown for next shot
                    if self.can_shoot:
                        self._shoot()
                        self._toggle_shoot(False)
                        game_time.schedule(self._toggle_shoot, self.shoot_cooldown, cb_args=(True,))
                if event.key in self.input["abilities"]["super jump"]:
                    if self._is_grounded:
                        self._super_jump()
                if event.key in self.input["movement"]["sprint"]:
                    self._sprint()
                """
                if event.key in [pygame.K_m]:
                    self._sword_swing()
                if event.key in [pygame.K_n]:
                    self._sword_away()
                """

    def _jump(self):
        self.velocity.y = self.jump_speed
        self._is_grounded = False
        self.set_animation("jump")
        play_sound("jump")

    def _sprint(self):
        self.is_sprinting = True

    def _super_jump(self):
        self.velocity.y = self.super_jump_speed
        self._is_grounded = False
        self.set_animation("jump")
        play_sound("jump")

    def _toggle_shoot(self, override: bool = None):
        """ Changes whether the player can or cannot shoot. """
        self.can_shoot = not self.can_shoot if override is None else override

    def _shoot(self):
        """ Creates a bullet with correct direction/positioning and add it to local bullet group. """

        # Create bullet with non-outgoing edge positioned at player's center
        new_bullet = Bullet(location=(self.rect.centerx, self.rect.centery),
                            direction=pygame.math.Vector2(1, 0) * self.direction.x,
                            damage=50)
        if self.direction.x == 1:
            new_bullet.rect.left = self.rect.centerx
        else:
            new_bullet.rect.right = self.rect.centerx

        self.bullet_group.add(new_bullet)
        play_sound("laser")

    def _move_sword(self):
        if self.direction.x == 1:
            self.sword_sprite.sword_direction = 0
            self.sword_sprite.rect.center = (self.rect.centerx + 33, self.rect.centery - 6)
        else:
            self.sword_sprite.sword_direction = 1
            self.sword_sprite.rect.center = (self.rect.centerx - 33, self.rect.centery - 6)

    def _sword_swing(self):
        self.sword_sprite.sword_swing = True

    def _sword_away(self):
        self.sword_sprite.sword_swing = False

    def update(self) -> None:
        keys = pygame.key.get_pressed()

        # Move left/right
        actively_moving = False
        for key in self.input["movement"]["right"]:
            if keys[key]:
                self.velocity.x = self.sprint_speed if self.is_sprinting else self.walk_speed
                actively_moving = True
        for key in self.input["movement"]["left"]:
            if keys[key]:
                self.velocity.x = -(self.sprint_speed if self.is_sprinting else self.walk_speed)
                actively_moving = True

        # Apply friction
        if not actively_moving:
            self.velocity.x *= 0.75
            # No longer sprinting?
            if self.is_sprinting and abs(self.velocity.x) < self.walk_speed:
                self.is_sprinting = False
            # Not really moving
            if abs(self.velocity.x) < 0.5:
                self.velocity.x = 0

        # Gravity
        self.velocity.y -= self.gravity

        # Apply movement
        self.rect.move_ip(self.velocity.x, -self.velocity.y)
        if self.velocity.x != 0:
            self.direction.x = self.velocity.x / abs(self.velocity.x)
        if self.velocity.y != 0:
            self.direction.y = self.velocity.y / abs(self.velocity.y)

        # Collided with "ground"?
        # if self.rect.bottom >= 650:
        #     self.rect.bottom = 650
        #     self.is_grounded = True
        # Unnecessary collision as long as level csv file has a solid line of platforms (0)'s at bottom now.

        # Update sword
        self._move_sword()

        # Update animation state
        if not self._is_grounded:
            if self.velocity.y >= 0:
                self.set_animation("jump")
            else:
                self.set_animation("fall")
        elif self.velocity.x != 0:
            self.set_animation("run")
        else:
            self.set_animation("idle")

        # Update vulnerability state and flash effect
        self.update_vulnerability()

    def set_animation(self, animation: str):
        if self.current_animation_frame[0] == animation:
            return
        self.current_animation_frame = [animation, 0]

    def load_animations(self, size: tuple) -> dict[str, list]:
        # Create container for animations
        animations: dict[str, list] = defaultdict(lambda: list())
        # Start at content root for this character type
        root_animations_dir = Path(f"assets/player/animations")

        # Iterate through animation types
        for animation_type_dir in root_animations_dir.iterdir():
            # Iterate through contents of animation type folder
            for frame in animation_type_dir.iterdir():
                # Load the frame
                img: pygame.Surface = pygame.image.load(frame).convert_alpha()
                # Scale it
                img = pygame.transform.scale(img, size)
                # Shift color values of image
                # self.shift_color(img=img, color_shift=0)
                for char, colors in self.outfits.items():
                    for color_name, color_value in colors.items():
                        coloring.recolor(img, self.outfits["default"][color_name],
                                         self.outfits[self.char_type][color_name])
                # Add it to big animation dictionary
                animations[animation_type_dir.name].append(img)

        return animations

    @property
    def image(self):
        return pygame.transform.flip(self._image, self.direction.x == -1, False)

    def draw(self, screen: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = False):
        if not self.harm_flash_on:
            super(Player, self).draw(screen, camera_offset, show_bounding_box)
        screen.blit(source=self.healthbar.render(self._image.get_width(), 12),
                    dest=self.rect.move(camera_offset).move(0, -12).move(-self.hitbox_offset_x, self.hitbox_offset_y))

    # Causes the player to take damage and enter a "flashing" state to indicate temporary invulnerability
    def take_damage(self, amount):
        if not self.vulnerable:
            return
        self.healthbar.health = self.healthbar.health - amount
        self.vulnerable = False
        self.harm_flash_on = True
        self.recovering = True

    # Updates the player's vulnerability state and flash effect, to indicate invulnerability
    def update_vulnerability(self):

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
