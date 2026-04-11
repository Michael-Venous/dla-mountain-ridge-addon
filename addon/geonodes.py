import os
import bpy
import logging

logger = logging.getLogger(__name__)

GEONODE_GROUP_NAME = "mountain"
HEIGHTMAP_IMAGE_NAME = "DLA_Heightmap"
PLANE_OBJECT_NAME = "DLA_Terrain"

def get_geonode_group():
    groups = bpy.data.node_groups
    if GEONODE_GROUP_NAME in groups:
        return groups[GEONODE_GROUP_NAME]

    asset_path = os.path.join(os.path.dirname(__file__), "assets", "dla_nodes.blend")
    if not os.path.exists(asset_path):
        logger.error(f"Asset file not found at {asset_path}")
        return None

    with bpy.data.libraries.load(asset_path, link=False) as (data_from, data_to):
        if GEONODE_GROUP_NAME in data_from.node_groups:
            data_to.node_groups.append(GEONODE_GROUP_NAME)

    return bpy.data.node_groups.get(GEONODE_GROUP_NAME)

def ensure_plane_object(size=10.0):
    plane = bpy.data.objects.get(PLANE_OBJECT_NAME)

    if plane:
        if plane.type != 'MESH':
            bpy.data.objects.remove(plane, do_unlink=True)
        else:
            return plane

    bpy.ops.mesh.primitive_plane_add(size=size, enter_editmode=False, align='WORLD')
    plane = bpy.context.active_object
    plane.name = PLANE_OBJECT_NAME
    plane.location = (0, 0, 0)

    return plane

def add_geonodes_modifier(obj, node_group):
    mod_name = "DLA_Displacement"

    if mod_name in obj.modifiers:
        obj.modifiers.remove(obj.modifiers[mod_name])

    modifier = obj.modifiers.new(name=mod_name, type='NODES')
    modifier.node_group = node_group
    return modifier

def update_modifier_inputs(scene):
    plane = bpy.data.objects.get(PLANE_OBJECT_NAME)
    if not plane:
        return

    modifier = plane.modifiers.get("DLA_Displacement")
    if not modifier:
        return

    props = scene.blur_properties

    sockets = {
        "Socket_2": props.blur_iterations_4,
        "Socket_3": props.blur_iterations_3,
        "Socket_4": props.blur_iterations_2,
        "Socket_5": props.blur_iterations_1,
        "Socket_6": props.height_multiplier_1,
        "Socket_7": props.height_multiplier_2,
        "Socket_8": props.height_multiplier_3,
        "Socket_9": props.height_multiplier_4,
        "Socket_10": props.final_multiplier
    }

    for key, val in sockets.items():
        if key in modifier:
            modifier[key] = val

def ensure_terrain_setup():
    node_group = get_geonode_group()
    if not node_group:
        return None, None

    plane = ensure_plane_object(size=10.0)
    modifier = add_geonodes_modifier(plane, node_group)
    update_modifier_inputs(bpy.context.scene)

    return plane, modifier

def assign_heightmap_to_node_group(image_name=HEIGHTMAP_IMAGE_NAME):
    node_group = get_geonode_group()
    if not node_group: return

    image_node = node_group.nodes.get("DLA_Texture_Node")
    img = bpy.data.images.get(image_name)

    if image_node and img:
        # Check if it's already assigned to prevent triggering a redundant
        # depsgraph evaluation in Blender, which saves processing time.
        if image_node.inputs['Image'].default_value != img:
            image_node.inputs['Image'].default_value = img
    elif not image_node:
        logger.error("Could not find 'DLA_Texture_Node' in the master node group.")

def register(): pass
def unregister(): pass
