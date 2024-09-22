from game.plane_data import PlaneStats, PlaneType, Vector
from game.plane import Plane

from math import sin, cos, pi, copysign, atan2
from strategy.utils import degree_to_radius, plane_path_offset


def deg(r: float) -> float:
    return r / pi * 180


def rad(d: float) -> float:
    return d / 180 * pi

def angle(v: Vector) -> float:
    return deg(atan2(v.y, v.x))


# degrees
def rotate(v: Vector, theta: float) -> Vector:
    theta = rad(theta)
    return Vector(
        v.x * cos(theta) - v.y * sin(theta), v.x * sin(theta) + v.y * cos(theta)
    )


def angle_diff(a2: float, a1: float) -> float:
    return cc if abs(cc := (a2 - a1) % 360) < 180 else -copysign(360 - abs(cc), cc)


def follow_point(p: Plane, v: Vector) -> float:
    delta_pos = v - p.position
    target_heading = deg(atan2(delta_pos.y, delta_pos.x))
    turn_speed = p.stats.turn_speed
    delta_angle = angle_diff(target_heading, p.angle)
    return copysign(min(abs(delta_angle) / turn_speed, 1), delta_angle)


def next_pose(p: Plane, steer: float) -> tuple[Vector, float]:
    next_pos = plane_path_offset(1, steer, p)
    next_angle = p.angle + steer * p.stats.turn_speed
    return (next_pos, next_angle)


def dont_collide(p: Plane, steer: float, v: Vector, r=0.0) -> float:
    radius = degree_to_radius(p.stats.turn_speed, p.stats.speed)
    dir = Vector(cos(rad(p.angle)), sin(rad(p.angle)))
    left_turn = p.position + rotate(dir, 90) * radius
    right_turn = p.position + rotate(dir, -90) * radius

    next_pos = plane_path_offset(1, steer, p)
    next_angle = p.angle + steer * p.stats.turn_speed

    next_dir = Vector(cos(rad(next_angle)), sin(rad(next_angle)))
    next_left_turn = next_pos + rotate(next_dir, 90) * radius
    next_right_turn = next_pos + rotate(next_dir, -90) * radius

    def turn_ok(turn_center: Vector):
        return (turn_center - v).norm() > radius + r

    left_ok = turn_ok(left_turn)
    right_ok = turn_ok(right_turn)

    next_left_ok = turn_ok(next_left_turn)
    next_right_ok = turn_ok(next_right_turn)

    if next_left_ok or next_right_ok:
        return steer

    if left_ok:
        return 1
    if right_ok:
        return -1

    print("we are cooked")
    # we are cooked
    return 1 


def dont_die(p: Plane, steer: float) -> float:
    radius = degree_to_radius(p.stats.turn_speed, p.stats.speed)
    dir = Vector(cos(rad(p.angle)), sin(rad(p.angle)))
    left_turn = p.position + rotate(dir, 90) * radius
    right_turn = p.position + rotate(dir, -90) * radius

    next_pos = plane_path_offset(1, steer, p)
    next_angle = p.angle + steer * p.stats.turn_speed

    next_dir = Vector(cos(rad(next_angle)), sin(rad(next_angle)))
    next_left_turn = next_pos + rotate(next_dir, 90) * radius
    next_right_turn = next_pos + rotate(next_dir, -90) * radius

    def turn_ok(turn_center: Vector):
        return (
            turn_center.y + radius < 50
            and turn_center.y - radius > -50
            and turn_center.x + radius < 50
            and turn_center.x - radius > -50
        )

    left_ok = turn_ok(left_turn)
    right_ok = turn_ok(right_turn)

    next_left_ok = turn_ok(next_left_turn)
    next_right_ok = turn_ok(next_right_turn)

    if next_left_ok and next_right_ok:
        return steer

    # print("making corrections")

    if next_left_ok:
        return 1
    if next_right_ok:
        return -1

    if left_ok:
        return 1
    if right_ok:
        return -1

    print("we are cooked")

    # we are cooked
    return 1 


def hold_formation(
    planes: list[Plane], formation: list[Vector], pos: Vector, theta: float
) -> list[float]:
    formation = [rotate(v, theta) + pos for v in formation]
    return [follow_point(p, v) for p, v in zip(planes, formation)]


def dist(plane: Plane, v: Vector) -> float:
    delta_pos = v - plane.position
    delta_angle = angle_diff(atan2(delta_pos.y, delta_pos.x), plane.angle)
    return delta_pos.norm() ** 0.5 * abs(delta_angle) ** 2


def dist_euclid(plane: Plane, v: Vector) -> float:
    return (v - plane.position).norm()


class Fighter:
    turn = 0

    def engage(self, plane: Plane, enemy: Plane) -> float:

        defense_radius = enemy.stats.attack_range * 1.5
        delta_pos = enemy.position - plane.position
        distance = delta_pos.norm()

        # if abs(angle_diff(plane.angle, deg(atan2(delta_pos.y, delta_pos.x)))) > 90:
        #     return follow_point(plane, enemy.position)

        if distance > 30:
            return follow_point(plane, enemy.position)

        enemy_heading_diff = angle_diff(deg(atan2(-delta_pos.y, -delta_pos.x)), enemy.angle)
        enemy_dir = Vector(cos(rad(enemy.angle)), sin(rad(enemy.angle)))

        defense = (
            0 if abs(enemy_heading_diff) > 90 else cos(rad(abs(enemy_heading_diff)))
        )

        # left_blindspot  = enemy.position + rotate(enemy_dir, 90)  * defense * defense_radius * distance
        # right_blindspot = enemy.position + rotate(enemy_dir, -90) * defense * defense_radius * distance


        left_blindspot = (
            enemy.position + rotate(enemy_dir, 110) * defense * defense_radius
        )
        right_blindspot = (
            enemy.position + rotate(enemy_dir, -110) * defense * defense_radius
        )

        if dist(plane, left_blindspot) < dist(plane, right_blindspot):
            return follow_point(plane, left_blindspot)

        return follow_point(plane, right_blindspot)

    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {PlaneType.THUNDERBIRD: 5}

    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        response = dict()

        friends = {
            idx: plane for idx, plane in planes.items() if plane.team == "friend"
        }
        enemies = {idx: plane for idx, plane in planes.items() if plane.team == "enemy"}

        if self.turn < 10:
            for idx, plane in planes.items():
                response[idx] = -plane.position.x / 30
            self.turn += 1
            return response

        for idx, plane in friends.items():
            response[idx] = 0
            closest = None
            closest_dist = 0
            for e, enemy in enemies.items():
                distance = dist(plane, enemy.position)
                if (closest is None) or distance < closest_dist:
                    closest = e
                    closest_dist = distance
            if closest is not None:
                if enemies[closest].type == PlaneType.PIGEON:
                    response[idx] = follow_point(plane, enemies[closest].position)
                else:
                    response[idx] = self.engage(plane, enemies[closest])

            for enemy in enemies.values():
                # next_pos, next_angle = next_pose(plane, response[idx])
                # dir = Vector(cos(rad(plane.angle)), sin(rad(plane.angle)))
                # # cone = next_pos

                e_next_pos = next_pose(enemy, 0)[0]
                e_dir = Vector(cos(rad(enemy.angle)), sin(rad(enemy.angle)))
                e_cone = e_next_pos + e_dir * enemy.stats.attack_range * 0.6

                if (enemy.type != PlaneType.PIGEON):
                    response[idx] = dont_collide(plane, response[idx], e_cone, r=enemy.stats.attack_range * 0.5)
                    response[idx] = dont_collide(plane, response[idx], e_next_pos + e_dir * enemy.stats.attack_range * 0.5, r=enemy.stats.attack_range * 0.2)
                response[idx] = dont_collide(plane, response[idx], e_next_pos + e_dir * enemy.stats.attack_range * 0.2, r=enemy.stats.attack_range * 0.2 + 1)


            response[idx] = dont_die(plane, response[idx])

        self.turn += 1
        return response
