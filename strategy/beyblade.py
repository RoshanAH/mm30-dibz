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
    max_theta = plane.stats.turn_speed
    # Return the steer
    return -copysign(1, delta_theta / max_theta)

special_message = "Beyblade beyblade let it rip! Let's fight, an epic battle! Face off and spin the metal! No time for doubt now, no place for backing down! Beyblade beyblade let it rip! Beyblade beyblade let it rip! Spin out the blade now, bring on the power! Right to the top, yeah, we're never givin' up! Here comes, here comes, METAL FUSION! Let's go Beyblade, let it rip! Metal Fusion, let it rip! Beyblade beyblade let it rip! This is it, get a grip, let it rip!"

class beyblade:
    let_it_rip: dict[str, bool] = {}
    drop_radii: dict[str, float] = {}
    previous_targets: dict[str, tuple[str, int]] = {}
    turn_for: dict[str, tuple[float, int]] = {}
    stagger_turns = 11
    
    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {
            # PlaneType.FLYING_FORTRESS: 3,
            # PlaneType.STANDARD: 2,
            PlaneType.THUNDERBIRD: 5,
            # PlaneType.SCRAPYARD_RESCUE: 2,
            # PlaneType.PIGEON: 10,
        }

    def steer_to_point(self, plane: Plane, target: Vector) -> float:
        dist_from_target = target - plane.position
        print("distance from target", dist_from_target.norm())
        delta_theta = angle_diff(angle(dist_from_target), plane.angle)
        max_theta = plane.stats.turn_speed
        return max(-1, min(1, delta_theta / max_theta))
    
    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        response = {}
        my_planes = {id: plane for id, plane in planes.items() if plane.team == "friend"}
        dists_to_each_other = {id1: {id2: (plane1.position - plane2.position).norm() for id2, plane2 in my_planes.items()} for id1, plane1 in my_planes.items()}
        if not self.let_it_rip:
            for id, plane in my_planes.items():
                self.let_it_rip[id] = False
                self.drop_radii[id] = degree_to_radius(plane.stats.turn_speed, plane.stats.speed)

        not_my_planes = {id: plane for id, plane in planes.items() if plane.team == "enemy"}
        if self.stagger_turns > 0:
            self.stagger_turns -= 1

        for id, plane in my_planes.items():
            if plane.type in [PlaneType.FLYING_FORTRESS, PlaneType.STANDARD, PlaneType.THUNDERBIRD, PlaneType.SCRAPYARD_RESCUE]:
                if self.stagger_turns > 0:
                    # response[id] = random() * 2 - 1
                    response[id] = copysign(1, plane.position.x * plane.position.y) * min(1, abs(plane.position.x/5))
                    # response[id] = -1 + 0.5 * (int(id) % 4)
                    continue
            if plane.type in [PlaneType.FLYING_FORTRESS]:
                if self.let_it_rip[id]:
                    """
                    if not somebody_dipped and dists_to_each_other[id][min(dists_to_each_other[id], key=dists_to_each_other[id].get)] < 1:
                        somebody_dipped = True
                        response[id] = 1
                        print("PROXIMITY ALERT")
                        continue
                    """
                    print(special_message)
                    # response[id] = -1
                    # continue
                # Drop zone is centered, so norm is the distance from it

                # Determining theta_abs
                to_center = Vector(-plane.position.x, -plane.position.y)
                absolute_angle_to_center = angle(to_center) % 360

                # Determining theta_int
                try:
                    angle_to_drop_zone = degrees(asin(self.drop_radii[id] / plane.position.norm()))
                except ValueError:
                    angle_to_drop_zone = 90
                internal_angle = 90 - angle_to_drop_zone

                theta_tot = absolute_angle_to_center + 180 - internal_angle

                # Target point at edge of the drop zone
                target_radius = Vector(
                    self.drop_radii[id] * cos(radians(theta_tot)),
                    self.drop_radii[id] * sin(radians(theta_tot))
                )

                if not self.let_it_rip[id] and (target_radius - plane.position).norm() < 1:
                    self.let_it_rip[id] = True

                response[id] = self.steer_to_point(plane, target_radius)

            # HUNTER >:)
            if plane.type in [PlaneType.PIGEON, PlaneType.SCRAPYARD_RESCUE, PlaneType.THUNDERBIRD, PlaneType.STANDARD]:
                # Find the closest enemy
                def distance_heuristic(id):
                    return (diff := not_my_planes[id].position - plane.position).norm() * (abs(angle_diff(angle(diff), plane.angle))**(1/3))
                closest_enemies = sorted(not_my_planes, key=distance_heuristic)

                if id not in self.previous_targets:
                    self.previous_targets[id] = (closest_enemies[0], 0)

                previous_target, turns_followed = self.previous_targets[id]

                target_idx = 0

                if turns_followed > 20 and len(closest_enemies) > 1:
                    target_idx = 1
                    turns_followed = 0
                    # self.turn_for[id] = (0, 10)

                for id_ in closest_enemies[target_idx:]:
                    steer = self.steer_to_point(plane, not_my_planes[id_].position)
                    if steer_crashes_plane(steer, plane):
                        continue
                    response[id] = steer
                    if id_ != previous_target:
                        self.previous_targets[id] = (id_, 1)
                    else:
                        self.previous_targets[id] = (id_, turns_followed + 1)
                    break
                
                if id not in response or steer_crashes_plane(response[id], plane):
                    response[id] = steer_away_from_wall(plane)
                    continue


                # TODO: detect whether other planes will hit you
                my_pos_next_turn = plane.position + plane.stats.speed * Vector(cos(radians(plane.angle)), sin(radians(plane.angle)))
                turned_away = False
                for id_ in closest_enemies[:5]:
                    enemy = not_my_planes[id_]
                    enemy_pos_next_turn = enemy.position + enemy.stats.speed * Vector(cos(radians(enemy.angle)), sin(radians(enemy.angle)))
                    if (enemy_pos_next_turn - my_pos_next_turn).norm() < 2:
                        response[id] = steer_away_from_point(plane, enemy_pos_next_turn)
                        turned_away = True
                        break
                    
                if turned_away:
                    continue

                # TODO: detect whether you'll collide with another plane and steer away
                

        # Return the steers
        print(response)
        return response
