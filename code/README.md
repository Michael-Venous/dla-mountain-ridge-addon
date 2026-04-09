Python script that generates Diffusion-limited aggregation (DLA) based ridges.
With some image processing, the output can be used to generate realistic mountain terrain.

I use this algorithm for my terrain generator addon for blender.
In the blender addon: I combined many layers of the image, each with varying levels of guassian blur. Then, I displaced a mesh plane by the result. 
