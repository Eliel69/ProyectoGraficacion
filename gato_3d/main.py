# gato_3d/main.py
# CORRECCIÓN: Añadido puente update(value) para el arcade.
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from gato_3d.actions import state, camera, update, ui_overlay
from gato_3d.resources import grid, scenes, input_handlers, sounds
from gato_3d.cat_character import cat

def init():
    glClearColor(0.12, 0.12, 0.18, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 8.0, 5.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.5, 0.5, 0.5, 1.0])
    sounds.init()
    sounds.play_scene(state.current_scene)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    camera.setup_camera()
    grid.draw_grid()
    scenes.draw_scenarios()

    glPushMatrix()
    glTranslatef(state.char_x, -1.21 + state.char_y, state.char_z)
    cat.draw_cat()
    glPopMatrix()

    ui_overlay.draw_ui()
    glutSwapBuffers()

def reshape(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(w)/float(h), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def timer(v):
    """Timer propio para modo standalone."""
    update.update_logic()
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)

# ==========================================================
# PUENTES PARA EL ARCADE
# ==========================================================

def update(value):
    """NUEVO PUENTE: Ejecuta sólo la lógica, sin re-registrar el timer."""
    from gato_3d.actions import update as upd_mod
    upd_mod.update_logic()

def keyboard(key, x, y):
    if hasattr(input_handlers, 'keyboard'):
        input_handlers.keyboard(key, x, y)

def special_keys(key, x, y):
    if hasattr(input_handlers, 'special_keys'):
        input_handlers.special_keys(key, x, y)

def mouse(button, state_btn, x, y):
    # gato usa mouse_wheel en lugar de glutMouseFunc estándar;
    # el scroll se maneja aquí manualmente para compatibilidad con el arcade.
    if button == 3 and state_btn == GLUT_DOWN:
        state.cam_radius -= 0.5
        glutPostRedisplay()
    elif button == 4 and state_btn == GLUT_DOWN:
        state.cam_radius += 0.5
        glutPostRedisplay()

def motion(x, y):
    pass  # gato usa mouse_wheel, no drag; se puede ampliar si se necesita

# ==========================================================
# MODO STANDALONE
# ==========================================================
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 700)
    glutCreateWindow(b"Proyecto Graficacion - Gato 3D")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(input_handlers.keyboard)
    glutSpecialFunc(input_handlers.special_keys)
    glutMouseWheelFunc(input_handlers.mouse_wheel)
    glutTimerFunc(16, timer, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
