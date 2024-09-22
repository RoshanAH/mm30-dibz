import dataclasses
from game.base_strategy import BaseStrategy
from game.plane import Plane, PlaneType

from strategy.base import Base
from strategy.balls import Balls
from strategy.amongus import Amongus
from strategy.bigballs import BigBalls
from strategy.ballsreal import BallsReal
from strategy.balls2 import Balls2
# The following is the heart of your bot. This controls what your bot does.
# Feel free to change the behavior to your heart's content.
# You can also add other files under the strategy/ folder and import them

class Strategy(BaseStrategy):
    bots = (Balls2(), Balls2())

    def select_planes(self) -> dict[PlaneType, int]:
        print(f"team: {self.team}")
        return self.bots[int(self.team)].select_planes()

    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        return self.bots[int(self.team)].steer_input(map_planes(self.team, planes))


def map_plane(team, plane: Plane) -> Plane:
    out = dataclasses.replace(plane)
    out.team = "friend" if team == plane.team else "enemy"
    if team == 0:
        out.angle = (out.angle + 180) % 360
        out.position = -1 * out.position
    return out



def map_planes(team, planes: dict[str, Plane]) -> dict[str, Plane]:
    return {id: map_plane(team, plane) for id, plane in planes.items()}
