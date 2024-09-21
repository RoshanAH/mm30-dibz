from game.plane import Plane, PlaneType

class Pigeon:
    def __init__(team):
        self.team = team;
    def select_planes(self) -> dict[PlaneType, int]:
        return {}

    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        return {}
