from game.base_strategy import BaseStrategy
from game.plane import Plane, PlaneType
from strategy.pigeon import *
from strategy.anti_pigeon import *

# The following is the heart of your bot. This controls what your bot does.
# Feel free to change the behavior to your heart's content.
# You can also add other files under the strategy/ folder and import them

class Strategy(BaseStrategy):

    def __init__(self):
        self.bot0 = AntiPigeon("0")
        self.bot1 = AntiPigeon("1")

    def select_planes(self) -> dict[PlaneType, int]:
        if (self.team == "0"):
            return self.bot0.select_planes()
        else:
            return self.bot1.select_planes()

    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        if (self.team == "0"):
            return self.bot0.steer_input(planes)
        else:
            return self.bot1.steer_input(planes)
