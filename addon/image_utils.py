import bpy
import numpy as np

def get_or_create_image(name, width, height, float_buffer=True):
    img = bpy.data.images.get(name)

    if img:
        if img.size[0] != width or img.size[1] != height:
            bpy.data.images.remove(img)
            img = bpy.data.images.new(name, width, height, alpha=True, float_buffer=float_buffer)
    else:
        img = bpy.data.images.new(name, width, height, alpha=True, float_buffer=float_buffer)

    img.pack()
    img.filepath = ""
    return img

def update_image_from_array(image, array, normalize=False):
    if normalize:
        amin, amax = array.min(), array.max()
        if amax > amin:
            array = (array - amin) / (amax - amin)
        else:
            array = np.zeros_like(array)

    array = np.ascontiguousarray(array, dtype=np.float32)

    pixels = np.repeat(array.ravel(), 4)

    pixels[3::4] = 1.0

    image.pixels.foreach_set(pixels)
    image.update()

def create_heightmap_from_array(name, array, normalize=False):
    height, width = array.shape
    img = get_or_create_image(name, width, height, float_buffer=True)
    update_image_from_array(img, array, normalize)
    return img
