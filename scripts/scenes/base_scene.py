import abc

import pygame


class BaseScene(abc.ABC):
    def __init__(self):
        """
        Executes when the Scene object is instantiated for the first time.
        """
        self.scene_manager = None

    @abc.abstractmethod
    def handle_events(self, events: list[pygame.event.Event]):
        """
        Allow the scene to process any or all of the events given.

        You can choose to pass, if no events need to be processed.
        :param events: a list of pygame events.
        :return: None
        """

        pass

    @abc.abstractmethod
    def update(self):
        """
        Allow the scene to do typical frame-by-frame computation and logic as needed.

        Physics calculations should go in here.
        :return: None
        """

        pass

    @abc.abstractmethod
    def render(self, screen: pygame.Surface):
        """
        Allow the scene to display what it needs to on the screen.

        You should consider beginning this function by getting the dimensions
        of the screen and/or by filling it with a color to use as the background.
        :param screen: the pygame Surface object that will be shown to the player
        :return: None
        """

        pass
