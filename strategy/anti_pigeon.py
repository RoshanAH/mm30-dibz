from game.plane import Plane, PlaneType
import math
import random
from strategy.utils import *


class UnoVUno:
    counter = 0

    def select_planes(self) -> dict[PlaneType, int]:
        return {
            PlaneType.THUNDERBIRD: 2
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
        ret_dict = {}  # [id,
        # get frens enmy dics
        frens = {}
        enmys = {}
        for id, plane in planes.items():
            if (plane.team == "friend"):
                frens[id] = plane
            else:
                enmys[id] = plane
        for f_id, f_plane in frens.items():
            for e_id, e_plane in enmys.items():
                if e_plane.type == PlaneType.FLYING_FORTRESS:
                    fren_pos = (f_plane.position.x, f_plane.position.y)
                    enmy_pos = (enmys[e_id].position.x, enmys[e_id].position.y)

                    ret_dict[f_id] = 0

        return ret_dict


class notBetterPigeon():
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

        frens = {id: plane for id, plane in planes.items() if plane.team == "friend"}
        enmys = {id: plane for id, plane in planes.items() if plane.team != "friend"}

        boundary = 47.5
        for id, plane in frens.items():

            if (plane.position.y > boundary or plane.position.y < -boundary or
                    plane.position.x > boundary or plane.position.x < -boundary):
                self.my_steers[id] = -1
            else:
                self.my_steers[id] = random.random() * 2 - 1
                minalr = 150
                fren_pos = (plane.position.x, plane.position.y)

                for e_id, e_plane in enmys.items():
                    enmy_pos = (e_plane.position.x, e_plane.position.y)
                    turn = self.find_turn_to(plane.angle, fren_pos, enmy_pos)

                    newang = plane.angle if plane.angle <= 180 else plane.angle - 360
                    newang2 = e_plane.angle if e_plane.angle <= 180 else e_plane.angle - 360

                    if abs(turn + newang - newang2) > 60 and abs(turn) < 30:
                        distance_to_enemy = math.dist(fren_pos, enmy_pos)
                        if distance_to_enemy < minalr:
                            minalr = distance_to_enemy
                            self.my_steers[id] = turn

                nearest_f = 150
                nearest_f_id = None
                for f2_id, f2_plane in frens.items():
                    if f2_id != id:
                        fren2_pos = (f2_plane.position.x, f2_plane.position.y)
                        distance_to_fren = math.dist(fren_pos, fren2_pos)
                        if distance_to_fren < nearest_f:
                            nearest_f = distance_to_fren
                            nearest_f_id = f2_id

                if nearest_f_id:
                    near_f_direc = self.find_turn_to(plane.angle, fren_pos, fren2_pos)
                    correction = 50 / (nearest_f + 0.1)
                    if near_f_direc > 0:
                        self.my_steers[id] -= correction
                    else:
                        self.my_steers[id] += correction
            response[id] = min(max(self.my_steers[id] / plane.stats.turn_speed, -1), 1)
            response[id] = self.my_steers[id]

        # Increment the counter
        self.my_counter += 1

        return response


class AntiPigeon:
    counter = 0

    def select_planes(self) -> dict[PlaneType, int]:
        return {
            PlaneType.SCRAPYARD_RESCUE: 4,
            PlaneType.PIGEON: 2
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
        ret_dict = {}  # [id,
        # get frens enmy dics
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
                if math.dist(fren_pos, enmy_pos) < nearest:
                    nearest = math.dist(fren_pos, enmy_pos)
                    nearest_id = e_id

            enmy_pos = (enmys[nearest_id].position.x, enmys[nearest_id].position.y)
            if math.dist(enmy_pos, fren_pos) < 17 or f_plane.type == PlaneType.PIGEON:
                turn = self.find_turn_to(f_plane.angle, fren_pos, enmy_pos)
                if f_plane.stats.turn_speed < abs(turn):
                    if turn > 0:
                        ret_dict[f_id] = 1
                    if turn < 0:
                        ret_dict[f_id] = -1
                else:
                    ret_dict[f_id] = turn / f_plane.stats.turn_speed

            boundary = 45.5
            if f_plane.position.y > boundary or f_plane.position.y < -boundary or f_plane.position.x > boundary or f_plane.position.x < -boundary:
                ret_dict[f_id] = -1
            if f_plane.type == PlaneType.SCRAPYARD_RESCUE and self.counter < 5:
                ret_dict[f_id] = 0
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


class BigBalls:
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
