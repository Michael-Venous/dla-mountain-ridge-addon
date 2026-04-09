# DLA Mountain Terrain Generator for Blender

A Blender 4.2+ extension that generates highly realistic, fractal-like mountain ridges using a Diffusion-Limited Aggregation (DLA) algorithm. 

Instead of relying on standard noise textures, this add-on simulates the random walk of thousands of particles to create natural, branching ridge structures. It automatically generates a heightmap, applies it to a plane, and sets up a Geometry Nodes displacement pipeline with non-destructive, real-time controls.

## ✨ Features

* **Optimized DLA Simulation:** Core simulation is accelerated using `numba` JIT compilation, allowing you to generate heightmaps with hundreds of thousands of particles in seconds.
* **One-Click Setup:** Automatically creates the mesh plane, generates the DLA heightmap texture, and appends the required Geometry Nodes modifier.
* **Non-Destructive Live Tweaking:** Adjust the terrain post-generation via the 3D viewport side panel. Control blur iterations and displacement intensities across multiple detail frequencies (fine, mid, large, huge).
* **Dynamic Geometry Nodes:** Powered by a custom `mountain` node group that handles the image processing, subdivision, and displacement.

## 📋 Requirements

* **Blender 4.2 or higher:** This add-on uses the new Extensions API (`blender_manifest.toml`).
* **Numba:** Used for algorithm acceleration. (Blender will automatically install this via `pip` when you install the extension).

## 🚀 Installation

1. Download or clone this repository.
2. Navigate to the `addon` directory.
3. Select all the contents *inside* the `addon` folder (including `blender_manifest.toml`, the `.py` files, and the `assets` folder) and compress them into a ZIP file (e.g., `dla_terrain.zip`).
4. Open Blender and go to **Edit > Preferences > Get Extensions**.
5. Click the **⌄** drop-down arrow in the top right and select **Install from Disk...**
6. Select your `dla_terrain.zip` file.
7. Accept the prompt allowing Blender to install the `numba` Python dependency.

## 🛠️ Usage

### 1. Generating the Terrain
1. In the 3D Viewport, press **N** to open the side panel and navigate to the **DLA Terrain** tab.
2. Under the **Generation** section, adjust your parameters:
   * **Resolution:** The width/height of the generated heightmap image (e.g., 512, 1024).
   * **Particle Count:** The number of DLA particles to simulate. Higher counts create thicker, more expansive mountain ranges.
   * **Stickiness:** The probability (0.01 - 1.0) of a particle attaching to the cluster. Lower values create denser, rounder shapes; higher values create spindly, branching lightning-like shapes.
3. Click **Generate DLA Terrain**. 
   * *Note: The very first time you click this in a new Blender session, there may be a slight delay while Numba compiles the C code. Subsequent generations will be lightning fast.*

### 2. Live Tweaks (Advanced)
Once generated, you can non-destructively shape the mountains using the Geometry Nodes modifier. 

Expand the **Live Tweaks (Advanced)** section in the panel to adjust:
* **Blur Iterations:** Smooths out the DLA pixels at different structural levels. High iterations on the base level create sweeping mountain bases, while low iterations on the fine level preserve sharp, rocky ridges.
* **Height Multipliers:** Controls the vertical displacement intensity for the huge, large, mid, and fine detail levels, as well as a final master multiplier.

## 📂 Project Structure

* `addon_ui.py`, `properties.py`, `operators.py`: Handle the user interface and Blender integrations.
* `dla_core.py`: The standalone, Numba-optimized simulation logic.
* `image_utils.py`: Converts the raw Numpy arrays from the simulation into Blender Image datablocks.
* `geonodes.py`: Handles appending the master `mountain` node group from the bundled `.blend` asset and mapping the UI sliders to the specific Geometry Node sockets.
* `assets/dla_nodes.blend`: The master file containing the pre-configured Geometry Nodes setup.

## 📄 License
This project is licensed under the GPL-3.0-or-later License.
