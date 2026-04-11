import bpy
import sys
import os
import site

# --- MODERN DEPENDENCY INJECTION ---
# Before importing any of our files, we ensure Blender's isolated
# local user 'modules' directory is created and added to the system path.
modules_path = bpy.utils.user_resource('SCRIPTS', path='modules', create=True)
if modules_path not in sys.path:
    sys.path.insert(0, modules_path)
    site.addsitedir(modules_path) # Required to properly link compiled C-libraries

# Now it is safe to import local modules
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
