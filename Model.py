import numpy
import glm
from Shader import *
from collections import namedtuple
import pywavefront

class ObjLoader:
    def __init__(self, filepath):
        self.vertices = []
        self.v_normals = []
        self.tex_coord = []
        self.indices = []
        self.vertexData = []


        v = []
        vt = []
        vn = []

        ind_f = []
        vt_f = []
        vn_f = []

        try:
            f = open(filepath)
            for line in f:
                if line.startswith('v '):
                    line = line[2:]
                    line = line.strip().split()
                    v.append([float(line[0]), float(line[1]), float(line[2])])

                elif line.startswith('vn '):
                    line = line[3:]
                    line = line.strip().split()
                    vn.append([float(line[0]), float(line[1]), float(line[2])])

                elif line.startswith('vt '):
                    line = line[3:]
                    line = line.strip().split()
                    vt.append([float(line[0]), float(line[1]), float(line[2])])

                elif line.startswith('f '):
                    line = line[2:]
                    line = line.strip().split()
                    for i in line:
                        indi = i.split('/')
                        ind_f.append(int(indi[0])-1)
                        vt_f.append(int(indi[1])-1)
                        vn_f.append(int(indi[2])-1)

            f.close()
        except IOError:
            print(".obj file not found.")

        faces = [[ind_f[i], vt_f[i], vn_f[i]] for i in range(len(ind_f))]

        self.vertices.extend([v[faces[i][0]] for i in range(len(faces))])

        self.tex_coord.extend([vt[faces[i][1]] for i in range(len(faces))])

        self.v_normals.extend([vn[faces[i][2]] for i in range(len(faces))])

        self.indices = [faces[i][0] for i in range(len(faces))]

        for vert in self.vertices:
            self.vertexData.append(vert[0])
            self.vertexData.append(vert[1])
            self.vertexData.append(vert[2])



        # for i in range(len(faces)):
        #     vert = v[faces[i][0]]
        #     print(vert)
        #     self.vertices.extend(vert)
        # print(self.vertices)


# class ObjLoader(object):
#     def __init__(self, fileName):
#         self.vertices = []
#         self.faces = []
#         ##
#         try:
#             f = open(fileName)
#             for line in f:
#                 if line.startswith('v '):
#                     line = line[2:]
#                     pos = line.strip().split()
#                     for i in pos:
#                         self.vertices.append(float(i))
#
#                 elif line.startswith('f '):
#                     line = line[2:]
#                     line = line.strip().split()
#                     for i in range(3):
#                         indi = line[i].split('/')
#                         self.faces.append(int(indi[0])-1)
#
#             f.close()
#         except IOError:
#             print(".obj file not found.")


class Mesh:

    def __init__(self):
        self.vertices = []
        self.faces = []
        self.tex_coord = []
        self.normal = []

    def load_obj(self, path):
        try:
            f = open(path)
            for line in f:
                if line.startswith('v '):
                    line = line[2:]
                    pos = line.strip().split()
                    for i in pos:
                        self.vertices.append(float(i))

                elif line.startswith('f '):
                    line = line[2:]
                    line = line.strip().split()
                    for i in range(3):
                        indi = line[i].split('/')
                        self.faces.append(int(indi[0])-1)

                elif line.startswith('vt '):
                    pass


            f.close()
        except IOError:
            print(".obj file not found.")


class Material:
    def __init__(self, shader):
        Maps = namedtuple('Maps', ['basecolor', 'roughness', 'normal', 'metalness', 'emmisive'])
        self.maps = Maps(None, None, None, None, None)
        self.shader = shader
        self.model_matrix = None

class Model:
    def __init__(self, materials, meshes):
        self.meshes = meshes
        self.materials = materials
        self.model_matrix = glm.mat4(1)





# obj = ObjLoader('res/meshes/box_t.obj')
obj = pywavefront.Wavefront('res/meshes/box_t.obj', create_materials=True)


# mesh = pywavefront.obj.Material.