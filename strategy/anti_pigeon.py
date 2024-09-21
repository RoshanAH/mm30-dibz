from game.plane import Plane, PlaneType

class AntiPigeon:

    def __init__(self, team):
        self.team = team;

    def select_planes(self) -> dict[PlaneType, int]:
        return {}

    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        return {}
