from game.plane import Plane, PlaneType
import math
import random
from strategy.utils import *



class BetterPigeon():
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

    my_counter = 0
    my_steers = dict()
    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {
            PlaneType.PIGEON: 100,
        }

    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        response = dict()

        frens = {}
        enmys = {}
        for id, plane in planes.items():
            if (plane.team == "friend"):
                frens[id] = plane
            else:
                enmys[id] = plane

        for id, plane in frens.items():
            boundary = 47.5
            if plane.position.y > boundary or plane.position.y < -boundary or plane.position.x > boundary or plane.position.x < -boundary:
                self.my_steers[id] = -1
            else:
                self.my_steers[id] = random.random() * 2 - 1
                minalr = 150
                fren_pos = (plane.position.x, plane.position.y)
                for e_id, e_plane in enmys.items():
                    enmy_pos = (enmys[e_id].position.x, enmys[e_id].position.y)
                    angle = self.find_turn_to(plane.angle, fren_pos, enmy_pos)

                    turn = self.find_turn_to(plane.angle, fren_pos, enmy_pos)
                    if abs(angle + 180 - enmys[e_id].angle > 90) and turn < 60:
                        if math.dist(fren_pos,enmy_pos) < minalr:
                            minalr = math.dist(fren_pos, enmy_pos)
                            if plane.stats.turn_speed < abs(turn):
                                if turn > 0:
                                    response[id] = 1
                                if turn <= 0:
                                    response[id] = -1
                            else:
                                response[id] = turn / plane.stats.turn_speed
            response[id] = self.my_steers[id]

        self.my_counter += 1

        # Return the steers
        return response


class AntiPigeon:
    counter = 0
    def select_planes(self) -> dict[PlaneType, int]:
        return {
            PlaneType.SCRAPYARD_RESCUE: 2,
            PlaneType.PIGEON: 80
        }

    def find_turn_to(self, heading, from_pos, to_pos):
        rad_angle = math.atan2(to_pos[1] - from_pos[1], to_pos[0] - from_pos[0])
        angle = rad_angle * 180 / math.pi
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
            if (plane.team == "friend"):
                frens[id] = plane
            else:
                enmys[id] = plane
        for f_id, f_plane in frens.items():
            nearest = 150
            nearest_id = None
            fren_pos = (f_plane.position.x, f_plane.position.y)
            for e_id, e_plane in enmys.items():
                enmy_pos = (e_plane.position.x, e_plane.position.y)
                if math.dist(fren_pos,enmy_pos) < nearest:
                    nearest = math.dist(fren_pos, enmy_pos)
                    nearest_id = e_id

            enmy_pos = (enmys[nearest_id].position.x, enmys[nearest_id].position.y)
            if math.dist(enmy_pos, fren_pos) < 17 or f_plane.type.PIGEON:
                turn = self.find_turn_to(f_plane.angle,fren_pos,enmy_pos)
                if f_plane.type.SCRAPYARD_RESCUE and self.counter < 100:
                    turn = self.find_turn_to(f_plane.angle, fren_pos, (0,20))
                if f_plane.stats.turn_speed < abs(turn):
                    if turn > 0:
                        ret_dict[f_id] = random.random()
                    if turn < 0:
                        ret_dict[f_id] = -random.random()
                else:
                    ret_dict[f_id] = turn/f_plane.stats.turn_speed

            boundary = 45.5
            if f_plane.position.y > boundary or f_plane.position.y < -boundary or f_plane.position.x > boundary or f_plane.position.x < -boundary:
                ret_dict[f_id] = -1


        self.counter += 1
        return ret_dict


class Pigeon():
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
            if plane.team != "friend":
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