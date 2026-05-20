# totoro/main.py
# CORRECCIONES:
# 1. Añadida función init() para que el arcade pueda inicializar luces y audio.
# 2. Añadido puente update(value) para que el arcade actualice animaciones.
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GLUT as glut
import sys

from totoro.caracteres import totoro
from totoro.actions import camara, state
from totoro.actions import update as update_module
from totoro.resources import input_handlers, grid, sound_manager
def stop_audio():
    """Para todo el audio al salir al lobby."""
    try:
        sound_manager.stop_music()
        sound_manager.stop_walk()
        import pygame
        pygame.mixer.stop()
    except Exception:
        pass


def init():
    """Inicialización de OpenGL + audio. Llamado por el arcade al activar este personaje."""
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    glLightfv(GL_LIGHT0, GL_POSITION, [8.0, 8.0, 10.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.9, 0.9, 0.9, 1.0])
    glClearColor(0.68, 0.85, 1.0, 1.0)
    sound_manager.load_sounds()
    sound_manager.play_music()

def draw_text(x, y, text):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, 900, 0, 700)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix(); glLoadIdentity()
    glDisable(GL_LIGHTING)
    glColor3f(0.0, 0.0, 0.0)
    glRasterPos2f(x, y)
    for ch in text:
        glut.glutBitmapCharacter(glut.GLUT_BITMAP_HELVETICA_18, ord(ch))
    glEnable(GL_LIGHTING)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_instructions():
    y = 660
    lines = [
        "INSTRUCCIONES:",
        "W = caminar       J = saltar",
        "K = girar         S = temblar",
        "H = elevar brazos L = mover piernas",
        "Y = feliz  A = triste  D = sorprendido",
        "N = neutral  M = enojado",
        "1..4 = cambiar escenario",
        "Flechas = mover camara",
        "Mouse izq = rotar camara",
        "Scroll = zoom",
        "I = mostrar/ocultar instrucciones",
        "B = acerca de",
        "O = musica bosque on/off",
        "R = reiniciar",
        "ESC = salir al lobby",
    ]
    for line in lines:
        draw_text(20, y, line)
        y -= 25

def draw_about():
    lines = [
        "ACERCA DE:",
        "Personaje: TotoRin",
        "Inspirado en un guardian del bosque tipo Totoro",
        "Desarrollado en Python + OpenGL",
        "Proyecto academico de personaje 3D interactivo",
    ]
    y = 220
    for line in lines:
        draw_text(20, y, line)
        y -= 25

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    camara.apply_camera()
    grid.draw_current_scene()
    grid.draw_axes()

    glPushMatrix()
    glTranslatef(state.char_x, 5.0 + state.jump_offset, state.char_z)
    glRotatef(state.rotate_y + state.spin_angle, 0, 1, 0)
    glRotatef(state.rotate_x, 1, 0, 0)
    glScalef(0.7, 0.7, 0.7)
    totoro.draw_totoro_full()
    glPopMatrix()

    if state.show_instructions:
        draw_instructions()
    if state.show_about:
        draw_about()

    glutSwapBuffers()

def reshape(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, w/h, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

# ==========================================================
# PUENTES PARA EL ARCADE
# ==========================================================

def update(value):
    """NUEVO PUENTE: Ejecuta sólo la lógica, sin re-registrar el timer."""
    update_module._logic()

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
    glutInitWindowSize(900, 700)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Totoro 3D - OpenGL")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(input_handlers.keyboard)
    glutMouseFunc(input_handlers.mouse)
    glutMotionFunc(input_handlers.motion)
    glutSpecialFunc(input_handlers.special_keys)
    glutTimerFunc(16, update_module.update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
