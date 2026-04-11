import numpy as np
import random
import math
import time

# Robust check with verbose error capturing
try:
    import numba
    HAVE_NUMBA = True
    NUMBA_ERROR = ""
except Exception as e:
    HAVE_NUMBA = False
    NUMBA_ERROR = str(e)
    # Create a dummy decorator that does nothing
    class numba:
        @staticmethod
        def jit(nopython=True, **kwargs):
            def decorator(func):
                return func
            return decorator

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

# Default configuration (can be overridden by the addon)
DEFAULT_WIDTH = 512
DEFAULT_HEIGHT = 512
DEFAULT_NUM_PARTICLES = 150000
DEFAULT_STICKINESS = 0.3


@numba.jit(nopython=True)
def run_optimized_dla(width, height, num_particles, stickiness):
    """Core DLA algorithm accelerated with Numba.

    Returns a binary grid of shape (height, width) where 1 indicates a particle.
    """
    grid = np.zeros((height, width), dtype=np.uint8)
    center_x, center_y = width // 2, height // 2
    grid[center_y, center_x] = 1

    max_spawn_distance = 20
    kill_distance = 40
    b_left = center_x
    b_right = center_x
    b_top = center_y
    b_bottom = center_y

    for i in range(num_particles - 1):
        # Spawn particles on the perimeter
        side = random.randint(0, 3)
        if side == 0:   # Top
            particle_x = random.randint(b_left - max_spawn_distance, b_right + max_spawn_distance)
            particle_y = b_top + max_spawn_distance
        elif side == 1: # Bottom
            particle_x = random.randint(b_left - max_spawn_distance, b_right + max_spawn_distance)
            particle_y = b_bottom - max_spawn_distance
        elif side == 2: # Left
            particle_x = b_left - max_spawn_distance
            particle_y = random.randint(b_bottom - max_spawn_distance, b_top + max_spawn_distance)
        else:           # Right
            particle_x = b_right + max_spawn_distance
            particle_y = random.randint(b_bottom - max_spawn_distance, b_top + max_spawn_distance)

        # Perform the random walk
        while True:
            move = random.randint(0, 3)
            if move == 0:   particle_y -= 1
            elif move == 1: particle_y += 1
            elif move == 2: particle_x -= 1
            else:           particle_x += 1

            # Kill particle if it wanders too far or hits image boundary
            if (particle_x < b_left - kill_distance or
                particle_x > b_right + kill_distance or
                particle_y < b_bottom - kill_distance or
                particle_y > b_top + kill_distance):
                break

            if (particle_x <= 0 or particle_x >= width - 1
                or particle_y <= 0
                or particle_y >= height - 1):
                break

            has_neighbor = (
                grid[particle_y-1, particle_x] or grid[particle_y+1, particle_x] or
                grid[particle_y, particle_x-1] or grid[particle_y, particle_x+1] or
                grid[particle_y-1, particle_x-1] or grid[particle_y-1, particle_x+1] or
                grid[particle_y+1, particle_x-1] or grid[particle_y+1, particle_x+1]
            )
            # Check for attachment
            if has_neighbor and random.random() < stickiness:
                grid[particle_y, particle_x] = 1  # Stick the particle

                if particle_x < b_left: b_left = particle_x
                if particle_x > b_right: b_right = particle_x
                if particle_y < b_bottom: b_bottom = particle_y
                if particle_y > b_top: b_top = particle_y
                break

    return grid


def generate_dla_grid(width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT,
                      num_particles=DEFAULT_NUM_PARTICLES,
                      stickiness=DEFAULT_STICKINESS):
    """Generate a DLA grid and return it as a float array normalized to [0, 1]."""
    grid = run_optimized_dla(width, height, num_particles, stickiness)
    return grid.astype(np.float32)
