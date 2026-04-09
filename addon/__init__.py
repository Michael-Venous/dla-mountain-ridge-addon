import bpy
from . import addon_ui, properties, operators, geonodes, image_utils, dla_core


def register():
    """Register all modules."""
    properties.register()
    operators.register()
    geonodes.register()
    addon_ui.register()
    # Note: dla_core and image_utils are utility modules, no registration needed

    print("DLA Mountain Terrain addon registered.")


def unregister():
    """Unregister all modules."""
    addon_ui.unregister()
    geonodes.unregister()
    operators.unregister()
    properties.unregister()

    print("DLA Mountain Terrain addon unregistered.")


if __name__ == "__main__":
    register()