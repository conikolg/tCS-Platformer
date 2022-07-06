import pygame

from scripts.scenes.title_scene import TitleScene
from scripts.scenes.scene_manager import SceneManager


def main():
    # Control for pygame itself
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("theCoderSchool Frisco Coaches' Platformer Game")
    clock = pygame.time.Clock()
    running = True

    # Control for this game
    scene_manager = SceneManager(initial_scene=TitleScene())

    # Main game loop
    while running:
        # Catch the quit event before handing control to a scene
        if pygame.event.get(eventtype=pygame.QUIT):
            running = False
            return

        # Let the current scene do what it needs to do
        scene_manager.current_scene.handle_events(pygame.event.get())
        scene_manager.current_scene.update()
        scene_manager.current_scene.render(screen)

        # Update the screen, wait until it's time for the next frame
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
