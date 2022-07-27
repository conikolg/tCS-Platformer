from scripts.enemy.basic_enemy import BasicEnemy
from scripts.util.platform import Platform


class Slime(BasicEnemy):
    def __init__(self, platform: Platform, horizontal_offset: int = 0):
        """
        Creates a slime enemy at a certain position that patrols on a platform.

        :param platform: the Platform on which this enemy will walk back and forth
        :param horizontal_offset: how far from the left edge of the platform the enemy will begin.
        """

        super().__init__("slime", platform, horizontal_offset=horizontal_offset,
                         hitbox_h_percent=80, hitbox_offset_y=10)

    def __str__(self):
        return super().__str__()
