# niveles/hud.py
# ─────────────────────────────────────────────────────────────
# HUD compartido para los tres niveles.
# Dibuja en 2D sobre la escena 3D:
#   • Instrucción activa ("¡Toca la caja Azul!")
#   • Feedback inmediato ("¡Correcto!" / "Ups...")
#   • Puntaje de cada jugador
#   • Etiquetas J1 / J2 con controles
#   • Número de nivel actual
# ─────────────────────────────────────────────────────────────
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *
from niveles     import state


# ─── utilidad de texto ───────────────────────────────────────
def _txt(x, y, texto, fuente=GLUT_BITMAP_HELVETICA_12, color=(1, 1, 1)):
    glColor3fv(color)
    glRasterPos2f(x, y)
    for c in texto:
        glutBitmapCharacter(fuente, ord(c))


def _enter_2d():
    """Cambia a proyección ortográfica 2D para el HUD."""
    w = glutGet(GLUT_WINDOW_WIDTH)
    h = glutGet(GLUT_WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    # (0,0) = esquina inferior-izquierda
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    return w, h


def _leave_2d():
    """Restaura el estado 3D."""
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()


# ─── dibujo principal del HUD ────────────────────────────────
def draw(nivel_num):
    """
    Dibuja el HUD completo.
    nivel_num : 1, 2 o 3 (para mostrar el título)
    """
    w, h = _enter_2d()

    # ── Barra superior oscura ────────────────────────────────
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 0.0, 0.55)
    glBegin(GL_QUADS)
    glVertex2f(0, h);  glVertex2f(w, h)
    glVertex2f(w, h - 48); glVertex2f(0, h - 48)
    glEnd()
    glDisable(GL_BLEND)

    # ── Número de nivel ──────────────────────────────────────
    _txt(10, h - 20,
         f"NIVEL {nivel_num}",
         GLUT_BITMAP_HELVETICA_18, (1.0, 0.85, 0.20))

    # ── Instrucción centrada ──────────────────────────────────
    if state.hud_msg:
        chars = len(state.hud_msg) * 9   # ancho aproximado a 18px
        _txt(w // 2 - chars // 2, h - 20,
             state.hud_msg,
             GLUT_BITMAP_HELVETICA_18, (0.20, 1.00, 0.60))

    # ── Puntaje ───────────────────────────────────────────────
    _txt(w - 220, h - 20,
         f"J1: {state.score_p1}   J2: {state.score_p2}",
         GLUT_BITMAP_HELVETICA_18, (0.90, 0.90, 1.00))

    # ── Feedback (mensaje temporal de correcto/incorrecto) ────
    if state.hud_feedback:
        color = (0.20, 1.00, 0.30) if "orrecto" in state.hud_feedback else (1.0, 0.35, 0.35)
        chars2 = len(state.hud_feedback) * 11
        _txt(w // 2 - chars2 // 2, h // 2,
             state.hud_feedback,
             GLUT_BITMAP_HELVETICA_18, color)

    # ── Etiquetas de jugadores (esquinas inferiores) ──────────
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # J1 — azul
    glColor4f(0.10, 0.40, 0.90, 0.70)
    glBegin(GL_QUADS)
    glVertex2f(0, 0); glVertex2f(200, 0)
    glVertex2f(200, 38); glVertex2f(0, 38)
    glEnd()
    _txt(8, 22,  "J1  W/S/A/D — mover",
         GLUT_BITMAP_HELVETICA_12, (0.80, 0.90, 1.00))

    # J2 — verde
    glColor4f(0.10, 0.60, 0.20, 0.70)
    glBegin(GL_QUADS)
    glVertex2f(w - 200, 0); glVertex2f(w, 0)
    glVertex2f(w, 38); glVertex2f(w - 200, 38)
    glEnd()
    _txt(w - 195, 22, "J2  Flechas — mover",
         GLUT_BITMAP_HELVETICA_12, (0.80, 1.00, 0.85))

    glDisable(GL_BLEND)

    # ── ESC para volver ───────────────────────────────────────
    _txt(w // 2 - 90, 14,
         "ESC: volver al lobby",
         GLUT_BITMAP_HELVETICA_12, (0.60, 0.60, 0.60))

    _leave_2d()
