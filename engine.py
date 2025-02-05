import sys, os, pygame, re, random
import numpy as np
from copy import copy, deepcopy

#import other components
from entity import entity

# pygame.init()
# clock = pygame.time.Clock()

#move entity into separate file
#do this for the level editor.

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
CELL_SIZE = 16
OFFSET_FROM_LEFT = 2 * CELL_SIZE
OFFSET_FROM_TOP = 1 * CELL_SIZE
PLAY_AREA_WIDTH = 24 * CELL_SIZE
PLAY_AREA_HEIGHT = 28 * CELL_SIZE
# pygame.rect
surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
MAX_T = (0, 0)

#The AI's available actions would be = LEFT, RIGHT, UP, DOWN, LEFT+UP, LEFT+DOWN, RIGHT+UP, RIGHT+DOWN, DO_NOTHING  -> 8 directions and 1 for doing nothing = a total of 9 options.
def input_handler(): #instead of player input hand this over to the DQN (AI) to make decisions.
    x, y = 0, 0
    down = (0,0)
    up = (0,0)
    left = (0,0)
    right = (0,0)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()   
        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_w:
        #         x,y = (0,1)
        #     if event.key == pygame.K_a:
        #         pass
        #     if event.key == pygame.K_s:
        #         x,y = (0,-1)
        #     if event.key == pygame.K_d:
        #         pass
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        up = (0, -1)
    else:
        up = (0, 0)

    if keys[pygame.K_LEFT]:
        left = (-1, 0)
    else:
        left = (0, 0)
    
    if keys[pygame.K_DOWN]:
        down = (0,  1)
    else:
        down = (0, 0)

    if keys[pygame.K_RIGHT]:
        right = (1,  0)
    else:
        right = (0, 0)

    multiplier = 2
    if keys[pygame.K_LSHIFT]:
        multiplier = 1

    # print(up, left, right, down)
    return tuple(map(lambda i, j, k, l: (i+j+k+l)*multiplier, up, down, left, right))
            


def cvo_algo(obstacles=[], player=None, blocker=[]):
    #these possible velocities should take into account
    #player locked to 8 directions
    #player can increase or decrease speed (pressing shift, x2)
    #player can stand still (do nothing)
    multiplier = 2
    possible_velocities = [
        ( 0 * multiplier,  0 * multiplier), #stand still
        ( 0 * multiplier, -1 * multiplier), #up
        (-1 * multiplier, -1 * multiplier), #upleft
        ( 1 * multiplier, -1 * multiplier), #upright
        ( 0 * multiplier,  1 * multiplier), #down
        (-1 * multiplier,  1 * multiplier), #downleft
        ( 1 * multiplier,  1 * multiplier), #downright
        (-1 * multiplier,  0 * multiplier), #left
        ( 1 * multiplier,  0 * multiplier), #right
        # ( 0 * multiplier,  0 * multiplier), #stand still
    ]

    # if "left" in blocker:
    #     possible_velocities.remove((-1, -1)) #upleft
    #     possible_velocities.remove((-1,  1)) #downleft
    #     possible_velocities.remove((-1,  0)) #left
    # if "right" in blocker:
    #     possible_velocities.remove(( 1, -1)) #uprigh
    #     possible_velocities.remove(( 1,  1)) #downright
    #     possible_velocities.remove(( 1,  0)) #right
    # if "up" in blocker:
    #     possible_velocities.remove(( 0, -1)) #up
    #     if "left" not in blocker:
    #         possible_velocities.remove((-1, -1)) #upleft
    #     if "right" not in blocker:    
    #         possible_velocities.remove(( 1, -1)) #upright
    # if "down" in blocker:
    #     possible_velocities.remove(( 0,  1)) #down
    #     if "left" not in blocker:
    #         possible_velocities.remove((-1,  1)) #downleft
    #     if "right" not in blocker:
    #         possible_velocities.remove(( 1,  1)) #downright

    
    #create a dictionary of smallest distance direction needs to go to collide with something
    dir_collision = dict()
    for each in possible_velocities:
        dir_collision[each] = float("inf")
    
    #somehow also need to choose "best available" if no good decisions are available
    safe_velocities = possible_velocities.copy()

    max_t = 0
    max_t_velocity = possible_velocities[random.randint(0, len(possible_velocities)-1)]
    # max_t_velocity = possible_velocities[0]
    # max_t_velocity = MAX_T
    # print(SCREEN_WIDTH)
    center_dist = float("inf")
    
    # found_new_dir = False

    #remove any velocity that would cause collision
    for ob in obstacles:
        if ob.get_distance(player) <= 128.0: #only consider obstacles close enough
        # print("WHAT")
            # found_new_dir = True
            for v in possible_velocities:
                #get how many frames 
                no_collision_frames = ob.check_steps_ahead(10, player, v)
                # print("temp", temp)
                if dir_collision[v] > no_collision_frames:
                    dir_collision[v] = no_collision_frames
                    
                    # if temp > max_t:
                    #     x, y = v
                    #     max_t_velocity = v
                    #     center_dist = abs(player.rect.x - x - 208) + abs(player.rect.y - y - 384)
                    #     max_t = temp
                    # if temp == max_t: #if same max frames, then check dist from center
                    #     x, y = v
                    #     #center = 208, 384
                    #     dist = abs(player.rect.x - x - 208) + abs(player.rect.y - y - 384)
                    #     if dist < center_dist:
                    #         max_t_velocity = v

    # if found_new_dir == False:
    #     x, y = max_t_velocity
    #     return (x, y, 1)

    checker = 0
    prev_frame_checker = 0
    for direction, frames in dir_collision.items():
        # if MAX_T == direction:
        #     prev_frame_checker = frames 
        # if checker == frames:
        #     #if number of frames is equal, find out which move is closer to center
        #     prev_x, prev_y = max_t_velocity
        #     prev_center_dist = abs(player.rect.x + prev_x - 320) + abs(player.rect.y + prev_y - 240)
        #     new_x, new_y = direction
        #     new_center_dist = abs(player.rect.x + new_x - 320) + abs(player.rect.y + new_y - 240)
        #     if new_center_dist < prev_center_dist:
        #         max_t_velocity = direction
        if checker < frames:
            max_t_velocity = direction
            checker = frames
            # if checker < 32:
            #     print(checker)

    # if prev_frame_checker == checker and prev_frame_checker != -1:
    #     return MAX_T
    x, y = max_t_velocity
    return (x, y, checker)
    # return max_t_velocity



def menu_handler():
    print(pygame.event.get())
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
            # pygame.quit()
            # sys.exit()
        # else:
        #     return True
    return True
            

def dumb_spawner(start_position = 0):
    # if random.random() < 0.8:
    #     start_position = start_position + random.randint(-1, 1) * 16
    # else:
    start_position = (random.randint(0, 640) // 5) * 5
    # start_position = random.randint(0, 640) #(random.randint(0, 640) // 16) * 16
    # return entity(location=(start_position, 0))
    #6, 6
    return entity((30,30), pygame.Rect(start_position,0, 6, 6), color=pygame.Color('red'), velocity=(0, 2))

#Notes:
#I have to determine a "reward" somehow. (I guess survival time +1?)



def game_loop():
    pygame.init()
    pygame.display.init()
    clock = pygame.time.Clock()

    color = (255, 0, 0)
    objects = [] #objects -> This should become "state" that is fed into Pytorch's DQN. However, it should be done in a way that is always consistent. 
    # red_test = entity((30,30), pygame.Rect(30,30,60,60), color=pygame.Color('red'))
    # objects.append(red_test) 
    blue_test = entity((100,100), pygame.Rect(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 64, 5, 5), type_flag='player', color=pygame.Color('blue'))
    # objects.append(blue_test)

    next_move = 0
    MAX_T = (0, 0)
    frames_val = 0

    input_value = input_handler()
    temp_list = [dumb_spawner()]

    # print(menu_handler())
    #load level stuff
    running = True

    while running:#menu_handler():
        #NOTE: Only do collision detection after applying movement to both objects that could collide
        #For example, move player, move bullet, then detect for collision between player and bullet
        #seems obvious, but previous code had issue where collision detection would happen before move,
        #causing strange behaviour

        # running = menu_handler()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        surface.fill((0,0,0))  # Clear the screen each frame.
        # pygame.draw.rect(surface, pygame.Color('white'), background) #draw background
        
        #move player
        if blue_test.type_flag == 'player':

            # dx, dy = input_value             #location to move to

            blocker = []
            
            if OFFSET_FROM_LEFT == blue_test.rect.x:
                blocker.append("left")

            if PLAY_AREA_WIDTH + OFFSET_FROM_LEFT - blue_test.rect.width == blue_test.rect.x:
                blocker.append("right")
            
            if OFFSET_FROM_TOP == blue_test.rect.y:
                blocker.append("up")

            if PLAY_AREA_HEIGHT + OFFSET_FROM_TOP - blue_test.rect.height == blue_test.rect.y:
                blocker.append("down")

            if next_move >= frames_val:
                x, y, frames = cvo_algo(objects, blue_test, blocker)
                frames_val = next_move
                MAX_T = (x, y)
                next_move = 0
            else:
                next_move += 1
            # MAX_T = (dx, dy)
            dx, dy = MAX_T

            if blue_test.rect.width <= blue_test.rect.x + dx <= SCREEN_WIDTH - blue_test.rect.width:
                blue_test.dx = dx
            else: #stop movement if going all the way horizontally
                blue_test.dx = 0
            
            if blue_test.rect.height <= blue_test.rect.y + dy <= SCREEN_HEIGHT - blue_test.rect.height:
                blue_test.dy = dy
            else: #stop movement if going all the way vertically
                blue_test.dy = 0

            # blue_test.dx = dx
            # blue_test.dy = dy

            blue_test.move()
            pygame.draw.rect(surface, blue_test.color, blue_test.rect) #FIXME: do something with surface?

        # do some dumb spawning
        objects = temp_list + [dumb_spawner()]
        temp_list = []

        for temp_object in objects: #move all objects
            pygame.draw.rect(surface, temp_object.color, temp_object.rect) #FIXME: do something with surface?
            
            # dx, dy = input_value             #location to move to
            
            # x1, y1 = temp_object.location; #current location
            # print(dx,dy)
            
            temp_object.move()
            

            if temp_object.collision_detection(blue_test):
                print("Colision with player detected")
                # objects.remove(temp_object)
                # del objects[temp_object.rect.collidelist(objects)] #delete object that collided with player
            else:
                # objects = [temp_object] + objects
                _, y = temp_object.get_position()
                if y < 480:
                    temp_list.append(temp_object) #if no collision add back reference

        # objects = temp_list #set the new list of objects after collision detection

        clock.tick(30) #30
        pygame.display.update()
        #FIXME: Look at above here. Make it so that a new action is only taken every 250~300 milliseconds.
    
    pygame.quit()
    sys.exit()
#somehow add above networking ot game_loop
game_loop()