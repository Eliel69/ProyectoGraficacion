# actions/ui_overlay.py
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from gato_3d.actions import state

_W, _H = 1000, 700   # Dimensiones de la ventana

def draw_ui():
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, _W, 0, _H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()

    # ── HUD permanente (esquina inferior izquierda) ───────────────────────────
    _rect(8, 8, 290, 90, (0.0, 0.0, 0.0, 0.65))
    glColor3f(0.8, 0.95, 1.0)
    _text(16, 82, "Gato 3D — Graficacion 2026-A")
    _text(16, 64, f"Escena : {state.current_scene}   Movim: {state.current_motion}")
    _text(16, 46, f"Expresion: {state.current_expression}")
    _text(16, 28, f"Sonido: {'ON  [M para apagar]' if state.sound_enabled else 'OFF [M para activar]'}")

    # ── Indicador de colisión activa ──────────────────────────────────────────
    any_hit = any(o["hit"] for o in state.collision_objects)
    if any_hit:
        hit_obj = next(o for o in state.collision_objects if o["hit"])
        _rect(8, 94, 290, 22, (0.8, 0.1, 0.05, 0.80))
        glColor3f(1.0, 1.0, 0.3)
        _text(16, 100, f"¡COLISION con {hit_obj['type'].upper()}! Color cambiado")

    # ── Indicador de tecla H ──────────────────────────────────────────────────
    glColor3f(0.6, 0.9, 0.6)
    _text(8, 96, "[H] Instrucciones   [I] Acerca de")

    # ── SECCIÓN ACERCA DE (tecla I) ───────────────────────────────────────────
    if state.show_info:
        _rect(8, _H - 180, 400, 170, (0.05, 0.05, 0.15, 0.90))
        glColor3f(0.4, 0.85, 1.0)
        _text(20, _H - 24, "━━━  ACERCA DE  ━━━")
        glColor3f(1, 1, 1)
        _text(20, _H - 46, "Instituto Tecnológico de Toluca")
        _text(20, _H - 66, "Carrera: Ing. en Sistemas Computacionales")
        _text(20, _H - 86, "Materia: Graficación   Periodo: 2026-A")
        _text(20, _H - 106, "Profesar: Rocio Elizabeth Pulido Alba")
        _text(20, _H - 126, "Alumno:   Brenda Luz Ramirez Garcia")
        _text(20, _H - 146, "Núm. Control: 25282222")
        glColor3f(0.5, 0.8, 0.5)
        _text(20, _H - 170, "Presiona [I] para cerrar")

    # ── INSTRUCCIONES (tecla H) ───────────────────────────────────────────────
    if state.show_instructions:
        _rect(_W - 310, 8, 302, 440, (0.05, 0.10, 0.20, 0.92))
        glColor3f(0.4, 0.85, 1.0)
        _text(_W - 300, 432, "━━━  CONTROLES  ━━━")
        glColor3f(1, 1, 1)
        lines = [
            "── CÁMARA ──────────────",
            "Flechas ◄ ►  : Rotar horizontal",
            "Flechas ▲▼  : Rotar vertical",
            "RePág / AvPág: Zoom +/-",
            "C : Reset cámara",
            "",
            "── ESCENARIOS ──────────",
            "Teclas 1-7  : Cambiar escenario",
            "",
            "── MOVIMIENTOS ─────────",
            "Q : Caminar    W : Saltar",
            "E : Saludar    R : Brazos arriba",
            "T : Girar      Y : Agacharse",
            "U : Bailar     S : Detener",
            "",
            "── EXPRESIONES ─────────",
            "F1: Guiño      F2: Felicidad",
            "F3: Tristeza   F4: Miedo",
            "F5: Enojo      F6: Duda",
            "F7: Admiración F8: Neutral",
            "",
            "── GENERAL ─────────────",
            "M : Sonido ON/OFF",
            "I : Acerca de",
            "H : Cerrar instrucciones",
        ]
        for idx, line in enumerate(lines):
            col = (0.4, 0.85, 1.0) if line.startswith("──") else (1, 1, 1)
            glColor3f(*col)
            _text(_W - 300, 410 - idx * 15, line)

    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _text(x, y, text, font=GLUT_BITMAP_HELVETICA_12):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

def _rect(x, y, w, h, color):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x,   y);   glVertex2f(x+w, y)
    glVertex2f(x+w, y+h); glVertex2f(x,   y+h)
    glEnd()
    glDisable(GL_BLEND)
