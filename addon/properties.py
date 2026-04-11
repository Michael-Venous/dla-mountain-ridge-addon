import bpy
from bpy.props import IntProperty, FloatProperty, PointerProperty
from bpy.types import PropertyGroup

from . import geonodes


def on_blur_property_update(self, context):
    """Callback triggered whenever a slider is moved in the UI."""
    geonodes.update_modifier_inputs(context.scene)


class DLAProperties(PropertyGroup):
    """Parameters for DLA generation."""
    
    resolution: IntProperty(
        name="Resolution",
        description="Width and height of the DLA grid (square)",
        default=120,
        min=64,
        max=4096,
        step=64,
        subtype='PIXEL'
    )
    
    particle_count: IntProperty(
        name="Particle Count",
        description="Number of particles to simulate",
        default=10000,
        min=1000,
        max=1000000,
        step=1000,
        subtype='UNSIGNED'
    )
    
    stickiness: FloatProperty(
        name="Stickiness",
        description="Probability of a particle sticking when it touches the cluster (0‑1)",
        default=0.3,
        min=0.01,
        max=1.0,
        step=0.01,
        precision=2,
        subtype='FACTOR'
    )


class BlurProperties(PropertyGroup):
    """Live‑tweakable parameters for the geometry node group.
    
    These correspond to the four blur iterations and four height multipliers
    inside the 'mountain_displacer' node group.
    """
    
    # Blur iterations (defaults: 500, 50, 30, 0)
    blur_iterations_1: IntProperty(
        name="Blur Iterations 1",
        description="Number of blur iterations for the finest detail level",
        default=0,
        min=0,
        max=2000,
        step=10,
        subtype='UNSIGNED',
        update=on_blur_property_update
    )
    
    blur_iterations_2: IntProperty(
        name="Blur Iterations 2",
        description="Number of blur iterations for the second detail level",
        default=30,
        min=0,
        max=2000,
        step=10,
        subtype='UNSIGNED',
        update=on_blur_property_update
    )
    
    blur_iterations_3: IntProperty(
        name="Blur Iterations 3",
        description="Number of blur iterations for the third detail level",
        default=50,
        min=0,
        max=2000,
        step=10,
        subtype='UNSIGNED',
        update=on_blur_property_update
    )
    
    blur_iterations_4: IntProperty(
        name="Blur Iterations 4",
        description="Number of blur iterations for the largest detail level",
        default=500,
        min=0,
        max=2000,
        step=10,
        subtype='UNSIGNED',
        update=on_blur_property_update
    )
    
    # Height multipliers (defaults: 0.004, 0.040, 0.200, 3.800)
    height_multiplier_1: FloatProperty(
        name="Height Multiplier 1",
        description="Intensity of the finest detail level",
        default=0.004,
        min=0.0,
        max=10.0,
        step=0.001,
        precision=4,
        subtype='FACTOR',
        update=on_blur_property_update
    )
    
    height_multiplier_2: FloatProperty(
        name="Height Multiplier 2",
        description="Intensity of the second detail level",
        default=0.040,
        min=0.0,
        max=10.0,
        step=0.001,
        precision=4,
        subtype='FACTOR',
        update=on_blur_property_update
    )
    
    height_multiplier_3: FloatProperty(
        name="Height Multiplier 3",
        description="Intensity of the third detail level",
        default=0.200,
        min=0.0,
        max=10.0,
        step=0.001,
        precision=4,
        subtype='FACTOR',
        update=on_blur_property_update
    )
    
    height_multiplier_4: FloatProperty(
        name="Height Multiplier 4",
        description="Intensity of the largest detail level",
        default=3.800,
        min=0.0,
        max=10.0,
        step=0.001,
        precision=4,
        subtype='FACTOR',
        update=on_blur_property_update
    )
    final_multiplier: FloatProperty(
        name="Final Multiplier",
        description="Overall intensity multiplier for the final terrain displacement",
        default=0.650,  # Matching the default from your screenshot
        min=0.0,
        max=10.0,
        step=0.001,
        precision=3,
        subtype='FACTOR',
        update=on_blur_property_update
    )

def register():
    """Register property groups and attach them to the Scene."""
    bpy.utils.register_class(DLAProperties)
    bpy.utils.register_class(BlurProperties)
    
    bpy.types.Scene.dla_properties = PointerProperty(type=DLAProperties)
    bpy.types.Scene.blur_properties = PointerProperty(type=BlurProperties)


def unregister():
    """Unregister property groups and remove pointers."""
    del bpy.types.Scene.dla_properties
    del bpy.types.Scene.blur_properties
    
    bpy.utils.unregister_class(BlurProperties)
    bpy.utils.unregister_class(DLAProperties)
