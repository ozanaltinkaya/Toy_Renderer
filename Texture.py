from PIL import Image
from OpenGL.GL import *
import numpy
from ctypes import *


class Texture:
    def __init__(self, filepath):
        self.image = Image.open(filepath)
        self.image = self.image.convert('RGBA')
        self.width, self.height = self.image.size
        print('opened file:', filepath, 'size:', self.image.size, 'format:', self.image.format, 'mode:',
              self.image.mode)
        self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)  # Flip image
        # imagedata = numpy.array(list(self.image.getdata()), numpy.uint8)
        imagedata = self.image.tobytes("raw", "RGBA", 0, -1)

        self.m_RendererID = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_2D, self.m_RendererID)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.width, self.height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, imagedata)

        # glBindTexture(0)
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
