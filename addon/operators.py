import bpy
import subprocess
import sys
import importlib
from bpy.props import StringProperty
from bpy.types import Operator

from . import dla_core, image_utils, geonodes

class DLA_OT_install_dependencies(Operator):
    bl_idname = "dla.install_dependencies"
    bl_label = "Install Numba (Requires Internet)"
    bl_description = "Installs required libraries into Blender's isolated script folder"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        modules_path = bpy.utils.user_resource('SCRIPTS', path='modules', create=True)

        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "numba", "scipy",
                "--target", modules_path, "--upgrade"
            ])
            importlib.reload(dla_core)

            if dla_core.HAVE_NUMBA:
                self.report({'INFO'}, "Success! Numba is installed.")
            else:
                self.report({'ERROR'}, f"Installed but failed to load: {dla_core.NUMBA_ERROR}")

        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"Installation failed: {e}")
            return {'CANCELLED'}

        for window in context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()

        return {'FINISHED'}


class GENERATE_OT_dla_terrain(Operator):
    bl_idname = "dla.generate_terrain"
    bl_label = "Generate DLA Terrain"
    bl_description = "Run DLA simulation, create heightmap, and set up geometry nodes"
    bl_options = {'REGISTER', 'UNDO'}

    image_name: StringProperty(default="DLA_Heightmap")

    def execute(self, context):
        props = context.scene.dla_properties

        if not dla_core.HAVE_NUMBA:
            self.report({'WARNING'}, "Numba is missing! Generation will be extremely slow.")

        try:
            grid = dla_core.generate_dla_grid(
                width=props.resolution,
                height=props.resolution,
                num_particles=props.particle_count,
                stickiness=props.stickiness
            )
            image_utils.create_heightmap_from_array(self.image_name, grid, normalize=False)
        except Exception as e:
            self.report({'ERROR'}, f"Generation Failed: {e}")
            return {'CANCELLED'}

        plane, modifier = geonodes.ensure_terrain_setup()
        if not plane or not modifier:
            self.report({'ERROR'}, "Geometry nodes setup failed.")
            return {'CANCELLED'}

        geonodes.assign_heightmap_to_node_group(self.image_name)

        bpy.ops.object.select_all(action='DESELECT')
        plane.select_set(True)
        context.view_layer.objects.active = plane

        self.report({'INFO'}, "DLA terrain successfully generated.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(DLA_OT_install_dependencies)
    bpy.utils.register_class(GENERATE_OT_dla_terrain)

def unregister():
    bpy.utils.unregister_class(GENERATE_OT_dla_terrain)
    bpy.utils.unregister_class(DLA_OT_install_dependencies)
