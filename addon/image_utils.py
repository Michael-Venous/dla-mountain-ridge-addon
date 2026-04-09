import bpy
import numpy as np


def get_or_create_image(name, width, height, float_buffer=True):
    """Return a Blender Image datablock with the given name and dimensions.
    
    If an image with that name already exists, its dimensions are checked;
    if they differ, the image is recreated. Otherwise the existing image is returned.
    
    Parameters
    ----------
    name : str
        Name of the image datablock.
    width, height : int
        Desired dimensions.
    float_buffer : bool
        If True, the image will be created with `is_float = True` (32‑bit float).
    
    Returns
    -------
    bpy.types.Image
        The (possibly new) image datablock.
    """
    images = bpy.data.images
    
    if name in images:
        img = images[name]
        if img.size[0] != width or img.size[1] != height:
            # Remove the old image and create a new one
            images.remove(img)
            img = images.new(name, width, height, alpha=True, float_buffer=float_buffer)
    else:
        img = images.new(name, width, height, alpha=True, float_buffer=float_buffer)
    
    # Ensure the image is not saved to disk (packed)
    img.pack()
    img.filepath = ""  # clear filepath to indicate it's not linked to a file
    
    return img


def update_image_from_array(image, array, normalize=False):
    """Write a 2D numpy array into an existing Blender Image.
    
    The array must have shape (height, width). Values are expected to be in the
    range [0, 1] if normalize is False; otherwise they are scaled to [0, 1].
    
    The image's pixels are updated in place.
    
    Parameters
    ----------
    image : bpy.types.Image
        Target image datablock.
    array : numpy.ndarray
        2D array of float or integer values.
    normalize : bool
        If True, scale the array to [0, 1] using its min/max.
    """
    height, width = array.shape
    if image.size[0] != width or image.size[1] != height:
        raise ValueError(f"Image size {image.size} does not match array shape ({height}, {width})")
    
    # Normalize if requested
    if normalize:
        amin = array.min()
        amax = array.max()
        if amax > amin:
            array = (array - amin) / (amax - amin)
        else:
            array = np.zeros_like(array)
    
    # Ensure the array is C‑contiguous float32 in range 0..1
    if array.dtype != np.float32:
        array = array.astype(np.float32)
    
    # Flatten to (height*width) and add an alpha channel (1.0)
    flat = array.ravel()
    # Create RGBA array: R = flat, G = flat, B = flat, A = 1.0
    rgba = np.empty((flat.shape[0], 4), dtype=np.float32)
    rgba[:, 0] = flat   # R
    rgba[:, 1] = flat   # G
    rgba[:, 2] = flat   # B
    rgba[:, 3] = 1.0    # A
    
    # Assign to image.pixels (image.pixels is a flat array of floats)
    image.pixels.foreach_set(rgba.ravel())
    
    # Mark the image as updated
    image.update()


def create_heightmap_from_array(name, array, normalize=False):
    """Convenience function: create or update an image with the given array.
    
    Returns the image datablock.
    """
    height, width = array.shape
    img = get_or_create_image(name, width, height, float_buffer=True)
    update_image_from_array(img, array, normalize)
    return img


# Example usage (for testing)
if __name__ == "__main__":
    # Generate a simple gradient for demonstration
    w, h = 256, 256
    x = np.linspace(0, 1, w)
    y = np.linspace(0, 1, h)
    X, Y = np.meshgrid(x, y)
    Z = (X + Y) * 0.5
    
    img = create_heightmap_from_array("TestHeightmap", Z)
    print(f"Created image {img.name} with size {img.size}")