# beru/main.py
# CORRECCIONES:
# 1. Eliminado sys.path.insert() que rompía imports en modo arcade.
# 2. Todos los imports ya usan rutas completas de paquete.
# 3. Añadido puente update(value) para el arcade.
# 4. init_gl() expuesto como init() para que el arcade pueda llamarlo.

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys

from beru.actions import state
from beru.actions import camara
from beru.actions import update as _upd  
from beru import collisions
from beru.caracteres import beru
from beru.Utilerias import scenarios
from beru.resources import sound_manager
from beru.resources import input_handlers
from beru.resources import ui
from beru.resources import grid

WIN_W = 1024
WIN_H = 700

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)              # ← AGREGAR: evita artefactos de iluminación
                                        #   en esferas con glScalef no uniforme
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.20, 0.20, 0.30, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.85, 0.85, 1.00, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.45, 0.45, 0.55, 1.0])
    sound_manager.play_scenario(state.current_scenario)

def display():
    # ──────────────────────────────────────────────────────
    # CORRECCIÓN CRÍTICA: la cámara se aplica PRIMERO.
    # Antes, scenarios.draw() dibujaba el suelo SIN cámara
    # y el personaje/sombra CON cámara → depth test roto →
    # sombra aparecía sobre el personaje como una "dona".
    # ──────────────────────────────────────────────────────
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    camara.apply()                             # ← cámara primero

    scenarios.draw()                           # glClear interno + suelo YA con cámara
    glLightfv(GL_LIGHT0, GL_POSITION, [3.0, 6.0, 4.0, 1.0])
    grid.draw()
    collisions.draw_objects()
    beru.draw()
    ui.draw(WIN_W, WIN_H)
    glutSwapBuffers()

def reshape(w, h):
    global WIN_W, WIN_H
    WIN_W, WIN_H = w, max(h, 1)
    glViewport(0, 0, WIN_W, WIN_H)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, WIN_W / WIN_H, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def timer(value):
    """Timer propio para modo standalone."""
    update.tick()
    collisions.check()
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)

# ==========================================================
# PUENTES PARA EL ARCADE
# ==========================================================

# Puente para el arcade — reemplaza la versión rota anterior
def update(value):
    # CORRECCIÓN: _upd es el alias del módulo de lógica (import arriba).
    # La versión anterior reemplazaba 'update' en globals con la función,
    # haciendo que update.tick() llamara a update_arcade.tick() → crash.
    _upd.tick()
    collisions.check()


def keyboard(key, x, y):
    if hasattr(input_handlers, 'keyboard'):
        input_handlers.keyboard(key, x, y)

def special_keys(key, x, y):
    if hasattr(input_handlers, 'special_keys'):
        input_handlers.special_keys(key, x, y)

def mouse(button, state_btn, x, y):
    if hasattr(input_handlers, 'mouse_button'):
        input_handlers.mouse_button(button, state_btn, x, y)

def motion(x, y):
    if hasattr(input_handlers, 'mouse_motion'):
        input_handlers.mouse_motion(x, y)

# ==========================================================
# MODO STANDALONE
# ==========================================================
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutInitWindowPosition(80, 60)
    glutCreateWindow(b"BERU  -  Solo Leveling 3D")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(input_handlers.keyboard)
    glutKeyboardUpFunc(input_handlers.keyboard_up)
    glutSpecialFunc(input_handlers.special_keys)
    glutSpecialUpFunc(input_handlers.special_keys_up)
    glutMouseFunc(input_handlers.mouse_button)
    glutMotionFunc(input_handlers.mouse_motion)
    glutTimerFunc(16, timer, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
