from game.plane_data import PlaneStats, PlaneType, Vector
from game.plane import Plane

from math import sin, cos, pi, copysign, atan2, ceil


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
    planes: list[Plane], formation: list[Vector], pos: Vector, theta: float
) -> list[float]:
    formation = [rotate(v, theta) + pos for v in formation]
    return [follow_point(p, v) for p, v in zip(planes, formation)]


# controlls a plane at a specific velocity
def throttle(plane: Plane, vel: Vector, turn) -> float:
    target_speed = vel.norm()
    target_heading = deg(atan2(vel.y, vel.x))
    ts_proportion = min(max(0, target_speed / plane.stats.speed), 1)
    def find_cross_angle(p):
        return -74.54*p**6 + 212.9*p**5 - 232.1*p**4 + 117.3*p**3 - 25.85*p**2 - 0.843*p + 3.14

    cross_angle = deg(find_cross_angle(ts_proportion))
    delta_angle = angle_diff(target_heading, plane.angle)

    period = cross_angle * 4 / plane.stats.turn_speed
    if abs(delta_angle) > cross_angle or round(period) == 0:
        return copysign(min(abs(delta_angle) / plane.stats.turn_speed, 1), delta_angle)

    i = turn % round(period)

    return -1 if i < period * 0.5 else 1

def hold_moving_formation(
    planes: list[Plane],
    formation: list[Vector],
    pos: Vector,
    vel: Vector,
    theta: float,
    alpha: float,
    turn: int, # for cycle timing
) -> tuple[list[float], float]:
    vel *= 1 / vel.norm()
    pos_formation = [rotate(v, theta) + pos for v in formation]
    vel_formation = [vel + rad(alpha) * rotate(v, 90 + theta) for v in formation]

    err = sum((plane.position - v).norm() for plane, v in zip(planes, pos_formation))

 self.x - o.x   return ([
        throttle(plane, vel + (pos - plane.position) * 0.1, turn)
        for plane, pos, vel in zip(planes, pos_formation, vel_formation)
    ], err)

class Roshan:
    turn = 0

    squad_pos = Vector(0, 0)
    squad_vel = Vector(0, 0.3)
    squad_theta = 0
    squad_alpha = 1
    squad_err = 0

    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {
            PlaneType.PIGEON: 2,
        }

    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        friends = {id: plane for id, plane in planes.items() if plane.team == "friend"}
        enemies = {id: plane for id, plane in planes.items() if plane.team == "enemies"}

        steer, self.squad_err = hold_moving_formation(
            list(friends.values()),
            [Vector(-4, 0), Vector(4, 0)],
            self.squad_pos,
            self.squad_vel,
            self.squad_theta,
            self.squad_alpha,
            self.turn,
        )

        print(self.squad_err)
        self.squad_vel = Vector(0, 0.3) - (self.squad_err * 0.02 * Vector(0,0.3) * 0.3)
        self.squad_pos += self.squad_vel
        self.squad_theta += self.squad_alpha

        response = dict(zip(friends.keys(), steer))

        self.turn += 1
        return response
