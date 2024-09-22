import dataclasses
from game.plane import Plane, PlaneType, Vector
from math import sin, cos, atan2, copysign, degrees, radians, pi
from strategy.utils import steer_crashes_plane

def cross(a: Vector, b: Vector) -> float:
    return a.x * b.y - a.y * b.x

def angle(a: Vector) -> float:
    return degrees(atan2(a.y, a.x)) % 360

def angle_diff(a2: float, a1: float) -> float:
    return cc if abs(cc := (a2 - a1) % 360) < 180 else -copysign(360 - abs(cc), cc)

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

def follow_point(p: Plane, v: Vector) -> float:
    delta_pos = v - p.position
    target_heading = degrees(atan2(delta_pos.y, delta_pos.x))
    turn_speed = p.stats.turn_speed
    delta_angle = angle_diff(target_heading, p.angle)
    return copysign(min(abs(delta_angle) / turn_speed, 1), delta_angle)

def hold_formation(
    planes: list[Plane], formation: list[Vector], pos: Vector, theta: float
) -> list[float]:
    formation = [rotate(v, theta) + pos for v in formation]
    return [follow_point(p, v) for p, v in zip(planes, formation)]

def rotate(v: Vector, theta: float) -> Vector:
    theta = radians(theta)
    return Vector(
        v.x * cos(theta) - v.y * sin(theta), v.x * sin(theta) + v.y * cos(theta)
    )
    
special_message = "Beyblade beyblade let it rip! Let's fight, an epic battle! Face off and spin the metal! No time for doubt now, no place for backing down! Beyblade beyblade let it rip! Beyblade beyblade let it rip! Spin out the blade now, bring on the power! Right to the top, yeah, we're never givin' up! Here comes, here comes, METAL FUSION! Let's go Beyblade, let it rip! Metal Fusion, let it rip! Beyblade beyblade let it rip! This is it, get a grip, let it rip!"

class Skibidi:
    stagger_turns = 11
    turn = 0

    def select_planes(self) -> dict[PlaneType, int]:
        return {
            # PlaneType.STANDARD: 3,
            # PlaneType.FLYING_FORTRESS: 1,
            # PlaneType.PIGEON: 10,
            PlaneType.THUNDERBIRD: 5,
            # PlaneType.SCRAPYARD_RESCUE: 1,
        }

    def steer_to_point(self, plane: Plane, target: Vector) -> float:
        return max(-1, min(1, angle_diff(angle(target - plane.position), plane.angle) / plane.stats.turn_speed))
    
    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        response = {}
        my_planes = {id: plane for id, plane in planes.items() if plane.team == "friend"}
        hunters = {id: plane for id, plane in my_planes.items() if plane.type != PlaneType.PIGEON}
        pigeons = {id: plane for id, plane in my_planes.items() if plane.type == PlaneType.PIGEON}

        not_my_planes = {id: plane for id, plane in planes.items() if plane.team == "enemy"}

        if self.stagger_turns > 0:
            self.stagger_turns -= 1

        hunted_targets = {}
        for id, plane in hunters.items():
            if self.stagger_turns > 0:
                response[id] = -copysign((50-abs(plane.position.x)) / 50, plane.position.x)
                continue

            
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

            warned = False
            for id_ in closest_enemies:
                if len(closest_enemies) == 1:
                    enemy = not_my_planes[id_]
                    steer = self.steer_to_point(plane, enemy.position)
                    response[id] = steer
                    hunted_targets[id] = id_
                    break

                # if id_ in hunted_targets.values():
                    # continue
                enemy = not_my_planes[id_]
                steer = self.steer_to_point(plane, enemy.position)
                if steer_causes_crash(steer, plane, 3):
                    if not warned:
                        warned = True
                    else:
                        print("!", end="")
                    continue
                response[id] = steer
                # hunted_targets[id] = id_
                if warned:
                    print()
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
                next_enemy_cone_pos = enemy_pos_next_turn + enemy.stats.attack_range * Vector(cos(radians(enemy.angle)), sin(radians(enemy.angle))) * 2
                if (enemy.type != PlaneType.PIGEON and ((enemy_cone_pos - my_pos_next_turn).norm() < 5 or (next_enemy_cone_pos - my_pos_next_turn).norm() < 7)):
                    response[id] = steer_away_from_point(plane, enemy_cone_pos)
                    break
                if (enemy_pos_next_turn - my_pos_next_turn).norm() < 4 - 1 * (enemy.type == PlaneType.PIGEON) \
                        and not (enemy.type == PlaneType.PIGEON and \
                        (enemy_pos_next_turn - my_cone_pos).norm() < plane.stats.attack_spread_angle * 0.8 * plane.stats.attack_range * pi / 180):
                    response[id] = steer_away_from_point(plane, enemy_pos_next_turn)
                    break

            if steer_crashes_plane(response[id], plane):
                response[id] *= -1
                if id in hunted_targets:
                    del hunted_targets[id]



        self.grid_box = (-40, min(-35 + self.turn * 0.1, 40), 80, 5)
        pigeons_alive = len(pigeons.values())
        if pigeons_alive == 0:
            return response
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
        for idx, enemy in not_my_planes.items():
            enemy_pos = enemy.position
            if enemy_pos.y <= self.grid_box[1] + 20 and enemy_pos.y > self.grid_box[1] - self.grid_box[3] - 30:
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

        response |= pigeon_response

        self.grid_box = (-40, min(-35 + self.turn * 0.1, 40), 80, 5)
        pigeons_alive = len(pigeons.values())
        if pigeons_alive == 0:
            return response
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
        for idx, enemy in not_my_planes.items():
            enemy_pos = enemy.position
            if enemy_pos.y <= self.grid_box[1] + 20 and enemy_pos.y > self.grid_box[1] - self.grid_box[3] - 30:
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

        response |= pigeon_response

        return response

