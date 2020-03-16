import glfw
from Renderer import *
import glm
import imgui
from imgui.integrations.glfw import GlfwRenderer
import GUI
import Settings
import Global
from GLTFLoader import *


def mouse_button_callback(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS:
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE)
        Global.CamRotationEnabled = True

    if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.RELEASE:
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
        Global.CamRotationEnabled = False


def process_input(window):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)


def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)


def scroll_callback(window, xoffset, yoffset):
    pass


def drop_callback(window, paths):
    print(paths[0])


def main():
    width, height = Settings.WindowWidth, Settings.WindowHeight

    # initialize glfw
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.SAMPLES, 4)
    glfw.window_hint(glfw.DEPTH_BITS, 32)

    window = glfw.create_window(width, height, "OpenGL Window", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    # glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # imgui stuff
    imgui.create_context()
    impl = GlfwRenderer(window)

    # Check OpenGL version
    print(glGetString(GL_VERSION))

    glfw.swap_interval(0)

    load = GLTFLoader("resources/gltf/trailer/scene.gltf")

    scene = load.get_scene()

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_MULTISAMPLE)

    Global.ProjMat = glm.perspective(glm.radians(35), width / height, 1.0, 100000.0)

    scene.setup_scene()

    grid = GUI.Grid(10, 50)

    renderer = Renderer()

    translation = glm.vec3(0.0, 0.0, 0.0)

    grid = GUI.Grid(10, 50)
    rotation = 0.0
    increment = 2.0

    view = glm.mat4(1.0)

    # Camera
    cam = GUI.Flycam(glm.vec3(0.0, 150.0, 1000))

    # Time & FPS counter
    tt = GUI.TimeTracker()

    # Input poll
    inpt = GUI.Input()

    # glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_drop_callback(window, drop_callback)

    scene.nodelist[0].transformation = glm.rotate(scene.nodelist[0].transformation, glm.radians(90),
                                                  vec3(1.0, 0.0, 0.0))

    scene.nodelist[0].transformation = glm.rotate(scene.nodelist[0].transformation, glm.radians(180),
                                                  vec3(0.0, 1.0, 0.0))

    while not glfw.window_should_close(window):
        # Time & FPS counter
        tt.update()

        # Input
        process_input(window)
        inpt.poll_mouse_pos(window)
        glfw.poll_events()

        # Camera
        cam.update(window)

        renderer.clear()
        glClear(GL_DEPTH_BUFFER_BIT)

        # --------Imgui----------
        impl.process_inputs()
        imgui.new_frame()
        GUI.draw_imgui(scene)

        imgui.show_demo_window()

        # Camera Stuff
        Global.ViewMat = cam.get_view()

        grid.draw_grid(Global.ProjMat, Global.ViewMat)

        scene.draw_scene()

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


if __name__ == '__main__':
    main()
