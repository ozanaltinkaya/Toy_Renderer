from glm import *
from collections import namedtuple
from typing import List, Set, Dict, Tuple, Optional
from PIL import Image
from Buffers import *
from Shader import *
import Global


class Scene:
    def __init__(self):

        self.nodelist: List[Node] = []
        self.texture_list: List[Texture] = []
        self.material_list: List[PBRMaterial] = []
        self.mesh_list: List[Mesh] = []

        self.root_node: Node


    def add_node(self, node):
        pass

    def delete_node(self, node):
        pass

    def draw_scene(self):
        for node in self.nodelist:
            node.draw_node()

    def setup_scene(self):
        for node in self.nodelist:
            node.setup_node()


class Node:
    def __init__(self):
        self.mesh = None
        self.name = ""
        self.parent = None
        self.children: List[int] = []
        self.transformation = mat4(1.0)

    def __repr__(self):
        print("Name: " + self.name)
        print("Transformation:\n", self.transformation)
        return ""

    def draw_node(self):
        if self.mesh is not None:
            tr = self.get_model_transform()
            self.mesh.draw_mesh(tr)

    def get_model_transform(self):
        nd = self
        tr = self.transformation
        # TODO:Fix
        # while nd.parent is not None:
        #     tr = nd.parent.transformation * tr
        #     nd = nd.parent
        while True:
            if nd.parent is not None:
                tr = nd.parent.transformation * tr
                nd = nd.parent
            if nd.parent is None:
                tr = nd.transformation * tr
                break

        return tr


    def setup_node(self):
        if self.mesh is not None:
            self.mesh.setup_mesh()


#         if node has mesh, draw mesh

class Mesh:
    def __init__(self):
        self.name = ''
        self.primitives = []

    def setup_mesh(self):
        for prim in self.primitives:
            prim.setup_prim()

    def draw_mesh(self, modeltransform):
        for prim in self.primitives:
            prim.draw_prim(modeltransform)


class Primitive:
    def __init__(self):
        self.vertex_count = 0
        self.vertices = []
        self.indices = []
        self.material = None
        self.va = None
        self.ib = None
        self.vbo = None
        self.layout = None
        self.shader = None

    def setup_prim(self):
        self.va = VertexArray()
        self.vbo = VertexBuffer(self.vertices)

        self.layout = VertexBufferLayout()
        self.layout.push_float(3)
        self.layout.push_float(2)
        self.layout.push_float(3)
        self.va.add_buffer(self.vbo, self.layout)
        self.ib = IndexBuffer(self.indices)
        self.shader = Shader('res/shaders/BasicTextureMVP.glsl')

        self.material.textures.basecolor.setup_texture()


    def draw_prim(self,modeltransform):
        self.shader.bind()
        mvp = Global.ProjMat * Global.ViewMat * modeltransform
        self.shader.set_uniformMat4f('u_MVP', mvp)
        self.material.textures.basecolor.bind()
        self.shader.set_uniform1i('u_Texture', 0)
        self.va.bind()
        self.ib.bind()
        glDrawElements(GL_TRIANGLES, self.ib.get_count(), GL_UNSIGNED_INT, None)




class PBRMaterial:
    def __init__(self):
        self.name = "PBRMaterial"
        self.shader = None

        # Textures
        self.textures = namedtuple("Textures", "basecolor metallicRoughness occlusion emissive normal")
        self.textures.basecolor = Texture(color='white')
        self.textures.metallicRoughness = Texture(color='white')
        self.textures.occlusion = Texture(color='white')
        self.textures.emissive = Texture(color='black')
        self.textures.normal = Texture(color='normal')

        # Factors
        self.factors = namedtuple("Factors", "basecolor roughness metallic occlusion emissive")
        self.factors.basecolor = vec4(1.0, 1.0, 1.0, 1.0)
        self.factors.roughness = 1.0
        self.factors.metallic = 1.0
        self.factors.emissive = vec3(1.0, 1.0, 1.0)

    def setup_material(self):
        pass

    def bind_material(self):
        pass


class Texture:
    def __init__(self, color=''):
        self.image = None
        self.width, self.height = 0, 0
        self.imagedata = []
        self.format = ''
        self.filepath = ''
        self.mode = ''
        self.name = ''

        self.m_RendererID = 0
        # glBindTexture(0)

        # Create default texture
        if color:
            if color == "white":
                self.load_texture("res/textures/white.png")
                self.name = "DefaultWhite"

            if color == "black":
                self.load_texture("res/textures/black.png")
                self.name = "DefaultBlack"

            if color == "normal":
                self.load_texture("res/textures/normal.png")
                self.name = "DefaultNormal"



    def __repr__(self):
        return '''\
        Texture
        Filepath : {path}
        Size: ({width}, {height})
        '''.format(path=self.filepath, width=self.width, height=self.height)

    def setup_texture(self):
        self.m_RendererID = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_2D, self.m_RendererID)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.width, self.height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, self.imagedata)


    def load_texture(self, filepath):
        self.filepath = filepath
        self.image = Image.open(filepath)
        self.format = self.image.format
        self.mode = self.image.mode
        self.image = self.image.convert('RGBA')
        self.width, self.height = self.image.size
        print('opened file:', filepath, 'size:', self.image.size, 'format:', self.image.format, 'mode:',
              self.image.mode)
        self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)  # Flip image
        # self.imagedata = numpy.array(list(self.image.getdata()), numpy.uint8)
        self.imagedata = self.image.tobytes("raw", "RGBA", 0, -1)
        self.image.close()

    def delete_texture(self):
        glDeleteTextures(1, self.m_RendererID)

    def bind(self, slot=0):
        glActiveTexture(GL_TEXTURE0 + slot)
        glBindTexture(GL_TEXTURE_2D, self.m_RendererID)

    def unbind(self):
        glBindTexture(0)

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height


class Light:
    pass
