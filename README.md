# furniture-renderer
Recruitment task

# Requirements

- Docker

# Installation

Build the image:
> $ docker build --tag svg_renderer:latest .

Run the container:
> $ docker run -p 8000:8000 svg_renderer:latest

# Assumptions / simplifications
I assumed that geometry described with a pair of two points (x1, y1, z1, x2, y2, z2) has each of its sides always parallel 
to one of XY, YZ, or XZ plane. With that assumption, I will render SVG on which only one side of given geometry may be 
visible.

# Additional features not required by specification

I was curious how the furniture will look from the back. To check that I decided to implement additional 
"reverse planes". 

This leads me to the conclusion that furniture like this from the example input, when cast to 2D would look exactly the 
same from both front and back because the same geometries are visible and are almost symmetric. 
I decided to use depth that could be easily calculated and use it to make the closer figures bright, and those which are 
from the back - darker. 

When looking at the furniture from the top (XZ plane) - only one figure is visible, and the rest is obscured. 
Therefore there is no need to render each geometry from the input. I implemented a simple mechanism to remove figures 
fully obscured by another one. I am aware of the case when figures could be fully obscured by multiple others, 
but those would be harder to implement in a hurry. The Idea might be to sort figures and stack them on each other, 
adding the collective area of them to the condition used to determine whenever further figures are obstructed.

To sum it up, additional features are:
- removing obscured geometries,
- shading of the geometry based on its depth,
- negated planes allowing to see the furniture from the other side.
