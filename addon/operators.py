import bpy
from bpy.props import StringProperty
from bpy.types import Operator
import numpy as np

from . import dla_core, image_utils, geonodes


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
        
        # Optionally assign the image to the node group (not strictly needed)
        geonodes.assign_heightmap_to_node_group(self.image_name)
        
        # Select the plane
        bpy.ops.object.select_all(action='DESELECT')
        plane.select_set(True)
        context.view_layer.objects.active = plane
        
        self.report({'INFO'}, "DLA terrain successfully generated and set up.")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # Optionally show a confirmation dialog
        return context.window_manager.invoke_confirm(self, event)


def register():
    bpy.utils.register_class(GENERATE_OT_dla_terrain)


def unregister():
    bpy.utils.unregister_class(GENERATE_OT_dla_terrain)