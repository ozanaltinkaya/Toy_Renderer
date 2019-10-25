from OpenGL.GL import *
from collections import namedtuple
import glm
from ctypes import *


class Shader:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.m_RendererID = 0
        self.source = self.parse_shader(self.filepath)
        self.m_RendererID = self.create_shader(self.source.vertex, self.source.fragment)
        self.location = None

    def delete_shader(self):
        glDeleteProgram(self.m_RendererID)

    def bind(self):
        glUseProgram(self.m_RendererID)

    def unbind(self):
        glUseProgram(0)

    def set_uniform4f(self, name: str, v0: float, v1: float, v2: float, v3: float):
        # TODO: cache location
        glUniform4f(self.get_uniform_location(name), v0, v1, v2, v3)

    def set_uniformMat4f(self, name: str, matrix: glm.mat4):
        # TODO: cache location
        glUniformMatrix4fv(self.get_uniform_location(name), 1, GL_FALSE, glm.value_ptr(matrix))

    def set_uniform1i(self, name: str, value: int):
        # TODO: cache location
        glUniform1i(self.get_uniform_location(name), value)

    def set_uniform1f(self, name: str, value: float):
        # TODO: cache location
        glUniform1f(self.get_uniform_location(name), value)

    def get_uniform_location(self, name: str):
        self.location = glGetUniformLocation(self.m_RendererID, name)
        if self.location == -1:
            print("Warning: Uniform " + name + " doesn't exist.")
        return self.location

    def compile_shader(self, shader_type, source):

        sid = glCreateShader(shader_type)
        glShaderSource(sid, source)
        glCompileShader(sid)
        return sid

    def create_shader(self, vertex_shader, fragment_shader):
        program = glCreateProgram()
        vs = self.compile_shader(GL_VERTEX_SHADER, vertex_shader)
        fs = self.compile_shader(GL_FRAGMENT_SHADER, fragment_shader)

        glAttachShader(program, vs)
        glAttachShader(program, fs)
        glLinkProgram(program)
        glValidateProgram(program)

        glDeleteShader(vs)
        glDeleteShader(fs)

        return program

    def parse_shader(self, filepath):
        file = open(self.filepath)
        file_str = file.read()
        file_list = file_str.splitlines()
        vertex = ''
        fragment = ''
        state = False

        for line in file_list:
            if line != '//shader fragment':
                vertex += '\n' + line
            else:
                break

        for line in file_list:
            if line == '//shader fragment':
                state = True
            if state:
                fragment += '\n' + line

        nt_Shader = namedtuple('Shader', ['vertex', 'fragment'])
        shader = nt_Shader(vertex, fragment)
        return shader

