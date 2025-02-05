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