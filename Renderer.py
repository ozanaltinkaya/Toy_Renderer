from OpenGL.GL import *
from Buffers import *
from Shader import *

class Renderer:
    def __init__(self):
        pass

    def render_scene(self):
        pass

    def draw_element(self, va: VertexArray, ib: IndexBuffer, shader: Shader):
        shader.bind()
        va.bind()
        ib.bind()
        glDrawElements(GL_TRIANGLES, ib.get_count(), GL_UNSIGNED_INT, None)

    def draw_array(self, va: VertexArray, shader: Shader, vertex_count):
        shader.bind()
        va.bind()
        glDrawArrays(GL_TRIANGLES, 0, vertex_count)


    def clear(self):
        glClearColor(0.15, 0.15, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
