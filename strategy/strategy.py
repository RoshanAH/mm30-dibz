import random
from game.base_strategy import BaseStrategy
from game.plane import Plane, PlaneType

# The following is the heart of your bot. This controls what your bot does.
# Feel free to change the behavior to your heart's content.
# You can also add other files under the strategy/ folder and import them

class Strategy(BaseStrategy):
    # BaseStrategy provides self.team, so you use self.team to see what team you are on

    # You can define whatever variables you want here
    my_counter = 0
    my_steers = dict()
    
    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {
            PlaneType.PIGEON: 100,
        }
    
    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        response = dict()

        for id, plane in planes.items():
            if plane.team != self.team:
                continue
            
            boundary = 47.5
            if plane.position.y > boundary or plane.position.y < -boundary or plane.position.x > boundary or plane.position.x < -boundary:
                self.my_steers[id] = -1
            else:
                self.my_steers[id] = random.random() * 2 - 1
            response[id] = self.my_steers[id]

        self.my_counter += 1

        # Return the steers
        return response
