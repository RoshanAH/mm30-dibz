from game.plane_data import PlaneStats, PlaneType, Vector
from game.plane import Plane

from math import sin, cos, pi, copysign, atan2


def deg(r: float) -> float:
    return r / pi * 180


def rad(d: float) -> float:
    return d / 180 * pi


# degrees
def rotate(v: Vector, theta: float) -> Vector:
    theta = rad(theta)
    return Vector(
        v.x * cos(theta) - v.y * sin(theta), v.x * sin(theta) + v.y * cos(theta)
    )


# degrees
# dont mod this pls
def angle_diff(a2: float, a1: float) -> float:
    a1 %= 360
    a2 %= 360
    cc = a2 - a1
    c = -copysign(360 - abs(cc), cc)
    if abs(cc) < 180:
        return cc
    return c


def follow_point(p: Plane, v: Vector) -> float:
    delta_pos = v - p.position
    target_heading = deg(atan2(delta_pos.y, delta_pos.x))
    turn_speed = p.stats.turn_speed
    delta_angle = angle_diff(target_heading, p.angle)
    # print(f"target pos: {v}")

    return copysign(min(abs(delta_angle) / turn_speed, 1), delta_angle)


def hold_formation(
    planes: list[Plane], formation: list[Vector], pos: Vector, heading: float
) -> list[float]:
    formation = [rotate(v, heading) + pos for v in formation]
    return [follow_point(p, v) for p, v in zip(planes, formation)]


class Formation:
    turn = 0

    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {
            PlaneType.PIGEON: 100,
            # PlaneType.SCRAPYARD_RESCUE: 10,
        }

    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        friends = {id: plane for id, plane in planes.items() if plane.team == "friend"}
        enemies = {id: plane for id, plane in planes.items() if plane.team == "enemies"}

        alive = len(friends.values())

        steer = hold_formation(
            list(friends.values()),
            [Vector(x * 90 / alive - 45, 0) for x in range(0, len(friends.values()))],
            Vector(0, 0),
            self.turn * 0.5,
        )
        response = dict(zip(friends.keys(), steer))
        # response = dict()
        # for id, plane in friends.items():
        #     response[id] = follow_point(plane, Vector(10, 30))
        self.turn += 1
        return response
