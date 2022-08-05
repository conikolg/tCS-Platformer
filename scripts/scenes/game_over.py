from scripts.scenes.base_scene import BaseScene
from scripts.util.button import Button
from scripts.util.sound import *


class GameOverScene(BaseScene):
    def __init__(self):
        super().__init__()

        # Load LevelOneScene (done here to avoid circular import issue)
        from scripts.scenes.level_one import LevelOneScene

        # Color shared by game over text and buttons
        self.game_over_theme_color = (200, 0, 0)

        # Processes transition from game over back to level 1
        def on_try_again_clicked():
            # Stop title theme
            stop_sound("gameOverTheme")

            # Create level one scene
            level_one = LevelOneScene()

            # Make sure level one's sound setting matches game over scene's sound setting
            level_one.sound_enabled = self.sound_enabled
            level_one.update_sounds()

            # Transition to level 1      
            self.scene_manager.go_to(level_one)

        self.try_again_button = Button(
            text="Try Again?",
            rect=(520, 400, 240, 40),
            on_click_fn=on_try_again_clicked,
            text_color=self.game_over_theme_color,
            background_color=(0, 0, 0),
            hover_color=(50, 50, 50)
        )

        # Load and play game over theme song
        load_sound("gameOverTheme", "assets/sounds/wavFiles/game_over_theme_2.wav", volume=30)
        play_sound("gameOverTheme")

        # Load camera for title scene (used for auto scrolling)
        # self.camera = Camera(behavior=AutoScroll(speed = 1))

        # Load scenery for title animation (copied from level_one.py)
        # Store all layers in a dict with the delta scroll for each layer
        # self.scenery: dict[pygame.Surface, float] = self.load_scenery(size=(self.camera.DISPLAY_W,
        #                                                                   self.camera.DISPLAY_H))

        # Length of level used in render method (for scenery layers)
        # self.length = 5

        # If sound is enabled for title scene
        self.sound_enabled = True

        # Ensure sounds are properly muted or muted when this scene loads ... probably unnecessary but sanity check
        self.update_sounds()

    def handle_events(self, events: list[pygame.event.Event]):
        self.try_again_button.handle_events(events)

        # handle keys
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.sound_enabled = not self.sound_enabled
                self.update_sounds()

    def update(self):
        pass

    def render(self, screen: pygame.Surface):
        # Black background
        screen.fill((0, 0, 0))

        # Title
        game_over_font = pygame.font.Font("assets/dogicapixelbold.ttf", 48)
        game_over_text = game_over_font.render("GAME OVER", True, self.game_over_theme_color)
        screen.blit(game_over_text, dest=(
            screen.get_width() / 2 - game_over_text.get_width() / 2,
            screen.get_height() / 4 - game_over_text.get_height() / 2))

        # Buttons
        screen.blit(self.try_again_button.render(), dest=self.try_again_button.rect)

    # Updates sound effects according to whether or not sound is enabled for this scene
    def update_sounds(self):
        if self.sound_enabled:
            for sound_name in sounds.keys():
                unmute_sound(sound_name)
        else:
            for sound_name in sounds.keys():
                mute_sound(sound_name)
