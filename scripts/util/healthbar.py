import pygame


class Healthbar:
    def __init__(self, minimum_health: int = 0, maximum_health: int = 100, initial_health: int = None):
        """
        Creates a healthbar, which ensures current health will always be within an intended minimum
        and maximum value, and provides a flexible Surface for rendering purposes.

        :param minimum_health: The minimum possible health value.
        :param maximum_health: The maximum possible health value.
        :param initial_health: The amount of health to begin with. If None, defaults to maximum_health.
        """

        self._minimum_health: int = minimum_health
        self._maximum_health: int = maximum_health
        self._current_health: int = self._maximum_health if initial_health is None else initial_health

        if self._maximum_health <= self._minimum_health:
            raise Exception("Maximum health must be greater than minimum health.")
        if not (self._minimum_health <= self._current_health <= self._maximum_health):
            raise Exception("Initial health must be between minimum and maximum health values.")

    @property
    def health(self):
        return self._current_health

    @health.setter
    def health(self, new_health):
        if self._current_health == new_health:
            return

        # Clamp health value between max and min value
        new_health = max(self._minimum_health, new_health)
        new_health = min(self._maximum_health, new_health)
        self._current_health = new_health

    def render(self, width: int, height: int, outline_width: int = 3) -> pygame.Surface:
        """
        Returns an image of the healthbar, with a black outline and a left-aligned green portion
        representing current remaining health.

        :param width: How wide in pixels the healthbar should be.
        :param height: How tall in pixels the healthbar should be.
        :param outline_width: How many pixels should be used for the outline.
        :return: a pygame.Surface of the specified width and height.
        """

        img = pygame.Surface((width, height))

        # Fill in red background
        pygame.draw.rect(surface=img, color=(210, 40, 0), rect=(
            outline_width, outline_width, (width - outline_width * 2), (height - outline_width * 2)
        ))

        # Calculate how much should be green
        green_percent = (self._current_health - self._minimum_health) / (self._maximum_health - self._minimum_health)
        pygame.draw.rect(surface=img, color=(100, 230, 0), rect=(
            outline_width, outline_width, (width - outline_width * 2) * green_percent, (height - outline_width * 2)
        ))

        return img
