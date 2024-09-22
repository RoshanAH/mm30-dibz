from random import random
from game.plane import Plane, PlaneType, Vector
from math import sin, cos, asin, atan2, copysign, degrees, radians
from strategy.utils import degree_to_radius, steer_crashes_plane

def cross(a: Vector, b: Vector) -> float:
    return a.x * b.y - a.y * b.x

def angle(a: Vector) -> float:
    return degrees(atan2(a.y, a.x)) % 360

def angle_diff(a2: float, a1: float) -> float:
    a1 %= 360
    a2 %= 360
    cc = a2 - a1
    c  = -copysign(360 - abs(cc), cc)
    if abs(cc) < 180:
        return cc
    return c

def steer_away_from_wall(plane: Plane) -> float:
    # Find the closest wall
    walls = [
        Vector(50, plane.position.y),
        Vector(-50, plane.position.y),
        Vector(plane.position.x, 50),
        Vector(plane.position.x, -50),
    ]
    closest_wall = min(walls, key=lambda wall: (wall - plane.position).norm())
    return steer_away_from_point(plane, closest_wall)

def steer_away_from_point(plane: Plane, point: Vector) -> float:
    # Find the angle to the point
    angle_to_point = angle(point - plane.position)
    # Find the angle difference
    delta_theta = angle_diff(angle_to_point, plane.angle)
    # Find the maximum angle you can turn
    # Return the steer
    return -copysign(1, delta_theta)

def steer_causes_crash(steer: float, plane: Plane, turns_ahead: int = 1) -> bool:
    if turns_ahead <= 1:
        return steer_crashes_plane(steer, plane)
    next_plane = plane
    next_plane.angle += steer * next_plane.stats.turn_speed
    next_plane.position += next_plane.stats.speed * Vector(cos(radians(next_plane.angle)), sin(radians(next_plane.angle)))
    return steer_causes_crash(steer, next_plane, turns_ahead - 1)


class Skibidi:
    previous_targets: dict[str, tuple[str, int]] = {}
    stagger_turns = 0
    
    def select_planes(self) -> dict[PlaneType, int]:
        return {
            PlaneType.STANDARD: 1,
            PlaneType.THUNDERBIRD: 1,
            PlaneType.FLYING_FORTRESS: 1,
            PlaneType.PIGEON: 30,
        }

    def steer_to_point(self, plane: Plane, target: Vector) -> float:
        dist_from_target = target - plane.position
        # print("distance from target", dist_from_target.norm())
        delta_theta = angle_diff(angle(dist_from_target), plane.angle)
        max_theta = plane.stats.turn_speed
        return max(-1, min(1, delta_theta / max_theta))
    
    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        response = {}
        my_planes = {id: plane for id, plane in planes.items() if plane.team == "friend"}
        hunters = {id: plane for id, plane in my_planes.items() if plane.type in [PlaneType.STANDARD, PlaneType.THUNDERBIRD]}
        pigeons = {id: plane for id, plane in my_planes.items() if plane.type == PlaneType.PIGEON}

        not_my_planes = {id: plane for id, plane in planes.items() if plane.team == "enemy"}
        if self.stagger_turns > 0:
            self.stagger_turns -= 1

        hunted_targets = {}
        for id, plane in hunters.items():
            if self.stagger_turns > 0:
                response[id] = copysign(1, plane.position.x * plane.position.y) * min(1, abs(plane.position.x/5))
                continue

            def distance_heuristic(id):
                return (diff := not_my_planes[id].position - plane.position).norm() * (abs(angle_diff(angle(diff), plane.angle))**(1/3))

            closest_enemies = sorted(not_my_planes, key=distance_heuristic)

            if id not in self.previous_targets:
                self.previous_targets[id] = (closest_enemies[0], 0)

            previous_target, turns_followed = self.previous_targets[id]

            target_idx = 0

            if turns_followed > 100 and len(closest_enemies) > 1:
                target_idx = 1
                turns_followed = 0

            warned = False
            for id_ in closest_enemies[target_idx:]:
                enemy = not_my_planes[id_]
                # future_enemy_position = enemy.position + enemy.stats.speed * Vector(cos(radians(enemy.angle)), sin(radians(enemy.angle)))
                # averaged_enemy_position = (enemy.position + future_enemy_position)
                # averaged_enemy_position = Vector(averaged_enemy_position.x / 2, averaged_enemy_position.y / 2)
                steer = self.steer_to_point(plane, enemy.position)
                if steer_causes_crash(steer, plane, 1):
                    if not warned:
                        print("WARN!", end="")
                        warned = True
                    else:
                        print("!", end="")
                    continue
                response[id] = steer
                hunted_targets[id] = id_
                if warned:
                    print()
                if id_ != previous_target:
                    self.previous_targets[id] = (id_, 1)
                else:
                    self.previous_targets[id] = (id_, turns_followed + 1)
                break
            
            if id not in response:
                print("REDIRECTING")
                steer = steer_away_from_wall(plane)
                # if steer_crashes_plane(steer, plane):
                    # print("WARN?",)
                    # response[id] = -steer
                    # continue
                response[id] = steer
                continue

            # TODO: detect whether other planes will hit you
            my_pos_next_turn = plane.position + plane.stats.speed * Vector(cos(radians(plane.angle)), sin(radians(plane.angle)))
            turned_away = False
            for id_ in closest_enemies[:5]:
                enemy = not_my_planes[id_]
                enemy_pos_next_turn = enemy.position + enemy.stats.speed * Vector(cos(radians(enemy.angle)), sin(radians(enemy.angle)))
                enemy_cone_pos = enemy.position + enemy.stats.attack_range * Vector(cos(radians(enemy.angle)), sin(radians(enemy.angle))) * 0.75
                if (enemy_pos_next_turn - my_pos_next_turn).norm() < 4 or (enemy_cone_pos - my_pos_next_turn).norm() < 4:
                    response[id] = steer_away_from_point(plane, enemy_pos_next_turn)
                    turned_away = True
                    break

            if steer_crashes_plane(response[id], plane):
                print("don't kill yourself",)
                response[id] *= -1
                if id in hunted_targets:
                    del hunted_targets[id]

        return response

