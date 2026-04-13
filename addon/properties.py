import bpy
from bpy.props import IntProperty, FloatProperty, PointerProperty
from bpy.types import PropertyGroup
from . import geonodes

def on_blur_property_update(self, context):
    geonodes.update_modifier_inputs(context.scene)

class DLAProperties(PropertyGroup):
    resolution: IntProperty(name="Resolution", default=512, min=64, max=4096, step=64, subtype='PIXEL')
    particle_count: IntProperty(name="Particle Count", default=50000, min=100, max=10000000, step=1000, subtype='UNSIGNED')
    stickiness: FloatProperty(name="Stickiness", default=0.6, min=0.01, max=1.0, step=0.01, precision=2, subtype='FACTOR')

class BlurProperties(PropertyGroup):
    blur_iterations_1: IntProperty(name="Blur Iterations 1", default=1, min=0, max=2000, step=10, subtype='UNSIGNED', update=on_blur_property_update)
    blur_iterations_2: IntProperty(name="Blur Iterations 2", default=25, min=0, max=2000, step=10, subtype='UNSIGNED', update=on_blur_property_update)
    blur_iterations_3: IntProperty(name="Blur Iterations 3", default=50, min=0, max=2000, step=10, subtype='UNSIGNED', update=on_blur_property_update)
    blur_iterations_4: IntProperty(name="Blur Iterations 4", default=500, min=0, max=2000, step=10, subtype='UNSIGNED', update=on_blur_property_update)

    height_multiplier_1: FloatProperty(name="Height Multiplier 1", default=1.000, min=0.0, max=100.0, step=0.001, precision=4, subtype='FACTOR', update=on_blur_property_update)
    height_multiplier_2: FloatProperty(name="Height Multiplier 2", default=1.000, min=0.0, max=100.0, step=0.001, precision=4, subtype='FACTOR', update=on_blur_property_update)
    height_multiplier_3: FloatProperty(name="Height Multiplier 3", default=1.000, min=0.0, max=100.0, step=0.001, precision=4, subtype='FACTOR', update=on_blur_property_update)
    height_multiplier_4: FloatProperty(name="Height Multiplier 4", default=1.000, min=0.0, max=100.0, step=0.001, precision=4, subtype='FACTOR', update=on_blur_property_update)

    final_multiplier: FloatProperty(name="Final Multiplier", default=1, min=0.0, max=10.0, step=0.001, precision=3, subtype='FACTOR', update=on_blur_property_update)

    subdivision_level: IntProperty(name="Subdivision Level", default=8, min=0, max=11, step=1, subtype='UNSIGNED', update=on_blur_property_update)
    
def register():
    bpy.utils.register_class(DLAProperties)
    bpy.utils.register_class(BlurProperties)

    bpy.types.Scene.dla_properties = PointerProperty(type=DLAProperties)
    bpy.types.Scene.blur_properties = PointerProperty(type=BlurProperties)

def unregister():
    del bpy.types.Scene.dla_properties
    del bpy.types.Scene.blur_properties

    bpy.utils.unregister_class(BlurProperties)
    bpy.utils.unregister_class(DLAProperties)
