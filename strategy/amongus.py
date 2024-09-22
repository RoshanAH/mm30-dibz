from game.plane import Plane, PlaneType
import random

class Amongus():
    my_counter = 0
    my_steers = dict()
    my_target = dict()
    reached = dict()
    counter_since = dict()
    
    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {
            PlaneType.FLYING_FORTRESS: 3,
        }
    
    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        response = dict()

        for id, plane in planes.items():
            if plane.team == "enemy":
                continue
            if id not in self.my_steers:
                self.my_steers[id] = -1
                self.my_target[id] = 45
                self.reached[id] = False
                self.counter_since[id] = 0
            else:
                tolerance = 6
                boundary = 45
                counter_tol = 15
                if plane.angle > self.my_target[id] + tolerance:
                    self.my_steers[id] = -1
                    self.counter_since[id] += 1
                elif plane.angle < self.my_target[id] - tolerance:
                    self.my_steers[id] = 1
                    self.counter_since[id] += 1
                else:
                    self.my_steers[id] = 0
                    self.reached[id] = True
                    self.counter_since[id] += 1
                if max(abs(plane.position.x), abs(plane.position.y)) > boundary and self.reached[id] and self.counter_since[id] > counter_tol:
                    self.my_target[id] = (self.my_target[id] + 90)
                    self.reached[id] = False
                    self.counter_since[id] = 0
            response[id] = self.my_steers[id]

        self.my_counter += 1

        # Return the steers
        return response