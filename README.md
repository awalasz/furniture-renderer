# furniture-renderer
Recruitment task

# Requirements

- Docker

# Installation

## Build the image:
> $ docker build --tag svg_renderer:latest .

## Run the container:
> $ docker run -p 8000:8000 svg_renderer:latest

# Additional features
- remove obscured geometries
- further geometries are darker
- negated planes (like -XY) allowing to see the furniture from the other side.
