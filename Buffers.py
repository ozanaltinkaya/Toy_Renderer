from OpenGL.GL import *
import numpy
from collections import namedtuple
from ctypes import *


def get_size_of_type(tp):
    if tp is GL_FLOAT:
        return 4
    elif tp is GL_UNSIGNED_INT:
        return 4
    elif tp is GL_UNSIGNED_BYTE:
        return 1
    else:
        return 0


class VertexBuffer:

    def __init__(self, data):
        self.data = numpy.array(data, 'f')
        self.size = get_size_of_type(GL_FLOAT) * int(len(data))
        self.m_RendererID = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.m_RendererID)
        glBufferData(GL_ARRAY_BUFFER, self.size, self.data, GL_STATIC_DRAW)

    def delete_buffer(self):
        glDeleteBuffers(1, self.m_RendererID)

    def bind(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.m_RendererID)

    def unbind(self):
        glBindBuffer(GL_ARRAY_BUFFER, 0)


class IndexBuffer:

    def __init__(self, data):
        self.data = numpy.array(data, 'i')
        self.count = len(data)
        self.m_RendererID = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.m_RendererID)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.count * 4, self.data, GL_STATIC_DRAW)

    def delete_buffer(self):
        glDeleteBuffers(1, self.m_RendererID)

    def get_count(self):
        return self.count

    def bind(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.m_RendererID)

    def unbind(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)


class VertexBufferLayout:
    def __init__(self):
        self.elements = []
        self.stride = 0

    def push_float(self, count: int):
        nt_element = namedtuple('Element', ['data_type', 'count', 'normalized'])(GL_FLOAT, count, GL_FALSE)
        self.stride += count * get_size_of_type(GL_FLOAT)
        self.elements.append(nt_element)

    def push_uint(self, count: int):
        nt_element = namedtuple('Element', ['data_type', 'count', 'normalized'])(GL_UNSIGNED_INT, count, GL_FALSE)
        self.stride += count * get_size_of_type(GL_UNSIGNED_INT)
        self.elements.append(nt_element)

    def push_uchar(self, count: int):
        nt_element = namedtuple('Element', ['data_type', 'count', 'normalized'])(GL_UNSIGNED_BYTE, count, GL_TRUE)
        self.stride += count * get_size_of_type(GL_UNSIGNED_BYTE)
        self.elements.append(nt_element)

    def get_elements(self):
        return self.elements

    def get_stride(self):
        return self.stride


class VertexArray:
    def __init__(self):
        self.m_RendererID = glGenVertexArrays(1)

    def delete_vertex_array(self):
        glDeleteVertexArrays(1, self.m_RendererID)

    def add_buffer(self, vb: VertexBuffer, layout: VertexBufferLayout):
        self.bind()
        vb.bind()
        elements = layout.get_elements()
        offset = 0
        for i in range(len(elements)):
            element = elements[i]
            glEnableVertexAttribArray(i)
            glVertexAttribPointer(i, element.count, element.data_type, element.normalized,
                                  layout.get_stride(), c_void_p(offset))
            offset += element.count * get_size_of_type(element.data_type)

    def bind(self):
        glBindVertexArray(self.m_RendererID)

    def unbind(self):
        glBindVertexArray(0)




