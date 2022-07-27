import time
from collections import defaultdict
from pathlib import Path

from scripts.util.custom_sprite import CustomSprite
from scripts.bullet.bullet import Bullet
from scripts.sword.sword import Sword
from scripts.util.custom_sprite import CustomSprite
from scripts.util.healthbar import Healthbar
from scripts.util.sound import *


class Player(CustomSprite):
    """
    Class for initializing a player and controller.

    :param char_type: A str to indicate which type of character is to be displayed
    :param rect: A rect to display the player image
    """

    def __init__(self, char_type: str, rect: pygame.rect.Rect):
        super().__init__(hitbox_w_percent = 50, hitbox_h_percent = 100, hitbox_offset_x = 25, hitbox_offset_y = 0)

        self.char_type: str = char_type
        self.rect: pygame.rect.Rect = rect       

        self.animations: dict[str, list] = self.load_animations(size=(self.rect.w, self.rect.h))
        self.healthbar = Healthbar()
        self.velocity = pygame.math.Vector2(0, 0)
        self.direction = pygame.math.Vector2(1, 0)
        self.gravity: float = 0.5
        self.update_time: int = 0

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
                "shoot": [pygame.K_SPACE],
            },
            "interact": {
                "pickup": [pygame.K_e],
                "drop": [pygame.K_q]
            }
        }

        self.fire_rate = 500  # in ms
        self.last_fire_time = -1  # timestamp representing last time player fired a bullet

        self._is_grounded: bool = True
        self.is_sprinting: bool = False
        self.current_animation_frame = ["idle", 0]

        self.bullet_group = pygame.sprite.Group()
        self.sword_sprite = Sword(location=(self.rect.centerx + 24, self.rect.centery - 18))

        self._image = None

        # Load sounds that are associated with the player
        Sound("laser", "assets/sounds/sfx/laser.wav")

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

    @property
    def center(self) -> tuple:
        """ Returns the center of the player's hitbox. """
        return self.rect.center

    @center.setter
    def center(self, location: tuple):
        """
        Sets the center of the player's hitbox to the given location.

        :param location: A tuple representing the new location of the player's hitbox's center.
        :return: None
        """
        self.rect.center = location

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in self.input["movement"]["jump"]:
                    if self._is_grounded:
                        self._jump()
                if event.key in self.input["abilities"]["shoot"]:
                    # todo: use pygame time, rather than system time
                    # todo: make a proper game clock that compensates for pausing/resuming
                    current_time = time.time() * 1000
                    if current_time - self.last_fire_time >= self.fire_rate:
                        self._shoot()
                        self.last_fire_time = current_time
                if event.key in self.input["abilities"]["super jump"]:
                    if self._is_grounded:
                        self._super_jump()
                if event.key in self.input["movement"]["sprint"]:
                    self._sprint()
                if event.key in [pygame.K_m]:
                    self._sword_swing()
                if event.key in [pygame.K_n]:
                    self._sword_away()

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

    def _shoot(self):
        new_bullet = Bullet(location=(self.rect.centerx, self.rect.centery),
                                     direction=pygame.math.Vector2(1, 0) * self.direction.x,
                                     damage=10)
        # adjust starting position of new bullet so that its left/right edge starts at our center
        # rather than the center of the bullet starting at our center
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
        if self.rect.bottom >= 650:
            self.rect.bottom = 650
            self.is_grounded = True

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

    def set_animation(self, animation: str):
        if self.current_animation_frame[0] == animation:
            return

        self.current_animation_frame = [animation, 0]

    def load_animations(self, size: tuple) -> dict[str, list]:
        # Create container for animations
        animations: dict[str, list] = defaultdict(lambda: list())
        # Start at content root for this character type
        root_animations_dir = Path(f"assets/{self.char_type}/animations")

        # Iterate through animation types
        for animation_type_dir in root_animations_dir.iterdir():
            # Iterate through contents of animation type folder
            for frame in animation_type_dir.iterdir():
                # Load the frame
                img: pygame.Surface = pygame.image.load(frame).convert_alpha()
                # Scale it
                img = pygame.transform.scale(img, size)
                # Add it to big animation dictionary
                animations[animation_type_dir.name].append(img)

        return animations

    @property
    def image(self):
        return pygame.transform.flip(self._image, self.direction.x == -1, False)

    def draw(self, screen: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = False):
        super(Player, self).draw(screen, camera_offset, show_bounding_box)
        screen.blit(source=self.healthbar.render(self._image.get_width(), 12),
                    dest=self.rect.move(camera_offset).move(0, -12).move(-self.hitbox_offset_x, self.hitbox_offset_y))
