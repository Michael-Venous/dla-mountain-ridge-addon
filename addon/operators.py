import os
import bpy
import subprocess
import sys
import importlib
from bpy.props import StringProperty
from bpy.types import Operator
import numpy as np

from . import dla_core, image_utils, geonodes

class DLA_OT_install_dependencies(Operator):
    """Downloads and securely installs Numba and SciPy"""
    bl_idname = "dla.install_dependencies"
    bl_label = "Install Numba (Requires Internet)"
    bl_description = "Installs required libraries into Blender's isolated script folder"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        modules_path = bpy.utils.user_resource('SCRIPTS', path='modules', create=True)
        python_exe = sys.executable

        self.report({'INFO'}, "Installing Numba... Blender will freeze for a minute, please wait.")

        try:
            # Install securely to the isolated modules_path using --target
            subprocess.check_call([
                python_exe, "-m", "pip", "install", "numba", "scipy",
                "--target", modules_path, "--upgrade"
            ])

            # Force Python to reload the core module to apply the newly downloaded Numba JIT
            importlib.reload(dla_core)

            if dla_core.HAVE_NUMBA:
                self.report({'INFO'}, "Success! Numba is installed. Generation will now be fast.")
            else:
                self.report({'ERROR'}, f"Installed but failed to load: {dla_core.NUMBA_ERROR}")

        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"Installation failed: {e}")
            return {'CANCELLED'}

        # Force UI refresh to hide the install button
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()

        return {'FINISHED'}


class GENERATE_OT_dla_terrain(Operator):
    """Generate DLA terrain and set up geometry nodes."""
    bl_idname = "dla.generate_terrain"
    bl_label = "Generate DLA Terrain"
    bl_description = "Run DLA simulation, create heightmap, and set up geometry nodes"
    bl_options = {'REGISTER', 'UNDO'}

    image_name: StringProperty(
        name="Heightmap Name",
        description="Name of the image datablock to store the DLA heightmap",
        default="DLA_Heightmap"
    )

    def execute(self, context):
        scene = context.scene
        props = scene.dla_properties

        if not dla_core.HAVE_NUMBA:
            self.report({'WARNING'}, "Numba is missing! Generation will be extremely slow.")

        self.report({'INFO'}, "Starting DLA generation...")

        # Generate DLA grid
        try:
            grid = dla_core.generate_dla_grid(
                width=props.resolution,
                height=props.resolution,
                num_particles=props.particle_count,
                stickiness=props.stickiness
            )
        except Exception as e:
            self.report({'ERROR'}, f"DLA generation failed: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"DLA grid generated, shape {grid.shape}.")

        # Create or update the heightmap image
        try:
            img = image_utils.create_heightmap_from_array(self.image_name, grid, normalize=False)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create heightmap image: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Heightmap '{img.name}' ready.")

        # Ensure geometry nodes setup
        plane, modifier = geonodes.ensure_terrain_setup()
        if plane is None or modifier is None:
            self.report({'ERROR'}, "Geometry nodes setup failed.")
            return {'CANCELLED'}

        geonodes.assign_heightmap_to_node_group(self.image_name)

        bpy.ops.object.select_all(action='DESELECT')
        plane.select_set(True)
        context.view_layer.objects.active = plane

        self.report({'INFO'}, "DLA terrain successfully generated and set up.")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(DLA_OT_install_dependencies)
    bpy.utils.register_class(GENERATE_OT_dla_terrain)

def unregister():
    bpy.utils.unregister_class(GENERATE_OT_dla_terrain)
    bpy.utils.unregister_class(DLA_OT_install_dependencies)
