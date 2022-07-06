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
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # Player movement
        self.moving_left = False
        self.moving_right = False

        animation_types = ["idle", "run", "jump"]
        for animation in animation_types:
            # Get number of frames for this animation
            temp_list = []
            try:
                num_of_frames = len(os.listdir(f'{self.char_type}/animations/{animation}'))
            except FileNotFoundError:
                print(f"Warning: {f'{self.char_type}/animations/{animation}'} does not exist. Defaulting to 1 frame.")
                num_of_frames = 1

            # Load animation images
            for i in range(num_of_frames):
                filename = f'{self.char_type}/animations/{animation}/{i}.png'
                try:
                    img = pygame.image.load(filename)
                except FileNotFoundError:
                    print(f"Warning: Unable to load file {filename}. Defaulting to black square.")
                    img = pygame.Surface((128, 128))
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

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
