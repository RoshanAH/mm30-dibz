from game.plane import Plane, PlaneType
import random

class BigBalls():
    my_counter = 0
    my_steers = dict()
    my_target = dict()
    reached = dict()
    counter_since = dict()
    
    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {
            PlaneType.FLYING_FORTRESS: 3,
            PlaneType.SCRAPYARD_RESCUE: 1,
        }
    
    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        response = dict()

        for id, plane in planes.items():
            if plane.team == "enemy":
                continue
            if id not in self.my_steers:
                self.my_steers[id] = 0
            if max(abs(plane.position.x), abs(plane.position.y)) < 30:
                self.my_steers[id] = -1
            response[id] = self.my_steers[id]

        self.my_counter += 1

        # Return the steers
        return response