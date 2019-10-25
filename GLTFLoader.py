from pygltflib import GLTF2
from os import path
from pygltflib import utils
from struct import *
from Scene import *
import itertools
import glm
from typing import List


def get_type_size(tp):
    if tp == 5120:  # BYTE
        return 1
    elif tp == 5121:  # U_BYTE
        return 1
    elif tp == 5122:  # SHORT
        return 2
    elif tp == 5123:  # U_SHORT
        return 2
    elif tp == 5124:  # INT
        return 4
    elif tp == 5125:  # U_INT
        return 4
    elif tp == 5126:  # FLOAT
        return 4


def get_component_count_in_type(tp):
    if tp == 'SCALAR':
        return 1
    elif tp == 'VEC2':
        return 2
    elif tp == 'VEC3':
        return 3
    elif tp == 'VEC4':
        return 4
    elif tp == 'FLOAT':
        return 1


def get_type_code(tp):
    if tp == 5120:  # BYTE
        return 'b'
    elif tp == 5121:  # HALF_NV
        return 'B'
    elif tp == 5122:  # SHORT
        return 'h'
    elif tp == 5123:  # U_SHORT
        return 'H'
    elif tp == 5124:  # INT
        return 'i'
    elif tp == 5125:  # U_INT
        return 'I'
    elif tp == 5126:  # FLOAT
        return 'f'


class GLTFLoader:

    def __init__(self, filepath):
        # Load GLTF file
        self.gltf = GLTF2().load(filepath)
        self.path = filepath
        self.buffer = None
        self.bufferviews = None

        self.scene = Scene()

        # Load Buffer
        with open(path.dirname(self.path) + '/' + self.gltf.buffers[0].uri, mode='rb') as file:
            buffer = file.read()
        print(self.path + ' loaded.')
        self.buffer = buffer

        # Get buffferviews
        self.bufferviews = []
        for item in self.gltf.bufferViews:
            if item.byteOffset:
                self.bufferviews.append(buffer[item.byteOffset:item.byteOffset + item.byteLength])
            else:
                self.bufferviews.append(buffer[:item.byteLength])

        # Fill Scene object.
        self.scene.texture_list = self.create_texture_list()
        self.scene.material_list = self.create_material_list()
        self.scene.mesh_list = self.create_mesh_list()
        self.scene.nodelist = self.create_node_list()

    def get_accesor_data(self, acs_id: int):  # Get accesor data using accesor ID

        count = self.gltf.accessors[acs_id].count
        component_type = self.gltf.accessors[acs_id].componentType

        comp_type_size = get_type_size(self.gltf.accessors[acs_id].componentType)  # Float, int ?
        tp = get_component_count_in_type(self.gltf.accessors[acs_id].type)  # VEC3, VEC2, SCALAR?

        byte_size = comp_type_size * tp * count  # Total size in bytes

        acc_buff = self.bufferviews[self.gltf.accessors[acs_id].bufferView]

        if self.gltf.accessors[acs_id].byteOffset:
            chunk = acc_buff[self.gltf.accessors[acs_id].byteOffset:self.gltf.accessors[acs_id].byteOffset + byte_size]
        else:
            chunk = acc_buff[:byte_size]

        data = unpack(get_type_code(component_type) * (tp * count), chunk)

        return data

    def compose_vertex_buffer(self, mesh_id, prim_id):
        vb = []

        pos = self.get_accesor_data(self.gltf.meshes[mesh_id].primitives[prim_id].attributes.POSITION)

        if self.gltf.meshes[mesh_id].primitives[prim_id].attributes.TEXCOORD_0 is not None:
            tex_coord = self.get_accesor_data(self.gltf.meshes[mesh_id].primitives[prim_id].attributes.TEXCOORD_0)
        else:
            print("Object has no texture coordinates.")
            tex_coord = list(itertools.repeat(0.0, int((len(pos) / 3) * 2)))

        if self.gltf.meshes[mesh_id].primitives[prim_id].attributes.NORMAL is not None:
            normal = self.get_accesor_data(self.gltf.meshes[mesh_id].primitives[prim_id].attributes.NORMAL)
        else:
            print("Object has no normals.")
            normal = list(itertools.repeat(0.0, len(pos)))

        pos = [pos[i:i + 3] for i in range(0, len(pos), 3)]
        tex_coord = [tex_coord[i:i + 2] for i in range(0, len(tex_coord), 2)]
        normal = [normal[i:i + 3] for i in range(0, len(normal), 3)]
        for i in range(len(pos)):
            vb.append(pos[i])
            vb.append(tex_coord[i])
            vb.append(normal[i])

        return list(itertools.chain(*vb))

    def get_node_transformation(self, node_id) -> glm.mat4:  # Get Node transformation matrix using Node ID.
        matrix = glm.mat4(1.0)
        if self.gltf.nodes[node_id].matrix:
            # Convert gltf matrix to glm matrix.
            matrix = glm.mat4(*self.gltf.nodes[node_id].matrix)
            print("Node has matrix.")

        elif self.gltf.nodes[node_id].rotation or self.gltf.nodes[node_id].scale or self.gltf.nodes[node_id].rotation:
            # Convert transformation vectors to matrix.
            print("Node has vectors.")

            translation = glm.vec3()
            rotation = glm.quat()
            scale = glm.vec3(1.0, 1.0, 1.0)

            if self.gltf.nodes[node_id].translation:
                translation = glm.vec3(*self.gltf.nodes[node_id].translation)

            if self.gltf.nodes[node_id].rotation:
                rotation = glm.quat(*self.gltf.nodes[node_id].rotation)

            if self.gltf.nodes[node_id].scale:
                scale = glm.vec3(*self.gltf.nodes[node_id].scale)

            trans_mat = glm.translate(glm.mat4(1.0), translation)
            rot_mat = glm.mat4_cast(rotation)
            scale_mat = glm.scale(glm.mat4(1.0), scale)
            matrix = trans_mat * rot_mat * scale_mat

        return matrix

    def create_node_list(self):
        nodes = []
        for ind, nd in enumerate(self.gltf.nodes):
            mynode = Node()
            mynode.transformation = self.get_node_transformation(ind)
            if nd.name is not None:
                mynode.name = nd.name

            if nd.mesh is not None:
                mynode.mesh = self.scene.mesh_list[nd.mesh]

            if nd.children is not None:
                mynode.children = nd.children

            # print(mynode)
            nodes.append(mynode)
        # Set parents
        for i in range(len(nodes)):
            for ch in self.gltf.nodes[i].children:
                nodes[ch].parent = nodes[i]
        return nodes

    def create_mesh_list(self):
        meshes = []
        if self.gltf.meshes is not None:
            for mesh_ind, msh in enumerate(self.gltf.meshes):
                mymesh = Mesh()
                if msh.name:
                    mymesh.name = msh.name
                if msh.primitives is not None:

                    for pr_ind, prim in enumerate(msh.primitives):
                        myprim = Primitive()
                        myprim.vertices = self.compose_vertex_buffer(mesh_ind, pr_ind)
                        myprim.indices = self.get_accesor_data(prim.indices)
                        if prim.material is not None:
                            # myprim.material = prim.material
                            myprim.material = self.scene.material_list[prim.material]
                        else:
                            print("Primitive has no material. Assigning default material.")
                            myprim.material = self.scene.defaultMaterial  # TODO
                        mymesh.primitives.append(myprim)
                meshes.append(mymesh)

        return meshes

    def create_material_list(self):
        materials = []
        if self.gltf.materials is not None:
            for ind, mat in enumerate(self.gltf.materials):
                mymat = PBRMaterial()

                if mat.pbrMetallicRoughness is not None:
                    if mat.name is not None:
                        mymat.name = mat.name

                        # Assign textures
                    if mat.pbrMetallicRoughness.baseColorTexture is not None:
                        mymat.textures.basecolor = self.scene.texture_list[
                            mat.pbrMetallicRoughness.baseColorTexture.index]

                    if mat.pbrMetallicRoughness.metallicRoughnessTexture is not None:
                        mymat.textures.metallicRoughness = self.scene.texture_list[
                            mat.pbrMetallicRoughness.metallicRoughnessTexture.index]

                    if mat.occlusionTexture is not None:
                        mymat.textures.occlusion = self.scene.texture_list[
                            mat.occlusionTexture.index]

                    if mat.normalTexture is not None:
                        mymat.textures.normal = self.scene.texture_list[
                            mat.normalTexture.index]

                    if mat.emissiveTexture is not None:
                        mymat.textures.emissive = self.scene.texture_list[
                            mat.emissiveTexture.index]

                        # Assign factors
                    if mat.pbrMetallicRoughness.baseColorFactor is not None:
                        mymat.factors.basecolor = vec4(*mat.pbrMetallicRoughness.baseColorFactor)

                    if mat.pbrMetallicRoughness.roughnessFactor is not None:
                        mymat.factors.roughness = mat.pbrMetallicRoughness.roughnessFactor

                    if mat.pbrMetallicRoughness.metallicFactor is not None:
                        mymat.factors.metallic = mat.pbrMetallicRoughness.metallicFactor

                    if mat.emissiveFactor is not None:
                        mymat.factors.emissive = vec3(*mat.emissiveFactor)

                    materials.append(mymat)

                else:
                    print("Unknown material type.")

        return materials

    def create_texture_list(self):
        textures: List[Texture] = []

        if self.gltf.textures is not None:
            for tex_ind, texture in enumerate(self.gltf.textures):
                uri = self.gltf.images[texture.source].uri
                tex = Texture()
                tex.name = uri
                tex.load_texture((path.dirname(self.path) + '/' + uri))
                textures.append(tex)

        return textures

    def get_scene(self):
        return self.scene


