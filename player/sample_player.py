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
                filename = f'{self.char_type}/animations/{animation}/{i}.gif'
                try:
                    img = pygame.image.load(filename)
                except FileNotFoundError:
                    print(f"Warn![](../../../Downloads/robot/0.gif)![](../../../Downloads/robot/1.gif)![](../../../Downloads/robot/2.gif)![](../../../Downloads/robot/3.gif)![](../../../Downloads/robot/4.gif)![](../../../Downloads/robot/5.gif)![](../../../Downloads/robot/6.gif)![](../../../Downloads/robot/7.gif)![](../../../Downloads/robot/8.gif)![](../../../Downloads/robot/9.gif)![](../../../Downloads/robot/10.gif)![](../../../Downloads/robot/11.gif)![](../../../Downloads/robot/12.gif)![](../../../Downloads/robot/13.gif)![](../../../Downloads/robot/14.gif)![](../../../Downloads/robot/15.gif)![](../../../Downloads/robot/16.gif)![](../../../Downloads/robot/17.gif)![](../../../Downloads/robot/18.gif)![](../../../Downloads/robot/19.gif)![](../../../Downloads/robot/20.gif)![](../../../Downloads/robot/21.gif)![](../../../Downloads/robot/22.gif)![](../../../Downloads/robot/23.gif)![](../../../Downloads/robot/24.gif)![](../../../Downloads/robot/25.gif)![](../../../Downloads/robot/26.gif)![](../../../Downloads/robot/27.gif)![](../../../Downloads/robot/28.gif)![](../../../Downloads/robot/29.gif)![](../../../Downloads/robot/30.gif)![](../../../Downloads/robot/31.gif)![](../../../Downloads/robot/32.gif)![](../../../Downloads/robot/33.gif)![](../../../Downloads/robot/34.gif)![](../../../Downloads/robot/35.gif)![](../../../Downloads/robot/36.gif)![](../../../Downloads/robot/37.gif)![](../../../Downloads/robot/38.gif)![](../../../Downloads/robot/39.gif)![](../../../Downloads/robot/40.gif)![](../../../Downloads/robot/41.gif)![](../../../Downloads/robot/42.gif)![](../../../Downloads/robot/43.gif)![](../../../Downloads/robot/44.gif)![](../../../Downloads/robot/45.gif)![](../../../Downloads/robot/46.gif)![](../../../Downloads/robot/47.gif)![](../../../Downloads/robot/48.gif)ing: Unable to load file {filename}. Defaulting to black square.")
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
