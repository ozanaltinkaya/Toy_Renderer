from glm import *
from dataclasses import dataclass


@dataclass
class Vertex:
    index: int
    position: vec3
    tex_coord: vec2
    tangent: vec3
    normal: vec3
    color: vec4

