from game.plane import Plane, PlaneType, Vector
from math import sin, cos, asin, acos, atan2, copysign, degrees, radians
from strategy.utils import degree_to_radius

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

special_message = "Beyblade beyblade let it rip! Let's fight, an epic battle! Face off and spin the metal! No time for doubt now, no place for backing down! Beyblade beyblade let it rip! Beyblade beyblade let it rip! Spin out the blade now, bring on the power! Right to the top, yeah, we're never givin' up! Here comes, here comes, METAL FUSION! Let's go Beyblade, let it rip! Metal Fusion, let it rip! Beyblade beyblade let it rip! This is it, get a grip, let it rip!"

class beyblade:
    let_it_rip: dict[str, bool] = {}
    drop_radii: dict[str, float] = {}
    my_steers: dict[str, float] = {}
    stagger_turns = 20
    
    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {
            PlaneType.FLYING_FORTRESS: 3,
        }
    
    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        response = {}
        my_planes = {id: plane for id, plane in planes.items() if plane.team == "friend"}
        if not self.let_it_rip:
            for id, plane in my_planes.items():
                self.let_it_rip[id] = False
                self.drop_radii[id] = degree_to_radius(plane.stats.turn_speed, plane.stats.speed)

        # not_my_planes = {id: plane for id, plane in planes.items() if plane.team == "enemy"}
        if self.stagger_turns > 0:
            self.stagger_turns -= 1
            return {id: -copysign(1, plane.position.x) * min(1, abs(plane.position.x/5)) for id, plane in my_planes.items()}

        for id, plane in my_planes.items():
            if self.let_it_rip[id]:
                print(special_message)
                response[id] = -1
                continue
            # Drop zone is centered, so norm is the distance from it

            # Determining theta_abs
            to_center = Vector(-plane.position.x, -plane.position.y)
            absolute_angle_to_center = angle(to_center) % 360

            # Determining theta_int
            angle_to_drop_zone = degrees(asin(self.drop_radii[id] / plane.position.norm()))
            internal_angle = 90 - angle_to_drop_zone

            theta_tot = absolute_angle_to_center + 180 - internal_angle

            # Target point at edge of the drop zone
            target_radius = Vector(
                self.drop_radii[id] * cos(radians(theta_tot)),
                self.drop_radii[id] * sin(radians(theta_tot))
            )
            dist_from_target = target_radius - plane.position
            print("distance from target", dist_from_target.norm())

            if dist_from_target.norm() < 1:
                print(special_message)
                self.let_it_rip[id] = True
                response[id] = -1
                continue

            delta_theta = angle_diff(angle(dist_from_target), plane.angle)
            max_theta = plane.stats.turn_speed

            steering = max(-1, min(1, delta_theta / max_theta))

            # TODO: Implement safety if the plane is too close to the drop zone

            response[id] = steering

        # Return the steers
        return response
