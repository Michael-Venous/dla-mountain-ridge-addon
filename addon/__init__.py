import bpy
import subprocess
import sys
import importlib

# Standard imports
from . import addon_ui, properties, operators, geonodes, image_utils, dla_core

def install_dependencies():
    """Checks for numba and installs it via pip if missing."""
    try:
        importlib.import_module("numba")
        return False # Already installed
    except ImportError:
        print("DLA Add-on: Numba not found. Installing automatically...")

        # Run pip install securely in the background using the --user flag
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--user", "numba", "scipy"
        ])

        print("DLA Add-on: Dependencies installed successfully!")
        return True # Just installed

def register():
    """Register all modules."""

    # 1. Check and install dependencies first
    just_installed = install_dependencies()

    # 2. If Numba was just installed, we MUST reload the core module.
    # Otherwise, it will continue using the dummy decorator created during the initial import.
    if just_installed:
        importlib.reload(dla_core)
        # Reload operators as well, since it imports dla_core
        importlib.reload(operators)

    # 3. Register everything else
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
