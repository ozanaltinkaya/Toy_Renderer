from pygltflib import GLTF2
from os import path
from pygltflib import utils
from struct import *
from Scene import *
import itertools
import glm


def get_type_size(tp):
    if tp == 5120:  # BYTE
        return 1
    elif tp == 5121:  # HALF_NV
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
        return 1
    elif tp == 5121:  # HALF_NV
        return 1
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
        self.buffer = None
        self.bufferviews = None
        self.nodelist = None

        # Load Buffer
        with open(path.dirname(filepath) + '/' + self.gltf.buffers[0].uri, mode='rb') as file:
            buffer = file.read()
        print(filepath + ' loaded.')
        self.buffer = buffer

        # Get buffferviews
        self.bufferviews = []
        for item in self.gltf.bufferViews:
            if item.byteOffset:
                self.bufferviews.append(buffer[item.byteOffset:item.byteOffset + item.byteLength])
            else:
                self.bufferviews.append(buffer[:item.byteLength])

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

    def vertex_buffer(self):
        vb = []
        pos = self.get_accesor_data(self.gltf.meshes[0].primitives[0].attributes.POSITION)  # TODO: Fix
        tex_coord = self.get_accesor_data(self.gltf.meshes[0].primitives[0].attributes.TEXCOORD_0)
        normal = self.get_accesor_data(self.gltf.meshes[0].primitives[0].attributes.NORMAL)

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
        if self.gltf.nodes[node_id]:
            # Convert gltf matrix to glm matrix.
            matrix = glm.mat4(*self.gltf.nodes[node_id].matrix)
            print("Node has matrix.")

        elif self.gltf.nodes[node_id].rotation or self.gltf.nodes[node_id].scale or self.gltf.nodes[node_id].rotation:
            # Convert transformation vectors to matrix.
            print("Node has transformation.")

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
            for ch in self.gltf.nodes[i].children:
                nodes[ch].parent = i
        return nodes

    def create_mesh_list(self):
        meshes = []
        for ind, msh in enumerate(self.gltf.meshes):
            mymesh = Mesh()
            if msh.name:
                mymesh.name = msh.name

            for prim in msh.primitives:
                myprim = Primitive()


        pass

    def get_scene(self):
        pass



# def gltf_to_model(filepath):
#     gltf = GLTF2().load(filepath)
#     with open('res/gltf/box/' + gltf.buffers[0].uri, mode='rb') as file:
#         buffer = file.read()
#
#     bufferviews = []
#     for item in gltf.bufferViews:
#         bufferviews.append(buffer[item.byteOffset:item.byteOffset + item.byteLength])
#
#     meshes = []
#
#     for i in gltf.meshes[0].primitives:
#         ms = Mesh()
#         pos_acc = gltf.accessors[i.attributes.POSITION]
#         pos_data = bufferviews[pos_acc.bufferView]
#         # pos_chunk = pos_data[pos_acc.byteOffset:pos_acc.byteOffset+pos_acc.]
#         print(ms.position)
#
#
#     mdl = Model()
#     mdl.Name = gltf.meshes[0].name
#     mdl.meshes = gltf.meshes[0].primitives


# gltf = GLTF2()
#
# path = "res/gltf/box/Box.gltf"
#
# gltf = GLTF2().load(path)
# indices, vertices = [],[]
# with open('res/gltf/box/' + gltf.buffers[0].uri, mode='rb') as file:
#     data = file.read()
# buffer_view = gltf.bufferViews[0]
# chunk = data[buffer_view.byteOffset:buffer_view.byteOffset + buffer_view.byteLength]
# indices = unpac
# k("H" * 36, chunk)
# print(len(indices))
# buffer_view1 = gltf.bufferViews[1]
# chunk1 = data[buffer_view1.byteOffset:buffer_view1.byteOffset + buffer_view1.byteLength]
# vertices = unpack("f" * 144, chunk1)
# print(len(vertices))
#
# print(chunk)
