import bpy
import logging

logger = logging.getLogger(__name__)

# Name of the geometry node group that must exist in the .blend file
GEONODE_GROUP_NAME = "mountain_displacer"
# Name of the image datablock that will be used as heightmap
HEIGHTMAP_IMAGE_NAME = "DLA_Heightmap"
# Name of the plane object to create (if not existing)
PLANE_OBJECT_NAME = "DLA_Terrain"


def get_geonode_group():
    """Return the geometry node group, appending it from the bundled asset if necessary."""
    node_groups = bpy.data.node_groups
    if GEONODE_GROUP_NAME in node_groups:
        return node_groups[GEONODE_GROUP_NAME]

    # If not found, append it from the included .blend file
    addon_dir = os.path.dirname(__file__)
    asset_path = os.path.join(addon_dir, "assets", "dla_nodes.blend")

    if not os.path.exists(asset_path):
        logger.error(f"Asset file not found at {asset_path}")
        return None

    with bpy.data.libraries.load(asset_path, link=False) as (data_from, data_to):
        if GEONODE_GROUP_NAME in data_from.node_groups:
            data_to.node_groups.append(GEONODE_GROUP_NAME)

    if GEONODE_GROUP_NAME in bpy.data.node_groups:
        logger.info(f"Appended {GEONODE_GROUP_NAME} from assets.")
        return bpy.data.node_groups[GEONODE_GROUP_NAME]

    logger.error("Failed to append the node group.")
    return None


def ensure_plane_object(subdivisions=512, size=1.0):
    """Create or retrieve a subdivided plane for the terrain.
    
    The plane is placed at the origin, scaled to match the DLA grid (size units).
    Subdivisions determine the mesh resolution for displacement.
    
    Returns the plane object.
    """
    scene = bpy.context.scene
    
    # Check if the plane already exists
    if PLANE_OBJECT_NAME in bpy.data.objects:
        plane = bpy.data.objects[PLANE_OBJECT_NAME]
        # Ensure it's a mesh
        if plane.type != 'MESH':
            logger.warning(f"Object '{PLANE_OBJECT_NAME}' exists but is not a mesh. Replacing.")
            bpy.data.objects.remove(plane, do_unlink=True)
        else:
            return plane
    
    # Create a new plane with subdivisions
    bpy.ops.mesh.primitive_plane_add(size=size, enter_editmode=False, align='WORLD')
    plane = bpy.context.active_object
    plane.name = PLANE_OBJECT_NAME
    
    # Subdivide the plane
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=subdivisions - 1)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Move to origin (already at origin)
    plane.location = (0, 0, 0)
    
    return plane


def add_geonodes_modifier(obj, node_group):
    """Add a Geometry Nodes modifier referencing the given node group.
    
    If a modifier with the same name already exists, it is reused.
    Returns the modifier.
    """
    mod_name = "DLA_Displacement"
    
    # Remove existing modifier with same name
    if mod_name in obj.modifiers:
        obj.modifiers.remove(obj.modifiers[mod_name])
    
    modifier = obj.modifiers.new(name=mod_name, type='NODES')
    modifier.node_group = node_group
    return modifier


def update_modifier_inputs(scene):

    if PLANE_OBJECT_NAME not in bpy.data.objects:
        return
    
    plane = bpy.data.objects[PLANE_OBJECT_NAME]
    mod_name = "DLA_Displacement"
    if mod_name not in plane.modifiers:
        return
    
    modifier = plane.modifiers[mod_name]
    props = scene.blur_properties
    
    
    try:
        modifier["Socket_X"] = props.blur_iterations_4  # huge_blur
        modifier["Socket_X"] = props.blur_iterations_3  # large_blur
        modifier["Socket_X"] = props.blur_iterations_2  # mid_blur
        modifier["Socket_X"] = props.blur_iterations_1  # fine_blur

        modifier["Socket_X"] = props.height_multiplier_1 # fine_mult
        modifier["Socket_X"] = props.height_multiplier_2 # mid_mult
        modifier["Socket_X"] = props.height_multiplier_3 # large_mult
        modifier["Socket_X"] = props.height_multiplier_4 # huge_mult

    except KeyError as e:
        logger.warning(f"Socket identifier {e} not found in modifier.")


def ensure_terrain_setup():
    """Main function: ensure a plane with the geometry node group is ready.
    
    Returns the plane object and the geometry nodes modifier.
    """
    node_group = get_geonode_group()
    if node_group is None:
        logger.error("Cannot proceed: geometry node group missing.")
        return None, None
    
    plane = ensure_plane_object(subdivisions=512, size=10.0)  # size can be adjusted
    modifier = add_geonodes_modifier(plane, node_group)
    
    # Set initial values for the modifier inputs (using current UI values)
    update_modifier_inputs(bpy.context.scene)
    
    return plane, modifier


def assign_heightmap_to_node_group(image_name=HEIGHTMAP_IMAGE_NAME):
    """Find the Image Texture node inside the geometry node group and assign the image.
    
    This is optional because the image datablock is referenced by name; if the
    node already uses the same name, the pixel data will be updated automatically.
    """
    node_group = get_geonode_group()
    if node_group is None:
        return
    
    # Find the first node of type 'TEX_IMAGE'
    image_node = None
    for node in node_group.nodes:
        if node.type == 'TEX_IMAGE':
            image_node = node
            break
    
    if image_node is None:
        logger.warning("No Image Texture node found in the geometry node group.")
        return
    
    # Assign the image datablock if it exists
    if image_name in bpy.data.images:
        image_node.image = bpy.data.images[image_name]
    else:
        logger.warning(f"Image '{image_name}' not found; node will stay empty.")


def register():
    """Module registration (optional)."""
    pass


def unregister():
    """Module unregistration (optional)."""
    pass


# Quick test when run as script
if __name__ == "__main__":
    # This should only be executed in Blender
    print("Testing geonodes module...")
    plane, mod = ensure_terrain_setup()
    if plane:
        print(f"Plane '{plane.name}' ready.")
    if mod:
        print(f"Modifier '{mod.name}' applied.")
