import pygame
import numpy as np
from copy import copy, deepcopy

class entity:
    def __init__(self, location, rect, type_flag=False, color=pygame.Color('red'), velocity=(0,0), radius=10):
        self.location = location
        self.dx, self.dy = velocity
        # self.dx = 0
        # self.dy = 0
        self.rect = rect
        self.type_flag = type_flag
        self.color = color
        self.velocity = velocity
        self.radius = radius #not sure how exactly this portion works
    
    def __copy__(self):
        return type(self)(self.location, self.rect, self.type_flag, self.color, self.velocity, self.radius)

    def collision_detection(self, other): #detect collision?
        return pygame.Rect.colliderect(self.rect, other.rect)

    def get_position(self):
        return np.array([self.rect.x, self.rect.y])

    def get_velocity(self):
        return np.array([self.dx, self.dy])

    def get_distance(self, other):
        # v = self.get_position() - other.get_position()
        v = other.get_position() - self.get_position()
        return np.linalg.norm(v)

    def move_timestep_bad(self, t):
        self.rect.move_ip(self.dx*t, self.dy*t)

    #check steps ahead
    def check_steps_ahead(self, t, other, velocity):
        collision_calculation_method = "collider_rects"
        
        if collision_calculation_method == "collider_rects":
            #method is very precise, but not every efficient
            
            #Create rects (essentialy AABB boxes) that simulate movement each frame (t). For the current object
            rects = {}
            for t_ in range(t):
                rects[t_] = pygame.Rect(self.rect.x + self.dx * t_, self.rect.y + self.dy * t_, self.rect.width , self.rect.height )
            
            other_rects = {}
            other_x, other_y = velocity
            for t_ in range(t):
                other_rects[t_] = pygame.Rect(other.rect.x + other_x * t_, other.rect.y + other_y * t_, other.rect.width, other.rect.height)

            #Create rects (essentialy AABB boxes) that simulate movement each frame (t). For the other object (usually player)
            for t_, value in rects.items(): #check for collisions by simulating the frames
                #FIXME: This was suposed to make sure that Player doesn't leave play area, but not very effective...
                if (other_rects[t_].width + 1 >= other_rects[t_].x >= 640 - other_rects[t_].width - 1) or (other_rects[t_].height + 1 >= other_rects[t_].y >= 480 - other_rects[t_].height - 1):
                    # return t_ - 1
                    return t_ -1 

                if pygame.Rect.colliderect(other_rects[t_], value):
                    return t_ - 1 #if collision detect at this point, return previous timestep where there was no collision
        elif collision_calculation_method == "distance":
            #more efficient method than using colliderects, but less precise
            other_x, other_y = velocity
            #simulate movement, get distance, it close enough, consider that to be a collision
            for t_ in range(t):
                if (other.rect.width >= other.rect.x + other_x * t_ >= 640 - other.rect.width) or (other.rect.height >= other.rect.y + other_y * t_ >= 480 - other.rect.height):
                    # return t_ - 1
                    return -1
                self_moved = np.array([self.rect.x + self.rect.width / 2 + self.dx * t_, self.rect.y + self.rect.height / 2 + self.dy * t_])
                other_moved = np.array([other.rect.x + other.rect.width / 2 + other_x * t_, other.rect.y + other.rect.height / 2 + other_y * t_])
                # self_moved = np.array([self.rect.x + self.dx * t_, self.rect.y + self.dy * t_])
                # other_moved = np.array([other.rect.x + other_x * t_, other.rect.y + other_y * t_])
                dist = np.linalg.norm(self_moved - other_moved)
                if dist <= 8: #~14.142
                    # print(dist)
                    return t_ - 1

        return t

    def move(self, x=0, y=0):
        #move_ip(x,y) => where x = 1 or y = 1 means 1 pixel movement per every update.
        if x == 0 and y == 0:
            self.rect.move_ip(self.dx, self.dy) #move_ip is used to move rect. x,y values are speed.
        else:
            self.rect.move_ip(x, y)