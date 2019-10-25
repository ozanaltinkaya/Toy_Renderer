from pygltflib import GLTF2
import glm
from Scene import *

gltf = GLTF2() #hello

path = "res/gltf/box/2CylinderEngine.gltf"

gltf = GLTF2().load(path)
indices, vertices = [], []
with open('res/gltf/box/' + gltf.buffers[0].uri, mode='rb') as file:
    data = file.read()


def get_node_transformation(gltfnode) -> glm.mat4:
    matrix = glm.mat4(1.0)
    if gltfnode.matrix:
        # Convert matrix to glm matrix.
        matrix = glm.mat4(*gltfnode.matrix)
        # print("Node has matrix.")

    elif gltfnode.rotation or gltfnode.scale or gltfnode.rotation:
        # Create matrix from transformation.
        # print("Node has transformation.")

        translation = glm.vec3()
        rotation = glm.quat()
        scale = glm.vec3(1.0, 1.0, 1.0)

        if gltfnode.translation:
            translation = glm.vec3(*gltfnode.translation)

        if gltfnode.rotation:
            rotation = glm.quat(*gltfnode.rotation)

        if gltfnode.scale:
            scale = glm.vec3(*gltfnode.scale)

        trans_mat = glm.translate(glm.mat4(1.0), translation)
        rot_mat = glm.mat4_cast(rotation)
        scale_mat = glm.scale(glm.mat4(1.0), scale)
        matrix = trans_mat * rot_mat * scale_mat

    return matrix


def create_node_list():
    nodes = []
    for nd in gltf.nodes:
        mynode = Node()
        mynode.transformation = get_node_transformation(nd)
        if nd.name:
            mynode.name = nd.name

        if nd.mesh:
            mynode.mesh = nd.mesh

        if nd.children:
            mynode.children = nd.children

        # print(mynode)
        nodes.append(mynode)
    # Set parents
    for i in range(len(nodes)):
        for ch in gltf.nodes[i].children:
            nodes[ch].parent = i
    return nodes



print(gltf.materials[0].pbrMetallicRoughness.baseColorFactor)
# print(create_node_list()[10].children)
# print(gltf.materials)
