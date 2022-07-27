import pygame


class CustomSprite(pygame.sprite.Sprite):

    def __init__(self, hitbox_w_percent: int = 100, hitbox_h_percent: int = 100, hitbox_offset_x: int = 0,
                 hitbox_offset_y: int = 0):
        """
        Creates a CustomSprite.

        :param hitbox_w_percent: How much the hitbox width is scaled from the image width (1 to 100)
        :param hitbox_w_percent: How much the hitbox height is scaled from the image height (1 to 100)
        :param hitbox_offset_x: How much the hitbox is shifted right (in pixels) after being rescaled
        :param hitbox_offset_y: How much the hitbox is shifted down (in pixels) after being rescaled
        """
        super().__init__()

        # General
        self.visible = True
        self._image = None

        # Hitbox management
        self.hitbox_offset_x = hitbox_offset_x
        self.hitbox_offset_y = hitbox_offset_y
        self.hitbox_w_percent = hitbox_w_percent
        self.hitbox_h_percent = hitbox_h_percent

        # Animation management
        self.animations = None
        self.current_animation_frame = None
        self.update_time = None

    def update_animation(self):
        animation_cooldown = 100
        self._image = self.animations[self.current_animation_frame[0]][self.current_animation_frame[1]]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.current_animation_frame[1] += 1
        if self.current_animation_frame[1] >= len(self.animations[self.current_animation_frame[0]]):
            self.current_animation_frame[1] = 0

    def draw(self, surface: pygame.Surface, camera_offset: pygame.math.Vector2 = None, show_bounding_box: bool = False):
        if self.visible:

            # Update animations if this sprite has any
            if self.animations:
                self.update_animation()

            # Update hitbox based on camera offset
            if camera_offset is None:
                camera_offset = pygame.math.Vector2(0, 0)
            hitbox = self.rect.move(camera_offset)

            # Adjust image by undoing the transformations applied to rect by hitbox offset and percents
            image_x = hitbox.x - self.hitbox_offset_x
            image_y = hitbox.y - self.hitbox_offset_y
            image_w = hitbox.width / (self.hitbox_w_percent / 100)
            image_h = hitbox.height / (self.hitbox_h_percent / 100)
            image_rect = pygame.Rect(image_x, image_y, image_w, image_h)

            # Draw image
            surface.blit(self.image, dest=image_rect)

            # Draw hitbox
            if show_bounding_box:
                pygame.draw.rect(surface=surface, color=(255, 0, 0), rect=hitbox, width=1)

    def init_hitbox(self):
        """
        initializes this CustomSprite's hitbox based on hitbox offset and hitbox percent variables

        :return: None
        """

        image_width = self.rect.width
        image_height = self.rect.height
        new_width = image_width * (self.hitbox_w_percent / 100)
        new_height = image_height * (self.hitbox_h_percent / 100)
        new_x = self.rect.left + self.hitbox_offset_x
        new_y = self.rect.top + self.hitbox_offset_y
        self.rect = pygame.Rect(new_x, new_y, new_width, new_height)
