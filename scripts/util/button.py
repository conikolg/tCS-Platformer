from typing import Callable, Union

import pygame


class Button:
    def __init__(self,
                 text: str,
                 rect: Union[pygame.rect.Rect, tuple],
                 text_color: tuple = None,
                 background_color: tuple = None,
                 outline_color: tuple = None,
                 hover_color: tuple = None,
                 shape: str = None,
                 outline_width: int = None,
                 text_font: pygame.font.Font = None,
                 on_click_fn: Callable = None):
        self.text = text
        self.rect = rect
        self.text_color = (0, 0, 0) if text_color is None else text_color
        self.background_color = (255, 255, 255) if background_color is None else background_color
        self.outline_color = (0, 0, 0) if outline_color is None else outline_color
        self.hover_color = (150, 150, 150) if hover_color is None else hover_color
        self.shape = "rect" if shape is None else shape
        self.outline_width = 2 if outline_width is None else outline_width
        self.text_font = pygame.font.Font("assets/dogicapixelbold.ttf", 24) if text_font is None else text_font
        self.on_click_fn = None if on_click_fn is None else on_click_fn

        self._is_hovered = False
        if isinstance(self.rect, tuple) and len(self.rect) == 4:
            self.rect = pygame.rect.Rect(self.rect)

    def handle_events(self, events: list[pygame.event.Event], consume_events=True):
        """
        Allow the button to be responsive to pygame events.
        :param events: a list of pygame events
        :param consume_events: if True, events that this button "uses up" will be removed from the event list,
        preventing any future components from using those events. Enabled by default.
        :return: None
        """

        n = len(events)
        for i, event in enumerate(reversed(events)):
            # Determine if mouse entered the button. Consume event if it did.
            if event.type == pygame.MOUSEMOTION:
                self._is_hovered = self.rect.collidepoint(*pygame.mouse.get_pos())
                if self._is_hovered:
                    if consume_events:
                        events.pop(n - i - 1)
            # Determine if the button was clicked. Consume event if it did and invoke on_click callback.
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._is_hovered = self.rect.collidepoint(*pygame.mouse.get_pos())
                if self._is_hovered:
                    if consume_events:
                        events.pop(n - i - 1)
                    if self.on_click_fn is not None:
                        self.on_click_fn()

    def render(self) -> pygame.Surface:
        # Create canvas
        img = pygame.Surface((self.rect.w, self.rect.h)).convert_alpha()
        img.fill((0, 0, 0, 0))

        # Draw the shape of the button
        if self.shape == "rect":
            img.fill(self.outline_color)
            pygame.draw.rect(
                surface=img, color=self.hover_color if self._is_hovered else self.background_color,
                rect=(self.outline_width, self.outline_width,
                      img.get_width() - 2 * self.outline_width, img.get_height() - 2 * self.outline_width))
        else:
            raise NotImplementedError("Only 'rect'-shaped buttons are supported right now!")

        # Apply text
        text_surf = self.text_font.render(self.text, True, self.text_color)
        img.blit(source=text_surf, dest=(
            img.get_width() / 2 - text_surf.get_width() / 2,
            img.get_height() / 2 - text_surf.get_height() / 2,
        ))

        return img
