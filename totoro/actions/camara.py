from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
from totoro.actions import state

cam_pos = [0.0, 6.0, 18.0]
yaw = 0.0
pitch = 10.0

cam_speed = 0.7
mouse_down = False
last_mouse_x = 0
last_mouse_y = 0


def apply_camera():
    global cam_pos

    cam_x = 0.0
    cam_y = 6.0
    cam_z = state.zoom

    glRotatef(-pitch, 1.0, 0.0, 0.0)
    glRotatef(-yaw, 0.0, 1.0, 0.0)
    glTranslatef(-cam_x, -cam_y, -cam_z)


def handle_special_keys(key, x, y):
    global yaw, pitch

    if key == GLUT_KEY_UP:
        pitch += 2
    elif key == GLUT_KEY_DOWN:
        pitch -= 2
    elif key == GLUT_KEY_LEFT:
        yaw -= 3
    elif key == GLUT_KEY_RIGHT:
        yaw += 3

    pitch = max(-89, min(89, pitch))
    glutPostRedisplay()


def mouse(button, button_state, x, y):
    global mouse_down, last_mouse_x, last_mouse_y

    if button == GLUT_LEFT_BUTTON:
        mouse_down = (button_state == GLUT_DOWN)
        last_mouse_x = x
        last_mouse_y = y


def motion(x, y):
    global yaw, pitch, last_mouse_x, last_mouse_y

    if not mouse_down:
        return

    dx = x - last_mouse_x
    dy = y - last_mouse_y

    yaw += dx * 0.2
    pitch += dy * 0.2
    pitch = max(-89, min(89, pitch))

    last_mouse_x = x
    last_mouse_y = y

    glutPostRedisplay()