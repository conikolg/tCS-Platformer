import pygame

from scripts.scenes.base_scene import BaseScene
from scripts.scenes.level_one import LevelOneScene
from scripts.util.button import Button


class TitleScene(BaseScene):
    def __init__(self):
        super().__init__()

        self.play_button = Button(
            text="Play",
            rect=(580, 400, 120, 40),
            on_click_fn=lambda: self.scene_manager.go_to(LevelOneScene())
        )
        self.quit_button = Button(
            text="Quit",
            rect=(580, 500, 120, 40),
            on_click_fn=lambda: quit(0)
        )

    def handle_events(self, events: list[pygame.event.Event]):
        self.play_button.handle_events(events)
        self.quit_button.handle_events(events)

    def update(self):
        pass

    def render(self, screen: pygame.Surface):
        # White background
        screen.fill((255, 255, 255))

        # Title
        title_font = pygame.font.Font("assets/dogicapixelbold.ttf", 48)
        title_text = title_font.render("Platformer", True, (0, 0, 0))
        screen.blit(title_text, dest=(
            screen.get_width() / 2 - title_text.get_width() / 2,
            screen.get_height() / 4 - title_text.get_height() / 2))

        # Buttons
        screen.blit(self.play_button.render(), dest=self.play_button.rect)
        screen.blit(self.quit_button.render(), dest=self.quit_button.rect)
