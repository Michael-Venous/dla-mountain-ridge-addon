import numpy as np
from PIL import Image
import random
import time
import numba

# Config
WIDTH = 2048
HEIGHT = 2048
NUM_PARTICLES = 1000000
FILENAME = "dla_optimized.png"
STICKINESS = 0.7 # How fart particles penetrate, lower = denser

@numba.jit(nopython=True)
def run_optimized_dla(width, height, num_particles, stickiness):
    # Grid and seed setup
    grid = np.zeros((height, width), dtype=np.uint8)
    center_x, center_y = width // 2, height // 2
    grid[center_y, center_x] = 1

    max_spawn_distance = 20
    kill_distance = 40

    # Use discrete variables instead of a list for max Numba speed
    b_left = center_x
    b_right = center_x
    b_top = center_y
    b_bottom = center_y

    for i in range(num_particles - 1):
        # Spawn particles ON THE PERIMETER, not inside the box
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

            # Kill particle if it wanders too far outside the kill box
            if (particle_x < b_left - kill_distance or
                particle_x > b_right + kill_distance or
                particle_y < b_bottom - kill_distance or
                particle_y > b_top + kill_distance):
                break

            # STRICT Boundary Check to prevent IndexError on +1/-1 neighbor lookups
            if particle_x <= 0 or particle_x >= width - 1 or particle_y <= 0 or particle_y >= height - 1:
                break

            # Evaluate neighbor check inline with stickiness (lazily evaluated)
            has_neighbor = (
                grid[particle_y-1, particle_x] or grid[particle_y+1, particle_x] or
                grid[particle_y, particle_x-1] or grid[particle_y, particle_x+1] or
                grid[particle_y-1, particle_x-1] or grid[particle_y-1, particle_x+1] or
                grid[particle_y+1, particle_x-1] or grid[particle_y+1, particle_x+1]
            )

            if has_neighbor and random.random() < stickiness:
                grid[particle_y, particle_x] = 1
                # Update bounding box
                if particle_x < b_left: b_left = particle_x
                if particle_x > b_right: b_right = particle_x
                if particle_y < b_bottom: b_bottom = particle_y
                if particle_y > b_top: b_top = particle_y
                break

    return grid

if __name__ == '__main__':
    print("Starting DLA generation...")
    start_time = time.time()

    dla_grid = run_optimized_dla(WIDTH, HEIGHT, NUM_PARTICLES, STICKINESS)

    end_time = time.time()
    print(f"DLA generation complete. Total time: {end_time - start_time:.2f} seconds.")

    # Save image
    image_array = dla_grid * 255
    img = Image.fromarray(image_array, 'L')
    img.save(FILENAME)

    lowres_size = (64, 64)
    lowres_img = img.resize(lowres_size, resample=Image.LANCZOS)
    lowres_filename = "dla_optimized_128.png"
    lowres_img.save(lowres_filename)

    print(f"Finished! Saved optimized DLA structure to {FILENAME}")
