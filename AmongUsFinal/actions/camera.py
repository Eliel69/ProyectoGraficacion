# camera.py
# Implementación de cámara interactiva s
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
from AmongUsFinal.actions import state 
from AmongUsFinal.resources import input_handlers

cam_pos = [0.0, 1.5, 6.0]  # Posición inicial en el espacio 3D (x, y, z)
yaw = 0.0                  # Ángulo de rotación horizontal (paneo)
pitch = 0.0                # Ángulo de inclinación vertical

cam_speed = 0.2            # Velocidad de traslación
mouse_down = False         # Bandera para el estado del clic izquierdo
last_mouse_x = 0           # Última posición X del cursor
last_mouse_y = 0           # Última posición Y del cursor

def apply_camera():
    global cam_pos, yaw, pitch

    # OpenGL no mueve la cámara, mueve el mundo en dirección opuesta.
   
    glRotatef(-pitch, 1.0, 0.0, 0.0)
    glRotatef(-yaw, 0.0, 1.0, 0.0)
    # Se traslada la escena en dirección opuesta a la posición de la cámara
    glTranslatef(-cam_pos[0], -cam_pos[1], -cam_pos[2])

def handle_special_keys(key, x, y):
    global cam_pos, yaw

    # Cálculo del vector direccional 
    # El seno y coseno del ángulo Yaw determinan cuánto nos movemos en X y Z.
    forward = [
        math.sin(math.radians(yaw)),
        0,
        -math.cos(math.radians(yaw))
    ]
    
    # Cálculo del vector "right" para movimiento lateral.
    right = [
        math.cos(math.radians(yaw)),
        0,
        math.sin(math.radians(yaw))
    ]

    # Actualización de la posición sumando o restando los vectores multiplicados por la velocidad
    if key == GLUT_KEY_UP:
        cam_pos[0] += forward[0] * cam_speed
        cam_pos[2] += forward[2] * cam_speed

    elif key == GLUT_KEY_DOWN:
        cam_pos[0] -= forward[0] * cam_speed
        cam_pos[2] -= forward[2] * cam_speed

    elif key == GLUT_KEY_LEFT:
        cam_pos[0] -= right[0] * cam_speed
        cam_pos[2] -= right[2] * cam_speed

    elif key == GLUT_KEY_RIGHT:
        cam_pos[0] += right[0] * cam_speed
        cam_pos[2] += right[2] * cam_speed

    # Solicita a GLUT que vuelva a renderizar la escena con la nueva posición
    glutPostRedisplay()

def mouse(button, button_state, x, y):
    global mouse_down, last_mouse_x, last_mouse_y

    # Detecta si el botón izquierdo está presionado para habilitar la rotación de cámara
    if button == GLUT_LEFT_BUTTON:
        mouse_down = (button_state == GLUT_DOWN)
        last_mouse_x = x
        last_mouse_y = y

    # Eventos de la rueda del ratón (Scroll) para rotar el modelo desde el estado global
    elif button == 3:
        state.rotate_y += 5.0
        glutPostRedisplay()

    elif button == 4:
        state.rotate_y -= 5.0
        glutPostRedisplay()

def motion(x, y):
    global yaw, pitch, last_mouse_x, last_mouse_y

    # Si no se está haciendo clic, no se calcula el movimiento
    if not mouse_down:
        return

    # Cálculo del diferencial de movimiento del ratón
    dx = x - last_mouse_x
    dy = y - last_mouse_y

    # Ajuste de sensibilidad (0.2) y actualización de ángulos
    yaw += dx * 0.2
    pitch += dy * 0.2
    
    # Restricción del ángulo pitch entre -89 y 89 grados 
    pitch = max(-89, min(89, pitch))

    # Actualiza las últimas posiciones del ratón
    last_mouse_x = x
    last_mouse_y = y

    glutPostRedisplay()


def reset_camera():
    global cam_pos, yaw, pitch
    cam_pos = [0.0, 1.5, 6.0]
    yaw = 0.0
    pitch = 0.0
    state.zoom = 45.0 # Resetea el zoom
    glutPostRedisplay()