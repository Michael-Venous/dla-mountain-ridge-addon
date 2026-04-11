import bpy
from bpy.props import BoolProperty
from bpy.types import Panel
from . import dla_core

class VIEW3D_PT_dla_terrain(Panel):
    """Main panel for DLA Terrain addon."""
    bl_label = "DLA Terrain"
    bl_idname = "VIEW3D_PT_dla_terrain"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DLA Terrain"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # --- DEPENDENCY WARNING UI ---
        if not dla_core.HAVE_NUMBA:
            box = layout.box()
            box.alert = True
            box.label(text="Missing Numba Engine!", icon='ERROR')

            # Print a snippet of the exact error so the user (or you) knows why it failed
            error_snippet = dla_core.NUMBA_ERROR.split('\n')[-1][:50]
            if error_snippet:
                box.label(text=f"Error: {error_snippet}")

            box.label(text="Generations will be extremely slow.")
            box.operator("dla.install_dependencies", text="Install Numba", icon='CONSOLE')
            layout.separator()

        # --- Generation Section ---
        box = layout.box()
        box.label(text="Generation", icon='MODIFIER')

        col = box.column(align=True)
        col.prop(scene.dla_properties, "resolution")
        col.prop(scene.dla_properties, "particle_count")
        col.prop(scene.dla_properties, "stickiness")

        col.separator()
        col.operator("dla.generate_terrain", icon='PARTICLE_DATA')

        # --- Live Tweaks Section (collapsible) ---
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene, "show_dla_advanced", icon='TRIA_DOWN' if scene.show_dla_advanced else 'TRIA_RIGHT',
                 icon_only=True, emboss=False)
        row.label(text="Live Tweaks (Advanced)", icon='SETTINGS')

        if scene.show_dla_advanced:
            col = box.column(align=True)
            col.label(text="Blur Iterations:")
            col.prop(scene.blur_properties, "blur_iterations_1", slider=True)
            col.prop(scene.blur_properties, "blur_iterations_2", slider=True)
            col.prop(scene.blur_properties, "blur_iterations_3", slider=True)
            col.prop(scene.blur_properties, "blur_iterations_4", slider=True)

            col.separator()
            col.label(text="Height Multipliers:")
            col.prop(scene.blur_properties, "height_multiplier_1", slider=True)
            col.prop(scene.blur_properties, "height_multiplier_2", slider=True)
            col.prop(scene.blur_properties, "height_multiplier_3", slider=True)
            col.prop(scene.blur_properties, "height_multiplier_4", slider=True)

def register():
    bpy.utils.register_class(VIEW3D_PT_dla_terrain)
    # Register the UI-only property for collapsing the advanced section
    bpy.types.Scene.show_dla_advanced = BoolProperty(
        name="Show Advanced",
        description="Expand/collapse the live tweaks section",
        default=False
    )

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_dla_terrain)
    del bpy.types.Scene.show_dla_advanced
