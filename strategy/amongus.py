from game.plane import Plane, PlaneType
import random

class Amongus():
    my_counter = 0
    my_steers = dict()
    
    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {
            PlaneType.STANDARD: 1,
            PlaneType.FLYING_FORTRESS: 1,
            PlaneType.THUNDERBIRD: 1,
            PlaneType.SCRAPYARD_RESCUE: 1,
            PlaneType.PIGEON: 10,
        }
    
    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        # Define a dictionary to hold our response
        response = dict()

        # For each plane
        for id, plane in planes.items():
            # id is the unique id of the plane, plane is a Plane object

            # We can only control our own planes
            if plane.team == "enemy":
                continue

            # If we're within the first 5 turns, just set the steer to 0
            if self.my_counter < 5:
                response[id] = 0
            else:
                # If we haven't initialized steers yet, generate a random one for this plane
                if id not in self.my_steers:
                    self.my_steers[id] = random.random() * 2 - 1

                # Set the steer for this plane to our previously decided steer
                response[id] = self.my_steers[id]
            self.my_counter += 1
        return response
