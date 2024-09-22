from game.plane import Plane, PlaneType

class Pigeon():
    def select_planes(self) -> dict[PlaneType, int]:
        return {
            PlaneType.PIGEON: 99
        }

    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        return {}
