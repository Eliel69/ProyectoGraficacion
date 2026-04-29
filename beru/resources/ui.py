# beru/resources/ui.py
# CORRECCIÓN:
# 1. Eliminado sys.path.insert
# 2. 'import actions.state as state' → from beru.actions import state

from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import (
    glutBitmapCharacter,
    GLUT_BITMAP_9_BY_15,
    GLUT_BITMAP_8_BY_13,
    glutPostRedisplay,
)
from beru.actions import state                        # CORREGIDO

_ABOUT = [
    "  BERU  -  Personaje 3D Interactivo",
    "",
    "  Desarrollado  : Jose Bernardo Martinez Evangelista",
    "  Materia       : Graficacion",
    "  Tema          : Examen",
]

_HELP = [
    "----  CONTROLES DE BERU  ----",
    "",
    "  MOVIMIENTO DEL PERSONAJE",
    "  W / Flecha Arriba    : Avanzar",
    "  S / Flecha Abajo     : Retroceder",
    "  A / Flecha Izquierda : Girar izquierda",
    "  D / Flecha Derecha   : Girar derecha",
    "",
    "  ACCIONES",
    "  Espacio   : Saltar",
    "  R         : Girar (Spin)",
    "  G         : Saludar",
    "  U         : Subir garras",
    "  J         : Bajar garras",
    "",
    "  EXPRESIONES (teclas 1-7)",
    "  1:Sonrisa   2:Tristeza  3:Enojo",
    "  4:Miedo     5:Duda      6:Admiracion",
    "  7:Guino",
    "",
    "  CAMARA",
    "  + / -    : Acercar / alejar zoom",
    "  Home     : Reset camara",
    "  F        : Seguir personaje",
    "",
    "  ESCENARIOS",
    "  Tab         : Siguiente",
    "  0-6         : Ir directo al escenario",
    "",
    "  OTROS",
    "  M  : Musica ON/OFF   N  : Efectos ON/OFF",
    "  H  : Teclas          P  : Acerca de",
    "  ESC: Regresar al lobby",
]

def _str(x, y, text, color=(1.0, 1.0, 1.0)):
    glColor3f(*color)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))

def _begin2d(w, h):
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

def _end2d():
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

def _panel(x, y, w, h, alpha=0.75):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 0.0, alpha)
    glBegin(GL_QUADS)
    glVertex2f(x,     y    )
    glVertex2f(x + w, y    )
    glVertex2f(x + w, y + h)
    glVertex2f(x,     y + h)
    glEnd()
    glDisable(GL_BLEND)

def draw(width, height):
    _begin2d(width, height)

    lh = 18
    yb = height - 22

    _str(18, yb,        f"Escenario : {state.scenario_names[state.current_scenario]}", (0.55, 0.80, 1.00))
    _str(18, yb - lh,   f"Expresion : {state.expression}",  (0.60, 0.95, 0.60))
    _str(18, yb - lh*2, f"Movimiento: {state.movement}",    (1.00, 0.85, 0.45))
    _str(18, yb - lh*3, f"Musica    : {'ON' if state.music_enabled else 'OFF'}", (1.00, 0.55, 0.55))
    _str(18, yb - lh*4, f"Efectos   : {'ON' if state.fx_enabled else 'OFF'}",   (1.00, 0.70, 0.40))
    _str(18, yb - lh*5, f"Camara    : {state.cam_mode}",    (0.85, 0.75, 1.00))

    if getattr(state, 'hud_msg', ''):
        _panel(width * 0.34, height - 52, 360, 30, 0.55)
        _str(width * 0.34 + 12, height - 33, state.hud_msg, (1.0, 1.0, 1.0))

    if state.show_help:
        panel_w = 500
        panel_h = 520
        px = 20
        py = height - panel_h - 20
        _panel(px, py, panel_w, panel_h, 0.82)
        yy = py + panel_h - 28
        for line in _HELP:
            _str(px + 14, yy, line, (0.90, 0.90, 0.90))
            yy -= 18

    if state.show_about:
        panel_w = 380
        panel_h = 120
        px = width - panel_w - 20
        py = 20
        _panel(px, py, panel_w, panel_h, 0.82)
        yy = py + panel_h - 28
        for line in _ABOUT:
            _str(px + 14, yy, line, (0.90, 0.90, 0.90))
            yy -= 20

    _str(width - 280, 20, "[H] Ayuda   [P] Acerca   [M/N] Audio", (0.70, 0.70, 0.70))

    _end2d()
