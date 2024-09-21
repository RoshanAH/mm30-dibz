from game.base_strategy import BaseStrategy
from game.plane import Plane, PlaneType
from strategy.pigeon import *
from strategy.anti_pigeon import *

# The following is the heart of your bot. This controls what your bot does.
# Feel free to change the behavior to your heart's content.
# You can also add other files under the strategy/ folder and import them

class Strategy(BaseStrategy):

    bot0 = Pigeon()
    bot1 = AntiPigeon()

    def select_planes(self) -> dict[PlaneType, int]:
        if (self.team == 0):
            return bot0.select_planes()
        else:
            return bot1.select_planes()

    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        if (self.team == 0):
            return bot0.steer_input(planes)
        else:
            return bot1.select_planes(planes)
