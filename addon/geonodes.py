import os
import bpy
import logging

logger = logging.getLogger(__name__)

# Name of the geometry node group that must exist in the .blend file
GEONODE_GROUP_NAME = "mountain"
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
    scene = bpy.context.scene

    if PLANE_OBJECT_NAME in bpy.data.objects:
        plane = bpy.data.objects[PLANE_OBJECT_NAME]
        if plane.type != 'MESH':
            logger.warning(f"Object '{PLANE_OBJECT_NAME}' exists but is not a mesh. Replacing.")
            bpy.data.objects.remove(plane, do_unlink=True)
        else:
            return plane

    # Create a new regular plane
    bpy.ops.mesh.primitive_plane_add(size=size, enter_editmode=False, align='WORLD')
    plane = bpy.context.active_object
    plane.name = PLANE_OBJECT_NAME

    # Move to origin
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
        modifier["Socket_2"] = props.blur_iterations_4  # huge_blur
        modifier["Socket_3"] = props.blur_iterations_3  # large_blur
        modifier["Socket_4"] = props.blur_iterations_2  # mid_blur
        modifier["Socket_5"] = props.blur_iterations_1  # fine_blur

        modifier["Socket_6"] = props.height_multiplier_1 # fine_mult
        modifier["Socket_7"] = props.height_multiplier_2 # mid_mult
        modifier["Socket_8"] = props.height_multiplier_3 # large_mult
        modifier["Socket_9"] = props.height_multiplier_4 # huge_mult
        modifier["Socket_10"] = props.final_multiplier # final scale

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
    node_group = get_geonode_group()
    if node_group is None:
        return

    # Grab the node directly by the exact name you gave it
    image_node = node_group.nodes.get("DLA_Texture_Node")

    if image_node is None:
        print("ERROR: Could not find 'DLA_Texture_Node' in the master node group.")
        return

    # Link the generated heightmap datablock to the node's Image socket
    if image_name in bpy.data.images:
        image_node.inputs['Image'].default_value = bpy.data.images[image_name]
        print(f"SUCCESS: Linked {image_name} to {image_node.name}!")
    else:
        print(f"ERROR: Image '{image_name}' not found in Blender data.")


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
