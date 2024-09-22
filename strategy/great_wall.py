from math import copysign
from strategy.utils import degree_to_radius
from game.plane import Plane, PlaneType, Vector

class GreatWall:
    previously_alive = {}
    converging = {}
    turning_around = 0

    @staticmethod
    def select_planes(): return { PlaneType.PIGEON: 100 }

    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:

        pigeons = {int(id_): plane for id_, plane in planes.items() if plane.team == "friend" and plane.type == PlaneType.PIGEON}

        mean_y = round(sum([plane.position.y for plane in pigeons.values()]) / len(pigeons), 3)
        mean_angle = sum([abs(180 - plane.angle) for plane in pigeons.values()]) / len(pigeons)
        print(f"{mean_angle=}, {mean_y=}")
        
        enemy_planes = dict(sorted({id_: plane for id_, plane in planes.items() if plane.team == "enemy"}.items(), key=lambda x: x[1].position.y - mean_y))

        if not self.turning_around:
            if (mean_angle == 90 and mean_y > 47.5) or (mean_angle == 270 and mean_y < -47.5):
                self.turning_around += 6

        if self.turning_around > 0:
            self.turning_around -= 1
            return {str(id_): copysign(1, pigeon.position.x) for id_, pigeon in pigeons.items()}
        
        
        dead = {id_: plane for id_, plane in self.previously_alive.items() if id_ not in pigeons}
        # TODO: Handle converging upon killed pigeons
        

        self.previously_alive = pigeons
        dummy_responses = {str(id_): 0. for id_ in pigeons}
        return dummy_responses
