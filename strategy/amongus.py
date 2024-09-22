from game.plane import Plane, PlaneType
import random
from math import degrees, atan2

class Amongus():
    my_counter = 0
    my_steers = dict()
    my_target = dict()
    reached = dict()
    counter_since = dict()
    marked_already = dict()
    
    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {
            PlaneType.FLYING_FORTRESS: 3,
            PlaneType.PIGEON: 10,
        }
    
    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        response = dict()
        all_pigeon = True 
        for id, plane in planes.items():
            if plane.team == "enemy" and plane.type != PlaneType.PIGEON:
                all_pigeon = False
        for id, plane in planes.items():
            if plane.team == "enemy":
                continue
            if id not in self.my_steers:
                self.my_steers[id] = -1
                self.my_target[id] = 45
                self.reached[id] = False
                self.counter_since[id] = 0
            else:
                tolerance = 6
                boundary = 45
                counter_tol = 15
                if plane.angle > self.my_target[id] + tolerance:
                    self.my_steers[id] = -1
                    self.counter_since[id] += 1
                elif plane.angle < self.my_target[id] - tolerance:
                    self.my_steers[id] = 1
                    self.counter_since[id] += 1
                else:
                    self.my_steers[id] = 0
                    self.reached[id] = True
                    self.counter_since[id] += 1
                if max(abs(plane.position.x), abs(plane.position.y)) > boundary and self.reached[id] and self.counter_since[id] > counter_tol:
                    self.my_target[id] = (self.my_target[id] + 90)
                    self.reached[id] = False
                    self.counter_since[id] = 0
            if plane.type == PlaneType.PIGEON:
                current_x = plane.position.x
                current_y = plane.position.y
                closest_enemy_x = -100
                closest_enemy_y = -100
                closest_distance = 99999
                for idx, plane_item in planes.items():
                    if plane_item.team == "enemy" and (plane_item.type != PlaneType.PIGEON or all_pigeon) and ((plane_item.position.x, plane_item.position.y) not in self.marked_already or (self.marked_already[(plane_item.position.x, plane_item.position.y)] != self.my_counter)):
                        distance = (plane_item.position.x - current_x) ** 2 + (plane_item.position.y - current_y) ** 2
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_enemy_x = plane_item.position.x
                            closest_enemy_y = plane_item.position.y

                steering_direction = 0
                self.marked_already[(closest_enemy_x, closest_enemy_y)] = self.my_counter
                angle_to_enemy = degrees(atan2(closest_enemy_y - current_y, closest_enemy_x - current_x))
                                        
                if (angle_to_enemy - plane.angle > 0):
                    steering_direction = 1
                else:
                    steering_direction = -1

                if closest_enemy_x != -100:
                    self.my_steers[id] = steering_direction
                else:
                    self.my_steers[id] = random.random() * 2 - 1
                    if abs(plane.position.y) > 0:
                        self.my_steers[id] = (-1 + (random.random() * 2 - 1) * .3) / 1.3

                if max(abs(plane.position.x), abs(plane.position.y)) >= 47.5: # Don't fall off edge
                    self.my_steers[id] = -1
            response[id] = self.my_steers[id]

        self.my_counter += 1

        # Return the steers
        return response
