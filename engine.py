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
CURRENT_VELOCITY = (0, 0)

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
            

#Retunrns
#x, y, frame_count
#x = x direction of velocity
#y = y direction of velocity
#frame_count = the number of frames it is safe to move in that direction (velocity)
def cvo_algo(obstacles=[], player=None):
    #these possible velocities should take into account
    #player can move in 8 directions
    #FIXME: player can increase or decrease speed (pressing shift, x2)
    #player can stand still (do nothing)
    multiplier = 2
    #FIXME: Need to have (0, 0) option at top. or else starts moving. Need to fix somehow.
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
        #Without multiplier
        ( 0, -1), #up
        (-1, -1), #upleft
        ( 1, -1), #upright
        ( 0,  1), #down
        (-1,  1), #downleft
        ( 1,  1), #downright
        (-1,  0), #left
        ( 1,  0), #right
    ]
    
    #create a dictionary of smallest distance direction needs to go to collide with something
    dir_collision = dict()
    for each in possible_velocities:
        dir_collision[each] = float("inf")
    
    #somehow also need to choose "best available" if no good decisions are available
    # safe_velocities = possible_velocities.copy()
    max_t_velocity = possible_velocities[random.randint(0, len(possible_velocities)-1)]
    
    CHECK_FRAMES = 20 #amount of frames to check for collision

    #remove any velocity that would cause collision
    for ob in obstacles:
        #FIXME: When working on frame time divided version, need to set distance to very high number (need to take into account all bullets)
        if True:#ob.get_distance(player) <= 128.0: #only consider obstacles close enough
        # if ob.get_distance(player) <= 256:#128.0: #only consider obstacles close enough
            for v in possible_velocities:
                #get how many frames it is safe to move in direction (velocity) v.
                no_collision_frames = ob.check_steps_ahead(CHECK_FRAMES, player, v)
                if dir_collision[v] > no_collision_frames: #get the minimum amount of frames for that direction, based on collision detection with the obstacle
                    dir_collision[v] = no_collision_frames

    max_frames = 0
    
    #greedy choose current best
    # for direction, frames in dir_collision.items(): #from all {velocity:frames until collision}, get velocity with highest frames
    #     if max_frames < frames:
    #         max_t_velocity = direction
    #         max_frames = frames

    # #choose from some safe velocities
    # safe_velocities = []
    # for direction in dir_collision.keys():
    #     if dir_collision[direction] >= 7:
    #         safe_velocities.append(direction)
    # if safe_velocities != []:
    #     # print(len(safe_velocities))
    #     max_t_velocity = safe_velocities[random.randint(0, len(safe_velocities)-1)]
    
    # max_frames = dir_collision[max_t_velocity]

    #choose from some safe velocities
    safe_velocities = {}
    GREATEST_POSSIBLE_FRAMES = None
    dist = float("inf")
    for direction, frames in dir_collision.items():
        if frames not in safe_velocities:
            safe_velocities[frames] = [direction]
        else:
            safe_velocities[frames].append(direction)
        
        #check if greatest number of frames possible from current set of directions
        if GREATEST_POSSIBLE_FRAMES == None:
            GREATEST_POSSIBLE_FRAMES = frames
        else:
            if frames > GREATEST_POSSIBLE_FRAMES:
                GREATEST_POSSIBLE_FRAMES = frames

    if GREATEST_POSSIBLE_FRAMES != None:
        # print(len(safe_velocities))
        # max_t_velocity = safe_velocities[random.randint(0, len(safe_velocities)-1)]

        #choose closest to center
        for dir in safe_velocities[GREATEST_POSSIBLE_FRAMES]:
            dir_x, dir_y = dir
            #manhattan distance
            # y_axis * 2 => to emphasize y-axis movement more over x, otherwise when same good move appears, gets stuck beneath bullet and collides at bottom of screen.
            temp = abs(player.rect.x + dir_x - 320) + abs(player.rect.y + dir_y - 240) * 2 
            if temp <= dist:
                max_t_velocity = dir
                dist = temp
        #pick randomly
        # max_t_velocity = safe_velocities[GREATEST_POSSIBLE_FRAMES][random.randint(0, len(safe_velocities[GREATEST_POSSIBLE_FRAMES])-1)]
    
    max_frames = dir_collision[max_t_velocity]

    x, y = max_t_velocity #FIXME: Better way to do this?
    # print(max_t_velocity)

    if max_frames > CHECK_FRAMES: #this means that the max_Frames = infinity
        max_frames = 0

    return (x, y, max_frames) #return x, y, and frame count (frame count so that player AI can switch to different velocity after current one is no longer safe)

#Very dumb spawner
#Every tick, spawns a new bullet randomly
def dumb_spawner(start_position = 0):
    # if random.random() < 0.8:
    #     start_position = start_position + random.randint(-1, 1) * 16
    # else:
    start_position = (random.randint(0, 640) // 5) * 5
    # start_position = random.randint(0, 640) #(random.randint(0, 640) // 16) * 16
    # return entity(location=(start_position, 0))
    #6, 6
    return entity((30,30), pygame.Rect(start_position,0, 6, 6), color=pygame.Color('red'), velocity=(0, 2))

def game_loop():
    pygame.init()
    pygame.display.init()
    clock = pygame.time.Clock()

    #create player
    color = (255, 0, 0)
    objects = [] #contains bullets (projectiles)
    blue_test = entity((100,100), pygame.Rect(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 64, 5, 5), type_flag='player', color=pygame.Color('yellow'))

    frame_cnt = 0
    CURRENT_VELOCITY = (0, 0)
    frames_to_next = 0

    #input
    input_value = input_handler()
    
    #FIXME: Very bad way to do this. Probably better method exists?
    temp_list = [dumb_spawner()]

    running = True #is the game running or not?

    while running:#menu_handler():
        #NOTE: Only do collision detection after applying movement to both objects that could collide
        #For example, move player, move bullet, then detect for collision between player and bullet
        #seems obvious, but previous code had issue where collision detection would happen before move,
        #causing strange behaviour

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        surface.fill((0,0,0))  # Clear the screen each frame.
        # pygame.draw.rect(surface, pygame.Color('white'), background) #draw background
        
        #move player
        if blue_test.type_flag == 'player':

            # dx, dy = input_value             #location to move to

            #FIXME: Frame counting method could work...
            #       I need to have a better look at this.
            
            #NOTE:  -2 is safety margin
            #WHY?:  Because frames_to_next = "amount of frames until collision in X direction"
            #       Therefore, if we stop it two frames before, we get a nice safety margin, that allows for the
            #       Player to move away
            if frame_cnt >= frames_to_next - 2: #check if frame count for current velocity is done
                x, y, frames = cvo_algo(objects, blue_test) #get new velocity, and frames until next move
                frames_to_next = frames #get frames until next move
                # print(frames_to_next, frames)
                CURRENT_VELOCITY = (x, y)
                frame_cnt = 0 #reset frame count
            else: 
                frame_cnt += 1 #else increment current frame count
            
            # #NOTE: This calculates a new velocity (direction) every tick
            # x, y, frames = cvo_algo(objects, blue_test) #get new velocity, and frames until next move
            # CURRENT_VELOCITY = (x, y)

            # dx, dy = input_value  #direct control

            dx, dy = CURRENT_VELOCITY

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

            blue_test.move() #move player
            pygame.draw.rect(surface, blue_test.color, blue_test.rect) #FIXME: do something with surface?

        # do some dumb spawning
        objects = temp_list + [dumb_spawner()]
        temp_list = [] #reset list

        for temp_object in objects: #for all objects
            pygame.draw.rect(surface, temp_object.color, temp_object.rect) #FIXME: do something with surface?
            
            temp_object.move() #move object

            if temp_object.collision_detection(blue_test): #if colision detected with player
                print("Colision with player detected")
            else:
                _, y = temp_object.get_position()
                if y < 480: #if not outside of view (allow it to be garbage collected)
                    temp_list.append(temp_object) #if no collision add back reference

        clock.tick(30) #30 fps
        pygame.display.update()
    
    pygame.quit()
    sys.exit()
#somehow add above networking ot game_loop
game_loop()