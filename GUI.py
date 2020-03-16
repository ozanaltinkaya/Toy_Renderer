from OpenGL.GL import *
from Buffers import *
from Shader import *
import numpy
from glm import *
import glfw
import Settings
import Global
import imgui
from Scene import *
import itertools


def draw_node_item(node, scene):
    nd = node

    if imgui.tree_node("Node: {} {}".format(str(nd.id), nd.name), imgui.TREE_NODE_OPEN_ON_ARROW):
        if nd.mesh:
            if imgui.tree_node("Mesh: {}".format(str(nd.mesh.id)), imgui.TREE_NODE_OPEN_ON_ARROW):
                if nd.mesh.primitives:
                    for i, prim in enumerate(nd.mesh.primitives):
                        if imgui.tree_node("Primitive: {}".format(str(i))):
                            if imgui.tree_node("Material", flags=imgui.TREE_NODE_LEAF | imgui.TREE_NODE_SELECTED):
                                imgui.tree_pop()
                            imgui.tree_pop()
                imgui.tree_pop()

        if nd.children:
            for i in nd.children:
                draw_node_item(scene.nodelist[i], scene)
        imgui.tree_pop()
        if imgui.is_item_clicked(): print("clicked")


def draw_imgui(scene: Scene):
    if Settings.GuiEnabled:
        # Menu Bar
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File"):
                imgui.menu_item("Open")

                if imgui.menu_item("Exit")[0]:
                    glfw.terminate()

                imgui.end_menu()

            if imgui.begin_menu("View"):

                if imgui.menu_item("Grid", shortcut='G', selected=Settings.GridEnabled)[0]:
                    Settings.GridEnabled = not Settings.GridEnabled

                if imgui.menu_item("GUI", shortcut='TAB', selected=Settings.GuiEnabled)[0]:
                    Settings.GuiEnabled = not Settings.GuiEnabled

                if imgui.menu_item("Stats", shortcut='P', selected=Settings.StatsEnabled)[0]:
                    Settings.StatsEnabled = not Settings.StatsEnabled

                imgui.end_menu()
            if Settings.StatsEnabled:
                imgui.same_line(imgui.get_window_width() - 150)
                imgui.text("FPS: " + "%.2f" % Global.fps + "  " + "%.2f" % Global.frametime + "ms")
        imgui.end_main_menu_bar()

        # imgui.show_demo_window()

        # Scene
        imgui.begin("Scene")
        draw_node_item(scene.nodelist[0], scene)
        imgui.end()

        imgui.begin("Properties")
        imgui.text("Model")

        # changed, translation.x = imgui.drag_float("X", translation.x)
        # changed, translation.y = imgui.drag_float("Y", translation.y)
        # changed, translation.z = imgui.drag_float("Z", translation.z)
        #
        # imgui.text("Camera")
        # changed, cam.position.x = imgui.drag_float("X cam", cam.position.x)
        # changed, cam.position.y = imgui.drag_float("Y cam", cam.position.y)
        # changed, cam.position.z = imgui.drag_float("Z cam", cam.position.z)

        imgui.end()

    else:
        pass


def draw_line(self, va: VertexArray, shader: Shader, point_count):
    shader.bind()
    va.bind()
    glDrawArrays(GL_LINES, 0, point_count)


class TimeTracker:
    def __init__(self):
        self.deltatime = 0.0
        self.lastframe = 0.0
        self.rendertime = 0.2
        self.timepassed = 0.0

    def update(self):
        currentframe = glfw.get_time()
        self.deltatime = currentframe - self.lastframe
        self.lastframe = currentframe

        if self.timepassed < 0.25:
            self.timepassed += self.deltatime
        else:
            self.rendertime = self.deltatime
            self.timepassed = 0
        Global.deltatime = self.deltatime
        Global.fps = 1000 / (self.rendertime * 1000)
        Global.frametime = self.deltatime * 1000

    def fps(self):
        return 1000 / (self.rendertime * 1000)

    def frame_time(self):
        return self.deltatime * 1000


class Grid:
    def __init__(self, step, cell_size):
        self.step = step
        self.cell_size = cell_size
        self.grid = []

        self.grid_sdr = Shader('res/shaders/Grid.glsl')
        self.grid_sdr.bind()

        self.layout = VertexBufferLayout()
        self.layout.push_float(2)
        self.VA = VertexArray()

        self.VA.unbind()
        self.grid_sdr.unbind()

        distance = cell_size * step
        grid_array = []
        if step == 0:
            xline = [cell_size, 0.0, -cell_size, 0.0]
            yline = [0.0, cell_size, 0.0, -cell_size]
        else:
            xline = [distance, 0.0, -distance, 0.0]
            yline = [0.0, distance, 0.0, -distance]

        grid_array.extend(xline)
        grid_array.extend(yline)

        if step > 0:
            for i in range(step):
                i = i + 1
                grid_array.extend([distance, i * cell_size,
                                   -distance, i * cell_size])
                grid_array.extend([distance, -i * cell_size,
                                   -distance, -i * cell_size])

                grid_array.extend([i * cell_size, distance,
                                   i * cell_size, -distance])
                grid_array.extend([-i * cell_size, distance,
                                   -i * cell_size, -distance])
        else:
            print("Grid step count can't be negative.")

        self.grid = numpy.array(grid_array, 'f')
        self.VB = VertexBuffer(self.get_grid_array())
        self.VA.add_buffer(self.VB, self.layout)

    def get_grid_array(self):
        return self.grid

    def get_point_count(self):
        # if self.step == 0:
        #     return 4
        return 4 + (self.step * 8)

    def unbind_shader(self):
        self.grid_sdr.bind()

    def bind_shader(self):
        self.grid_sdr.unbind()

    def draw_grid(self, proj, view):
        if Settings.GridEnabled:
            glEnable(GL_LINE_SMOOTH)
            self.grid_sdr.bind()
            self.VA.bind()
            self.grid_sdr.set_uniformMat4f('u_MVP',
                                           proj * view * rotate(mat4(1.0), radians(90), vec3(1.0, 0.0, 0.0)))
            # print(self.get_point_count())

            glDrawArrays(GL_LINES, 0, self.get_point_count())
            # draw_line(VALin, self.grid_sdr, self.get_point_count())
            self.grid_sdr.unbind()
            self.VA.unbind()


class Input:
    def __init__(self):
        self.xpos = Settings.WindowWidth / 2
        self.ypos = Settings.WindowHeight / 2
        self.lastX = 0.0
        self.lastY = 0.0
        self.xoffset = 0.0
        self.yoffset = 0.0
        self.firstmouse = True

    def mouse_pos_callback(self, window, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        if self.firstmouse:
            self.lastX = xpos
            self.lastY = ypos
            self.firstmouse = False

        self.xoffset = xpos - self.lastX
        self.yoffset = self.lastY - ypos

        self.lastX = xpos
        self.lastY = ypos

    def get_xoffset(self):
        return self.xoffset

    def get_yoffset(self):
        return self.xoffset

    def poll_mouse_pos(self, window):
        xpos = glfw.get_cursor_pos(window)[0]  # TODO: Use Callback Func instead.
        ypos = glfw.get_cursor_pos(window)[1]
        self.xpos = xpos
        self.ypos = ypos
        if self.firstmouse:
            self.lastX = xpos
            self.lastY = ypos
            self.firstmouse = False
        self.xoffset = xpos - self.lastX
        self.xoffset = self.lastX - xpos
        self.yoffset = self.lastY - ypos

        self.lastX = xpos
        self.lastY = ypos
        Global.XOffset = self.xoffset
        Global.YOffset = self.yoffset


class Flycam:
    def __init__(self, position=vec3(0.0, 0.0, 0.0), orientation=glm.quat()):
        self.firstPos = position
        self.firstOrient = orientation

        self.position = position
        self.orientation = orientation
        self.view = mat4(1.0)
        self.cam_X_rotation = 0.0
        self.cam_Y_rotation = 0.0

    def update(self, window):

        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            self.position -= glm.vec3(1.0, 0.0, 0.0) * Settings.CameraSpeed * Global.deltatime * glm.inverse(
                self.orientation)

        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            self.position += glm.vec3(1.0, 0.0, 0.0) * Settings.CameraSpeed * Global.deltatime * glm.inverse(
                self.orientation)

        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            self.position -= glm.vec3(0.0, 0.0, 1.0) * Settings.CameraSpeed * Global.deltatime * glm.inverse(
                self.orientation)

        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            self.position += glm.vec3(0.0, 0.0, 1.0) * Settings.CameraSpeed * Global.deltatime * glm.inverse(
                self.orientation)

        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            self.position.y = self.position.y + Settings.CameraSpeed * Global.deltatime

        if glfw.get_key(window, glfw.KEY_LEFT_ALT) == glfw.PRESS:
            self.position.y = self.position.y - Settings.CameraSpeed * Global.deltatime

        # if Global.XOffset > 30.0 or Global.XOffset < -30.0:
        #     Global.XOffset = 0.0
        #
        # if Global.YOffset > 30.0 or Global.YOffset < -30.0:
        #     Global.YOffset = 0.0

        self.cam_X_rotation += Global.XOffset * Settings.MouseSensitivity
        self.cam_Y_rotation += Global.YOffset * Settings.MouseSensitivity

        qxrot = glm.angleAxis(glm.radians(self.cam_X_rotation), glm.vec3(0.0, 1.0, 0.0))
        qyrot = glm.angleAxis(glm.radians(self.cam_Y_rotation), glm.vec3(1.0, 0.0, 0.0))

        print(Global.XOffset)

        self.orientation = qxrot * qyrot

        cam_rot_mat = glm.mat4_cast(self.orientation)

        self.view = glm.inverse(glm.translate(glm.mat4(1), self.position) * cam_rot_mat)

    def reset(self):
        pass

    def get_view(self):
        return self.view
