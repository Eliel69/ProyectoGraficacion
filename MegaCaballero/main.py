# MegaCaballero/main.py
# CORRECCIONES:
# 1. update() puente llama _logic() → evita doble timer.
# 2. init() inicializa audio correctamente.
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys

from MegaCaballero.characters import MegaKknight
from MegaCaballero.utilerias.escenarios import escenarios
from MegaCaballero.actions import camera, state
from MegaCaballero.utilerias.sonidos import audio_manager
from MegaCaballero.resources import grid, input_handlers
from MegaCaballero.actions import update as logica_update
from MegaCaballero.resources import ui_menu

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    glLightfv(GL_LIGHT0, GL_POSITION, [2.0, 5.0, 5.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.8, 0.8, 0.8, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glClearColor(0.5, 0.8, 1.0, 1.0)
    audio_manager.init_audio()

def display():
    escenarios.establecer_fondo(state.current_escenario)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    w = glutGet(GLUT_WINDOW_WIDTH)
    h = glutGet(GLUT_WINDOW_HEIGHT)
    if h == 0: h = 1
    gluPerspective(state.zoom, w/h, 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    camera.apply_camera()
    escenarios.dibujar_escenario_actual(state.current_escenario)
    grid.draw_axes()

    glPushMatrix()
    glTranslatef(state.fox_x, 1.2 + state.jump_y + state.smash_y + state.crouch_y, state.fox_z)
    glRotatef(state.rotate_y + state.spin_angle, 0, 1, 0)
    glRotatef(state.rotate_x, 1, 0, 0)
    MegaKknight.draw_megaknight_full()
    glPopMatrix()

    ui_menu.draw_hud()
    glutSwapBuffers()

def reshape(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(state.zoom, w/h, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

# ==========================================================
# PUENTES PARA EL ARCADE
# ==========================================================

def update(value):
    """CORRECCIÓN: Llama _logic() sin re-registrar timer."""
    logica_update._logic()

def keyboard(key, x, y):
    if hasattr(input_handlers, 'keyboard'):
        input_handlers.keyboard(key, x, y)

def special_keys(key, x, y):
    if hasattr(input_handlers, 'special_keys'):
        input_handlers.special_keys(key, x, y)

def mouse(button, state_btn, x, y):
    if hasattr(input_handlers, 'mouse'):
        input_handlers.mouse(button, state_btn, x, y)

def motion(x, y):
    if hasattr(input_handlers, 'motion'):
        input_handlers.motion(x, y)

# ==========================================================
# MODO STANDALONE
# ==========================================================
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"MegaCaballero 3D - OpenGL")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(input_handlers.keyboard)
    glutMouseFunc(input_handlers.mouse)
    glutMotionFunc(input_handlers.motion)
    glutSpecialFunc(input_handlers.special_keys)
    glutSpecialUpFunc(input_handlers.special_keys_up)
    glutTimerFunc(16, logica_update.update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
