from game.plane import Plane, PlaneType
import math
class AntiPigeon():

    def __init__(self, team):
        self.team = team
    def select_planes(self) -> dict[PlaneType, int]:
        return {
            PlaneType.THUNDERBIRD: 5
        }

    def find_turn_to(self, heading, from_pos, to_pos):
        rad_angle = math.atan2(to_pos[1] - from_pos[1], to_pos[0] - from_pos[0])
        angle = rad_angle * 180 / math.pi
        # print(angle)
        if heading > 180:
            heading -= 360
        a = angle - heading
        if abs(a) > 180:
            if a < 0:
                a = -(180 - abs(a))
            else:
                a = 180 - abs(a)
        return a

    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        ret_dict = {} # [id,
        #get frens enmy dics
        frens = {}
        enmys = {}
        for id, plane in planes.items():
            if (plane.team == self.team):
                frens[id] = plane
            else:
                enmys[id] = plane
        #target nearest Pigeon
        for f_id, f_plane in frens:
            #find nearest Pigeon
            nearest = 150
            nearest_id = None
            fren_pos = (f_plane.position.x, f_plane.position.y)
            for e_id, e_plane in enmys:
                enmy_pos = (e_plane.position.x, e_plane.position.y)
                if math.dist(fren_pos,enmy_pos) < nearest:
                    nearest = math.dist(fren_pos, enmy_pos)
                    nearest_id = e_id

            enmy_pos = (enmys[nearest_id].position.x, enmys[nearest_id].position.y)
            turn = self.find_turn_to(f_plane.angle,fren_pos,enmy_pos)
            if plane.PlaneStats.turn_speed > abs(turn):
                if turn > 0:
                    ret_dict[f_id] = 1
                if turn > 0:
                    ret_dict[f_id] = 1

        return ret_dict