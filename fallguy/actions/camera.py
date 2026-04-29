# actions/camera.py
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *
import math
from fallguy.actions import state

# --- Posicion inicial de camara ---
cam_pos      = [0.0, 3.5, 9.0]
yaw          = 0.0
pitch        = -12.0
cam_speed    = 0.22
mouse_down   = False
last_mouse_x = 0
last_mouse_y = 0

def apply_camera():
    glRotatef(-pitch, 1.0, 0.0, 0.0)
    glRotatef(-yaw,   0.0, 1.0, 0.0)
    glTranslatef(-cam_pos[0], -cam_pos[1], -cam_pos[2])

# --- 7 movimientos de camara ---
def move_up():       cam_pos[1] += cam_speed          # 1. Arriba
def move_down():     cam_pos[1] -= cam_speed          # 2. Abajo

def move_left():                                       # 3. Izquierda
    cam_pos[0] -= math.cos(math.radians(yaw)) * cam_speed
    cam_pos[2] -= math.sin(math.radians(yaw)) * cam_speed

def move_right():                                      # 4. Derecha
    cam_pos[0] += math.cos(math.radians(yaw)) * cam_speed
    cam_pos[2] += math.sin(math.radians(yaw)) * cam_speed

def zoom_in():                                         # 5. Zoom In
    cam_pos[0] += math.sin(math.radians(yaw)) * cam_speed * 2
    cam_pos[2] -= math.cos(math.radians(yaw)) * cam_speed * 2

def zoom_out():                                        # 6. Zoom Out
    cam_pos[0] -= math.sin(math.radians(yaw)) * cam_speed * 2
    cam_pos[2] += math.cos(math.radians(yaw)) * cam_speed * 2

def reset_camera():                                    # 7. Reset
    global yaw, pitch
    cam_pos[0] = 0.0
    cam_pos[1] = 3.5
    cam_pos[2] = 9.0
    yaw   = 0.0
    pitch = -12.0

# --- Mouse: rotar arrastrando, scroll = zoom ---
def mouse(button, button_state, x, y):
    global mouse_down, last_mouse_x, last_mouse_y
    if button == GLUT_LEFT_BUTTON:
        mouse_down   = (button_state == GLUT_DOWN)
        last_mouse_x = x
        last_mouse_y = y
    elif button == 3:   # scroll arriba → zoom in
        zoom_in(); glutPostRedisplay()
    elif button == 4:   # scroll abajo  → zoom out
        zoom_out(); glutPostRedisplay()

def motion(x, y):
    global yaw, pitch, last_mouse_x, last_mouse_y
    if not mouse_down:
        return
    yaw   += (x - last_mouse_x) * 0.3
    pitch += (y - last_mouse_y) * 0.3
    pitch  = max(-89, min(89, pitch))
    last_mouse_x = x
    last_mouse_y = y
    glutPostRedisplay()

# --- Flechas del teclado mueven la camara ---
def handle_special_keys(key, x, y):
    if   key == GLUT_KEY_UP:        zoom_in()
    elif key == GLUT_KEY_DOWN:      zoom_out()
    elif key == GLUT_KEY_LEFT:      move_left()
    elif key == GLUT_KEY_RIGHT:     move_right()
    elif key == GLUT_KEY_PAGE_UP:   move_up()
    elif key == GLUT_KEY_PAGE_DOWN: move_down()
    glutPostRedisplay()