import dataclasses
from random import random
from game.plane import Plane, PlaneType, Vector
from math import sin, cos, asin, atan2, copysign, degrees, radians, pi
from strategy.utils import degree_to_radius, steer_crashes_plane

def cross(a: Vector, b: Vector) -> float:
    return a.x * b.y - a.y * b.x

def angle(a: Vector) -> float:
    return degrees(atan2(a.y, a.x)) % 360

def angle_diff(a2: float, a1: float) -> float:
    return cc if abs(cc := (a2 % 360) - (a1 % 360)) < 180 else copysign(abs(cc) - 360, cc)

def steer_away_from_wall(plane: Plane) -> float:
    # Find the closest wall
    walls = [
        Vector(50, plane.position.y),
        Vector(-50, plane.position.y),
        Vector(plane.position.x, 50),
        Vector(plane.position.x, -50),
    ]
    return steer_away_from_point(plane, min(walls, key=lambda wall: (wall - plane.position).norm()))

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
    next_plane = dataclasses.replace(plane)
    next_plane.angle += steer * next_plane.stats.turn_speed
    next_plane.position += next_plane.stats.speed * Vector(cos(radians(next_plane.angle)), sin(radians(next_plane.angle)))
    return steer_causes_crash(steer, next_plane, turns_ahead - 1)

special_message = "Beyblade beyblade let it rip! Let's fight, an epic battle! Face off and spin the metal! No time for doubt now, no place for backing down! Beyblade beyblade let it rip! Beyblade beyblade let it rip! Spin out the blade now, bring on the power! Right to the top, yeah, we're never givin' up! Here comes, here comes, METAL FUSION! Let's go Beyblade, let it rip! Metal Fusion, let it rip! Beyblade beyblade let it rip! This is it, get a grip, let it rip!"

class Skibidi:
    def select_planes(self) -> dict[PlaneType, int]:
        return {
            PlaneType.STANDARD: 1,
            PlaneType.FLYING_FORTRESS: 1,
            PlaneType.THUNDERBIRD: 1,
            PlaneType.PIGEON: 30,
        }

    def steer_to_point(self, plane: Plane, target: Vector) -> float:
        return max(-1, min(1, angle_diff(angle(target - plane.position), plane.angle) / plane.stats.turn_speed))
    
    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        response = {}
        my_planes = {id: plane for id, plane in planes.items() if plane.team == "friend"}
        hunters = {id: plane for id, plane in my_planes.items() if plane.type in [PlaneType.STANDARD, PlaneType.THUNDERBIRD, PlaneType.FLYING_FORTRESS]}
        pigeons = {id: plane for id, plane in my_planes.items() if plane.type == PlaneType.PIGEON}

        not_my_planes = {id: plane for id, plane in planes.items() if plane.team == "enemy"}

        hunted_targets = {}
        for id, plane in hunters.items():
            def distance_heuristic(id):
                dist = (diff := not_my_planes[id].position - plane.position).norm() ** 2
                if plane.type == PlaneType.STANDARD:
                    dist *= abs(angle_diff(angle(diff), plane.angle)) ** (1/4)
                elif plane.type == PlaneType.THUNDERBIRD:
                    dist *= abs(angle_diff(angle(diff), plane.angle)) ** (1/4)
                elif plane.type == PlaneType.FLYING_FORTRESS:
                    dist *= abs(angle_diff(angle(diff), plane.angle)) ** .25
                return dist

            closest_enemies = sorted([id_ for id_ in not_my_planes if id_ not in hunted_targets], key=distance_heuristic)

            # if id not in self.previous_targets:
                # self.previous_targets[id] = (closest_enemies[0], 0)

            # previous_target, turns_followed = self.previous_targets[id]

            warned = False
            for id_ in closest_enemies:
                if len(closest_enemies) == 1:
                    enemy = not_my_planes[id_]
                    steer = self.steer_to_point(plane, enemy.position)
                    response[id] = steer
                    hunted_targets[id] = id_
                    break

                if id_ in hunted_targets.values():
                    continue
                enemy = not_my_planes[id_]
                # future_enemy_position = enemy.position + enemy.stats.speed * Vector(cos(radians(enemy.angle)), sin(radians(enemy.angle)))
                # averaged_enemy_position = (enemy.position + future_enemy_position)
                # averaged_enemy_position = Vector(averaged_enemy_position.x / 2, averaged_enemy_position.y / 2)
                steer = self.steer_to_point(plane, enemy.position)
                if steer_causes_crash(steer, plane, 3):
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
                # if id_ != previous_target:
                    # self.previous_targets[id] = (id_, 1)
                # else:
                    # self.previous_targets[id] = (id_, turns_followed + 1)
                break
            
            if id not in response:
                if not warned:
                    print("REDIRECTING")
                steer = steer_away_from_wall(plane)
                # if steer_crashes_plane(steer, plane):
                    # print("WARN?",)
                    # response[id] = -steer
                    # continue
                response[id] = steer
                continue

            my_pos_next_turn = plane.position + plane.stats.speed * Vector(cos(radians(plane.angle)), sin(radians(plane.angle)))
            my_cone_pos = my_pos_next_turn + plane.stats.attack_range * Vector(cos(radians(plane.angle)), sin(radians(plane.angle))) * 0.5
            for id_ in closest_enemies[:10]:
                enemy = not_my_planes[id_]
                enemy_pos_next_turn = enemy.position + enemy.stats.speed * Vector(cos(radians(enemy.angle)), sin(radians(enemy.angle)))
                enemy_cone_pos = enemy.position + enemy.stats.attack_range * Vector(cos(radians(enemy.angle)), sin(radians(enemy.angle))) * 0.75
                if (enemy.type != PlaneType.PIGEON and (enemy_cone_pos - my_pos_next_turn).norm() < 3):
                    response[id] = 1
                    break
                if (enemy_pos_next_turn - my_pos_next_turn).norm() < 4 - (enemy.type == PlaneType.PIGEON) \
                        and not (enemy.type == PlaneType.PIGEON and \
                        (enemy_pos_next_turn - my_cone_pos).norm() < plane.stats.attack_spread_angle * 0.8 * plane.stats.attack_range * pi / 180):
                    response[id] = steer_away_from_point(plane, enemy_pos_next_turn)
                    break

            if steer_crashes_plane(response[id], plane):
                print("don't kill yourself",)
                response[id] *= -1
                if id in hunted_targets:
                    del hunted_targets[id]


        print(special_message)

        return response

