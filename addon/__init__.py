import bpy
import sys
import site

modules_path = bpy.utils.user_resource('SCRIPTS', path='modules', create=True)
if modules_path not in sys.path:
    sys.path.insert(0, modules_path)
    site.addsitedir(modules_path)

from . import addon_ui, properties, operators, geonodes, image_utils, dla_core

def register():
    properties.register()
    operators.register()
    geonodes.register()
    addon_ui.register()

def unregister():
    addon_ui.unregister()
    geonodes.unregister()
    operators.unregister()
    properties.unregister()

if __name__ == "__main__":
    register()
