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
    planes: list[Plane], formation: list[Vector], pos: Vector, theta: float
) -> list[float]:
    formation = [rotate(v, theta) + pos for v in formation]
    return [follow_point(p, v) for p, v in zip(planes, formation)]


class PigeonGrid:

    grid_box = (-45, -20, 90, 25)
    turn = 0

    # class attacker:
    #     formation = [Vector(-10, 0), Vector(0, -10), Vector(10, 0)]
    #     def __init__(self, pigeons: list[str], planes: dict[str, Plane]):
    #         self.pigeons = pigeons
    #         self.pos = (planes[pigeons[0]].position + planes[pigeons[1]].position) * 0.5
    #         self.angle = 0
    #
    #     def attack(self, planes: dict[str, Plane], enemy: str):
    #         delta_pos = planes[enemy].position
    #         target_angle = deg(atan2(delta_pos.y, delta_pos.x))
    #         delta_angle = angle_diff(target_angle, self.angle)
    #         target_vel = (delta_pos / delta_pos.norm()) * 0.5 * (1 - abs(delta_angle) / 360)
    #         self.pos = self.pos + target_vel
    #         self.angle = target_angle

    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {PlaneType.PIGEON: 100}

    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        pigeons = {
            id: plane
            for id, plane in planes.items()
            if plane.team == "friend" and plane.type == PlaneType.PIGEON
        }
        enemies = {id: plane for id, plane in planes.items() if plane.team == "enemies"}

        self.grid_box = (-45, min(-35 + self.turn * 0.1, 40), 90, 5)
        pigeons_alive = len(pigeons.values())
        grid_space = (self.grid_box[2] * self.grid_box[3] / pigeons_alive) ** 0.5

        pigeon_formation = [
            Vector(
                self.grid_box[0] + (i % int(self.grid_box[2] / grid_space)) * grid_space + grid_space * 0.5,
                self.grid_box[1] - (i // int(self.grid_box[2] / grid_space)) * grid_space - grid_space * 0.5,
            )
            for i in range(pigeons_alive)
        ]

        pigeon_steer = hold_formation(list(pigeons.values()), pigeon_formation, Vector(0, 0), 0)
        pigeon_response = dict(zip(pigeons.keys(), pigeon_steer))

        to_attack: set[str] = set()
        for idx, enemy in enemies.items():
            enemy_pos = enemy.position
            if enemy_pos.y <= self.grid_box[1] and enemy_pos.y > self.grid_box[1] - self.grid_box[3] - 20:
                to_attack.add(idx)

        for idx, pigeon in pigeons.items():
            closest_dist = 0
            closest = None
            for e in to_attack:
                dist = (planes[e].position - pigeon.position).norm()
                if (closest is None or dist < closest_dist):
                    closest = e
                    closest_dist = dist
            if (closest is not None and closest_dist < 10):
                pigeon_response[idx] = follow_point(pigeon, planes[closest].position)

        self.turn += 1

        return pigeon_response
