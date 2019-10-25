import glfw
from Renderer import *
import glm
import imgui
from imgui.integrations.glfw import GlfwRenderer
from ctypes import *
import GUI
import Settings
from Model import *

def mouse_button_callback(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS:
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.RELEASE:
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

def process_input(window):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)


def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)


def scroll_callback(window, xoffset, yoffset):
    pass


def main():
    width, height = Settings.WindowWidth, Settings.WindowHeight

    # initialize glfw
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.SAMPLES, 4)

    window = glfw.create_window(width, height, "OpenGL Window", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    # imgui stuff
    impl = GlfwRenderer(window)

    # Check OpenGL version
    print(glGetString(GL_VERSION))

    glfw.swap_interval(0)

    positions = [
        -50, -50, 0.0, 0.0,
        50, -50, 0.0, 0.0,
        -50.0, 50, 0.0, 0.0,
        50.0, 50, 0.0, 0.0
                 ]
    indices = [0, 1, 2,
               2, 3, 0]

    obj = Mesh()
    obj.load_obj('res/meshes/knot.obj')

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_MULTISAMPLE)



    va = VertexArray()
    vb = VertexBuffer(obj.vertices)

    layout = VertexBufferLayout()
    layout.push_float(3)
    # layout.push_float(2)
    va.add_buffer(vb, layout)

    ib = IndexBuffer(obj.faces)
    proj = glm.perspective(glm.radians(35), width / height, 0.1, 100000.0)

    sdr = Shader('res/shaders/BasicMVP.glsl')
    sdr.bind()

    # sdr.set_uniform4f('u_Color', 0.8, 0.3, 0.8, 1.0)

    texture = Texture('res/textures/google512.png')
    texture.bind()
    sdr.set_uniform1i('u_Texture', 0)

    grid = GUI.Grid(10, 50)

    va.unbind()
    sdr.unbind()
    vb.unbind()
    ib.unbind()

    renderer = Renderer()

    translation = glm.vec3(0.0, 100.0, 0.0)

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

    cubevb = VertexBuffer(positions)
    cubelayout = VertexBufferLayout()
    cubelayout.push_float(2)
    cubelayout.push_float(2)
    cubeVA = VertexArray()
    cubeVA.add_buffer(cubevb, cubelayout)


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

        # Imgui
        impl.process_inputs()
        imgui.new_frame()

        imgui.begin("Test")
        imgui.text("Model")
        changed, translation.x = imgui.drag_float("X", translation.x)
        changed, translation.y = imgui.drag_float("Y", translation.y)
        changed, translation.z = imgui.drag_float("Z", translation.z)

        imgui.text("Camera")
        changed, cam.position.x = imgui.drag_float("X cam", cam.position.x)
        changed, cam.position.y = imgui.drag_float("Y cam", cam.position.y)
        changed, cam.position.z = imgui.drag_float("Z cam", cam.position.z)

        imgui.text("Light")
        changed, cam.position.x = imgui.drag_float("X cam", cam.position.x)
        changed, cam.position.y = imgui.drag_float("Y cam", cam.position.y)
        changed, cam.position.z = imgui.drag_float("Z cam", cam.position.z)
        imgui.text("FPS: " + "%.2f" % (tt.fps()) + "     " + "%.2f" % (tt.frame_time()) + "ms")

        imgui.text("Changed: %s, Value: %s" % (changed, translation.x))
        imgui.end()

        # Camera Stuff
        view = cam.get_view()

        grid.draw_grid(proj, view)

        model = glm.translate(glm.mat4(1.0), translation)
        rotation = rotation + tt.deltatime * 20
        model = glm.rotate(model, glm.radians(rotation), glm.vec3(0.0, -1.0, 0.0))

        mvp = proj * view * model

        sdr.bind()
        sdr.set_uniformMat4f('u_MVP', mvp)

        # renderer.draw_element(va, ib, sdr)
        renderer.draw_array(cubeVA, sdr, 4)
        sdr.unbind()

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    imgui.shutdown()
    glfw.terminate()


if __name__ == '__main__':
    main()