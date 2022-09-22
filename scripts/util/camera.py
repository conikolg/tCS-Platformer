import abc

import pygame


class CameraBehavior(abc.ABC):
    def __init__(self, target):
        self.target = target
        self.camera = None

    @abc.abstractmethod
    def scroll(self):
        pass


class FollowTarget(CameraBehavior):
    def __init__(self, target):
        """
        Scroll behavior ensures that the offsets are calculated relative to only the target's position.

        :param target: a Sprite for the camera to focus on.
        """

        CameraBehavior.__init__(self, target)

    def scroll(self):
        self.camera.offset.x = self.target.body.position.x + self.camera.constant.x
        self.camera.offset.y = -self.target.body.position.y + self.camera.constant.y


class BoundedFollowTarget(CameraBehavior):
    def __init__(self, target, horizontal_limits: tuple, vertical_limits: tuple):
        """
        Scroll behavior ensures that the offsets are calculated relative to the target's position, but
        horizontal scrolling cannot move past a lower and/or upper limit.

        :param target: a Sprite for the camera to focus on.
        :param horizontal_limits: a tuple containing the lower and upper limits x-coordinates of the camera's viewport.
        :param vertical_limits: a tuple containing the lower and upper limits y-coordinates of the camera's viewport.
        """

        CameraBehavior.__init__(self, target)
        self.horizontal_limits = horizontal_limits
        self.vertical_limits = vertical_limits

    # Add dead zone for player x and y?
    def scroll(self):
        self.camera.offset.x = self.target.body.position.x + self.camera.constant.x
        self.camera.offset.y = -self.target.body.position.y + self.camera.constant.y

        self.camera.offset.x = max(self.horizontal_limits[0], self.camera.offset.x)
        self.camera.offset.x = min(self.camera.offset.x, self.horizontal_limits[1] - self.camera.DISPLAY_W)

        self.camera.offset.y = max(self.vertical_limits[0], self.camera.offset.y)
        self.camera.offset.y = min(self.camera.offset.y, self.vertical_limits[1] - self.camera.DISPLAY_H)


class AutoScroll(CameraBehavior):
    def __init__(self, speed: int = 1):
        """
        Scroll behavior slowly pans the camera, with no target to focus on.

        :param speed: the number of pixels, per scroll invocation (which should be per frame), to shift the camera
        """

        CameraBehavior.__init__(self, None)
        self.speed: int = speed

    def scroll(self):
        self.camera.offset.x += self.speed


class Camera:
    def __init__(self, behavior: CameraBehavior = None, screen_dimensions: tuple = None, constant=None):
        """
        Creates a camera to handle the math and offset calculation needed when focused on a particular target.

        :param behavior: a CameraBehavior object that implements how the camera will be calculating offsets.
        :param screen_dimensions: a tuple defining how large the screen is.
        :param constant: a tuple or Vector2 to add an offset relative to the target of the camera. Useful if the
        target is not supposed to appear at the top-left of the screen.
        """

        self.offset = pygame.math.Vector2(0, 0)
        self.offset_float = pygame.math.Vector2(0, 0)
        self.constant = pygame.math.Vector2(0, 0) if constant is None else constant

        self.DISPLAY_W, self.DISPLAY_H = (1280, 720) if screen_dimensions is None else screen_dimensions
        self.behavior = None
        if behavior is not None:
            self.set_behavior(behavior)

    def set_behavior(self, behavior: CameraBehavior):
        self.behavior = behavior
        self.behavior.camera = self

    def scroll(self):
        if self.behavior is None:
            raise Exception(f"No scroll behavior defined for camera.")

        self.behavior.scroll()
