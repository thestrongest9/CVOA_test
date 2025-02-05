# CVOA_test
 CVOA - Constrained Velocity Obstacle Algorithm

# How to run?
 To run, just run engine.py.

# Todo:
 Algorithm gets stuck at edges of the screen, where it inevitably collides with a bullet. 

# Possible solutions?
 Problem: "Algorithm gets stuck at edges of the screen, where it inevitably collides with a bullet."
 1. Make random choice instead of greedy search.
 2. By using clusters (or some other method of deciding), choose a point that is "desirable" for the player to move to, then focus on moving there.
 3. Something else???

# Greedy?
 As of right now the algorithm instantly selects the velocity (i.e. direction)
 that allows it to survive to the greatest amount of frames. HOWEVER.
 Since we have the amount of frames that the player can survive with a velocity
 we could possibly have the AI move such that ANY velocity can be chosen
 (or chosen according to some heuristic) and the moves in that direction for
 the amount of frames the player can survive in that direction, then when that
 "safe frame time" is exceeded, a new direction could then be found.
 Possibly, this could allow other heuristics or algorithms to direct the player
 at a higher level (i.e. macrododging?).