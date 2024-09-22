import random
from game.plane import Plane, PlaneType
from math import degrees, atan2
# The following is the heart of your bot. This controls what your bot does.
# Feel free to change the behavior to your heart's content.
# You can also add other files under the strategy/ folder and import them

class Balls2():
    # BaseStrategy provides self.team, so you use self.team to see what team you are on

    # You can define whatever variables you want here
    my_counter = 0
    my_steers = dict()
    marked_already = dict()
    
    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {
            PlaneType.PIGEON: 50,
            PlaneType.FLYING_FORTRESS: 1,
            PlaneType.STANDARD: 1,
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
            else:
                current_x = plane.position.x
                current_y = plane.position.y
                closest_enemy_x = 0
                closest_enemy_y = 0
                closest_distance = 99999
                for idx, plane_item in planes.items():
                    if plane_item.team == "enemy" and plane_item.type == PlaneType.PIGEON:
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

                self.my_steers[id] = steering_direction
                bound = 40
                if plane.position.x > bound:
                    if plane.angle > 0 and plane.angle < 180:
                        self.my_steers[id] = 1
                    else:
                        self.my_steers[id] = -1
                elif plane.position.x < -bound:
                    if plane.angle > 180:
                        self.my_steers[id] = 1
                    else:
                        self.my_steers[id] = -1
                elif plane.position.y > bound:
                    if plane.angle > 90:
                        self.my_steers[id] = 1
                    else:
                        self.my_steers[id] = -1
                elif plane.position.y < -bound:
                    if plane.angle > 270:
                        self.my_steers[id] = 1
                    else:
                        self.my_steers[id] = -1
            response[id] = self.my_steers[id]

        self.my_counter += 1

        # Return the steers
        return response
            