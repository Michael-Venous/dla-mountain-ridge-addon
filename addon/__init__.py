import bpy
import subprocess
import sys

# Standard imports
from . import addon_ui, properties, operators, geonodes, image_utils, dla_core

def register():
    """Register all modules."""

    properties.register()
    operators.register()
    geonodes.register()
    addon_ui.register()

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
