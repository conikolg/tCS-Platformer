from collections import defaultdict
from pathlib import Path

import pygame
import math

from scripts.bullet.bullet import Bullet
from scripts.sword.sword import Sword


class Player(pygame.sprite.Sprite):
    """
    Class for initializing a player and controller.

    :param char_type: A str to indicate which type of character is to be displayed
    :param rect: A rect to display the player image
    """

    def __init__(self, char_type: str, rect: pygame.rect.Rect):
        super().__init__()

        self.char_type: str = char_type
        self.rect: pygame.rect.Rect = rect

        self.animations: dict[str, list] = self.load_animations(size=(self.rect.w, self.rect.h))
        self.health: float = 100.0
        self.x_speed: float = 0.0
        self.delta_x: float = 5.0
        self.y_speed: float = 0.0
        self.jump_speed: float = 10.0
        self.gravity: float = 0.5
        self.horizontal_direction: int = 1  # Right
        self.update_time: int = 0

        # Nested dict to store all player input key binds
        # This will allow the player to easily remap keys once feature is created
        # WARNING: Do not make changes to this dict without also adding the image bind to assets/keys
        self.input = {
            "movement": {
                "left": [pygame.K_LEFT, pygame.K_a],
                "right": [pygame.K_RIGHT, pygame.K_d],
                "sprint": [pygame.K_LSHIFT, pygame.K_s],
                "jump": [pygame.K_SPACE, pygame.K_UP, pygame.K_w]
            },
            "abilities": {
                "shoot": [pygame.K_j],
                "other thing here": [pygame.K_k],
                "another other thing here": [pygame.K_l],
                "super jump": [pygame.K_p],
            },
            "interact": {
                "pickup": [pygame.K_e],
                "drop": [pygame.K_q]
            }
        }

        # TODO: add shoot cooldown once the bullet is working properly

        self._is_grounded: bool = True
        self.current_animation_frame = ["idle", 0]

        self.bullet_group = pygame.sprite.Group()
        self.sword_sprite = Sword(location=(self.rect.centerx + 24, self.rect.centery - 18))

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
            self.y_speed = 0

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
                    self._shoot()
                if event.key in self.input["abilities"]["super jump"]:
                    if self._is_grounded:
                        self._super_jump()
                if event.key in self.input["movement"]["sprint"]:
                    self._sprint()
                # if event.key not in self.input["movement"]["sprint"]:
                #     self.x_speed = 5.0
                if event.key in [pygame.K_m]:
                    self._swordSwing()
                if event.key in [pygame.K_n]:
                    self._swordAway()

    def _jump(self):
        self.y_speed = self.jump_speed
        self._is_grounded = False
        self.set_animation("jump")

    def _sprint(self):
        self.delta_x = 10.0

    def _super_jump(self):
        self.y_speed = self.jump_speed * 2
        self._is_grounded = False
        self.set_animation("jump")

    def _shoot(self):
        self.bullet_group.add(Bullet(location=(self.rect.centerx, self.rect.centery),
                                     direction=pygame.math.Vector2(1, 0) * self.horizontal_direction))

    def _moveSword(self):
        if self.horizontal_direction == 1:
            self.sword_sprite.sword_direction = 0
            self.sword_sprite.rect.center = (self.rect.centerx + 33, self.rect.centery - 6)
        else:
            self.sword_sprite.sword_direction = 1
            self.sword_sprite.rect.center = (self.rect.centerx - 33, self.rect.centery - 6)

    def _swordSwing(self):
        self.sword_sprite.sword_swing = True

    def _swordAway(self):
        self.sword_sprite.sword_swing = False

    def update(self) -> None:
        keys = pygame.key.get_pressed()

        # Move left/right
        horizontal_movement = pygame.math.Vector2(0, 0)

        for key in self.input["movement"]["right"]:
            if keys[key]:
                horizontal_movement.x += 1
                self.horizontal_direction = 1
                self.x_speed = self.delta_x
        for key in self.input["movement"]["left"]:
            if keys[key]:
                horizontal_movement.x -= 1
                self.horizontal_direction = -1
                self.x_speed = self.delta_x

        # Slowly decrease x_speed
        # Check if player is not moving horizontally
        # Reset delta x to normal value
        self.x_speed *= 0.8
        self.x_speed = math.floor(self.x_speed)
        if self.x_speed < 1:
            self.delta_x = 5.0

        # Horizontal movement
        self.rect.move_ip(horizontal_movement * self.x_speed)

        # Vertical movement
        self.y_speed -= self.gravity
        self.rect.move_ip(0, -self.y_speed)
        # Collided with "ground"?
        if self.rect.bottom >= 650:
            self.rect.bottom = 650
            self.is_grounded = True

        # Update animation state
        if not self._is_grounded:
            if self.y_speed >= 0:
                self.set_animation("jump")
            else:
                self.set_animation("fall")
        elif horizontal_movement.x != 0:
            self.set_animation("run")
        else:
            self.set_animation("idle")

    def set_animation(self, animation: str):
        if self.current_animation_frame[0] == animation:
            return

        self.current_animation_frame = [animation, 0]

    def update_animation(self):
        animation_cooldown = 100
        self.image = self.animations[self.current_animation_frame[0]][self.current_animation_frame[1]]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.current_animation_frame[1] += 1

        if self.current_animation_frame[1] >= len(self.animations[self.current_animation_frame[0]]):
            self.current_animation_frame[1] = 0

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
                # TODO: smoothscale or scale? scale makes the picture look better imo
                img = pygame.transform.scale(img, size)
                # Add it to big animation dictionary
                animations[animation_type_dir.name].append(img)

        return animations

    def draw(self, screen: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = False):
        if camera_offset is None:
            camera_offset = pygame.math.Vector2(0, 0)

        self.update_animation()
        screen.blit(source=pygame.transform.flip(self.image, self.horizontal_direction == -1, False),
                    dest=self.rect.move(camera_offset))

        if show_bounding_box:
            pygame.draw.rect(surface=screen, color=(255, 0, 0), rect=self.rect.move(camera_offset), width=1)

        self._moveSword()
