from game.plane import Plane, PlaneType, Vector
import random
from math import pi, sin, cos, copysign, atan2

def deg(r: float) -> float:
    return r / pi * 180

def rad(d: float) -> float:
    return d / 180 * pi


# degrees
def rotate(v: Vector, theta: float) -> Vector:
    theta = rad(theta)
    return Vector(v.x * cos(theta) - v.y * sin(theta), v.x * sin(theta) + v.y * cos(theta))

# degrees
# dont mod this pls
def angle_diff(a2: float, a1: float) -> float:
    a1 %= 360
    a2 %= 360
    cc = a2 - a1
    c  = -copysign(360 - abs(cc), cc)
    if abs(cc) < 180:
        return cc
    return c

def follow_point(p: Plane, v: Vector) -> float:
    target_heading = deg((lambda d: atan2(d.y, d.x))(v - p.position))
    turn_speed = p.stats.turn_speed
    delta_angle = angle_diff(target_heading, p.angle)
    return copysign(min(abs(delta_angle) / turn_speed, 1), delta_angle)

class BallsReal:
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
            if plane.team == "enemy":
                continue
            
            current_x = plane.position.x
            current_y = plane.position.y
            nearest_plane_x = 0
            nearest_plane_y = 0
            nearest_dist = 99999
            for plane_id, plane_obj in planes.items():
                if plane.team != "enemy":
                    continue
                distance = (plane_obj.position.x - current_x) ** 2 + (plane_obj.position.y - current_y) ** 2
    
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_plane_x = plane_obj.position.x
                    nearest_plane_y = plane_obj.position.y



            boundary = 47.5
            if plane.position.y > boundary or plane.position.y < -boundary or plane.position.x > boundary or plane.position.x < -boundary:
                self.my_steers[id] = -1
            else:
                self.my_steers[id] = follow_point(plane, Vector(nearest_plane_x, nearest_plane_y))
            response[id] = self.my_steers[id]

        self.my_counter += 1

        # Return the steers
        return response
