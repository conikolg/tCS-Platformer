from scripts.scenes.base_scene import BaseScene
from scripts.scenes.level_one import LevelOneScene
from scripts.ui.button import Button
from scripts.util.camera import Camera, AutoScroll
from scripts.util.sound import *


class TitleScene(BaseScene):
    def __init__(self):
        super().__init__()

        # Color shared by title text and buttons
        self.title_theme_color = (0, 200, 0)

        # Create scene on initialization to render background as well.
        # Is this bad practice? I know ideally we would not want to render the whole scene
        # until we click play. But this helps us with background on title screen.
        self.level_one = LevelOneScene()

        # Processes transition from title to level 1
        def on_play_clicked():
            # Stop title theme
            stop_sound("titleTheme")

            # Create level one scene
            level_one = LevelOneScene()

            # Make sure level one's sound setting matches title's sound setting
            level_one.sound_enabled = self.sound_enabled
            level_one.update_sounds()

            # Transition to level 1      
            self.scene_manager.go_to(level_one)

        self.play_button = Button(
            text="Play",
            rect=(580, 400, 120, 40),
            on_click_fn=on_play_clicked,
            text_color=self.title_theme_color,
            background_color=(0, 0, 0),
            hover_color=(50, 50, 50)
        )
        self.quit_button = Button(
            text="Quit",
            rect=(580, 500, 120, 40),
            on_click_fn=lambda: quit(0),
            text_color=self.title_theme_color,
            background_color=(0, 0, 0),
            hover_color=(50, 50, 50)
        )

        # Load and play title theme song
        load_sound("titleTheme", "assets/sounds/wavFiles/metroid_title_theme.wav", volume=50)
        play_sound("titleTheme")

        # Load camera for title scene (used for auto scrolling)
        self.camera = Camera(behavior=AutoScroll(speed=1))

        # Length of level used in render method (for scenery layers)
        self.length = 5

        # If is enabled for title scene
        self.sound_enabled = True

        # Ensure sounds are properly muted or muted when this scene loads ... probably unnecessary but sanity check
        self.update_sounds()

    def handle_events(self, events: list[pygame.event.Event]):
        self.play_button.handle_events(events)
        self.quit_button.handle_events(events)

        # handle keys
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.sound_enabled = not self.sound_enabled
                self.update_sounds()

    def update(self):
        pass

    def render(self, screen: pygame.Surface):
        # White background
        screen.fill((255, 255, 255))

        # Just realized doing it this way stops the title screen scrolling...
        self.level_one.render_scenery(screen)

        # Move the camera
        self.camera.scroll()

        # Reset the camera back to beginning position if it has gone too far
        # With enough "length" for this title "level", the player should rarely see the title screen camera reset
        # WARNING: This is spaghetti code! This is using a hard-coded value.
        #          Not sure if the value we check here should be based off the shortest layer's length or what.
        #          I am not sure what would accomplish the smoothest "camera reset" across all layers.
        if self.camera.offset.x >= 2400:
            self.camera.offset.x = 0

        # Title
        title_font = pygame.font.Font("assets/dogicapixelbold.ttf", 48)
        title_text = title_font.render("Lost in Cyberspace", True, self.title_theme_color)
        screen.blit(title_text, dest=(
            screen.get_width() / 2 - title_text.get_width() / 2,
            screen.get_height() / 4 - title_text.get_height() / 2))

        # Buttons
        screen.blit(self.play_button.render(), dest=self.play_button.rect)
        screen.blit(self.quit_button.render(), dest=self.quit_button.rect)

    # Updates sound effects according to whether or not sound is enabled for this scene
    def update_sounds(self):
        if self.sound_enabled:
            for sound_name in sounds.keys():
                unmute_sound(sound_name)
        else:
            for sound_name in sounds.keys():
                mute_sound(sound_name)
