import os

import pygame


class Player(pygame.sprite.Sprite):
    """
    Class for initializing a player and controller.
    """

    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # Player movement
        self.moving_left = False
        self.moving_right = False

        self.gravity = 0.75

        animation_types = ["idle", "run"]
        for animation in animation_types:
            # Get number of frames for this animation
            temp_list = []
            folder_path = f'assets/{self.char_type}/animations/{animation}'
            try:
                num_of_frames = len(os.listdir(folder_path))
            except FileNotFoundError:
                print(f"Warning: {folder_path} does not exist. Defaulting to 1 frame.")
                num_of_frames = 1

            # Load animation images TODO: scale sprites to specific image size, so the source image doesn't matter
            for i in range(num_of_frames):
                try:
                    img = pygame.image.load(f'{folder_path}/{animation} ({i}).png')
                except FileNotFoundError:
                    print(f"Warning: Unable to load file {folder_path}/{i}.png. Defaulting to black square.")
                    img = pygame.Surface((100, 100))
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        if self.jump:
            self.vel_y = -11
            self.jump = False

        # Apply gravity
        self.vel_y += self.gravity

        # Terminal velocity check
        if self.vel_y > 20:
            self.vel_y = 20

        # Rough ground collision check
        if self.rect.bottom + dy > 800:
            dy = 800 - self.rect.bottom

        dy += self.vel_y

        self.rect.move_ip(dx, dy)

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, screen: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = False):
        if camera_offset is None:
            camera_offset = pygame.math.Vector2(0, 0)

        screen.blit(source=pygame.transform.flip(self.image, self.flip, False), dest=self.rect.move(camera_offset))
        if show_bounding_box:
            pygame.draw.rect(surface=screen, color=(255, 0, 0), rect=self.rect.move(camera_offset), width=1)
