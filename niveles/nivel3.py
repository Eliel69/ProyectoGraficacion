# niveles/nivel3.py
# ─────────────────────────────────────────────────────────────
# NIVEL 3 — Las Cuevas del Sonido
#
# Objetivo pedagógico: memoria auditiva y atención sostenida.
#
# Dinámica:
#  - Tres cristales idénticos (mismo color, misma forma).
#  - Al inicio se anuncia el sonido objetivo con un HUD.
#  - Al acercarse a un cristal, éste "brilla" (pista visual de
#    proximidad) y reproduce un sonido distintivo de proximidad.
#  - Solo uno tiene el sonido correcto → al colisionar con el
#    correcto se activa el MEGA-COMBO.
#  - Si pygame no está disponible el nivel funciona igual pero
#    sin audio (degradación elegante).
# ─────────────────────────────────────────────────────────────
import math, random, os
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *
from niveles     import state, camera, hud, players

# ── Intentar cargar pygame para el sonido ─────────────────────
try:
    import pygame
    pygame.mixer.init()
    _AUDIO = True
except Exception:
    _AUDIO = False

# ── Nombres descriptivos de los sonidos objetivo ─────────────
_SONIDOS_OBJETIVO = ["Leon", "Flauta", "Campana"]

# ── Cristales: misma forma, mismo color base ─────────────────
_CRISTALES = [
    {"id": 0, "x": -4.5, "z":  0.0, "sonido_idx": 0},
    {"id": 1, "x":  0.0, "z": -4.5, "sonido_idx": 1},
    {"id": 2, "x":  4.5, "z":  0.0, "sonido_idx": 2},
]

_RADIO_CRISTAL  = 0.9
_RADIO_PROX     = 3.0   # distancia para "brillo de proximidad"
_RADIO_JUG      = 0.5

# ── Estado interno ────────────────────────────────────────────
_sonido_correcto = 0     # índice de _SONIDOS_OBJETIVO
_cristal_correcto = 0    # id del cristal que tiene ese sonido
_mega_combo       = False
_mega_timer       = 0
_brillo           = {}   # {cristal_id: intensidad 0.0-1.0}
_cooldown         = 0


def _reset_nivel():
    global _sonido_correcto, _cristal_correcto
    global _mega_combo, _mega_timer, _brillo, _cooldown

    state.p1_x = -2.0;  state.p1_z =  0.0;  state.p1_rot = 0.0
    state.p2_x =  2.0;  state.p2_z =  0.0;  state.p2_rot = 180.0
    state.p1_walking = state.p2_walking = False
    state.p1_anim    = state.p2_anim    = 0.0
    state.k_w = state.k_s = state.k_a = state.k_d    = False
    state.k_up = state.k_down = state.k_left = state.k_right = False

    state.score_p1 = state.score_p2 = 0
    state.hud_feedback = ""
    state.hud_fb_timer  = 0
    state.turno = 1
    state.nivel_completado = False

    _mega_combo  = False
    _mega_timer  = 0
    _brillo = {c["id"]: 0.0 for c in _CRISTALES}
    _cooldown = 0

    # Asignar el cristal correcto de forma aleatoria
    _cristal_correcto = random.randint(0, len(_CRISTALES) - 1)
    _sonido_correcto  = _CRISTALES[_cristal_correcto]["sonido_idx"]

    _anunciar_sonido()


def _anunciar_sonido():
    """Muestra en el HUD el nombre del sonido que hay que buscar."""
    nombre = _SONIDOS_OBJETIVO[_sonido_correcto]
    jugador = "J1" if state.turno == 1 else "J2"
    state.hud_msg = f"{jugador}: Busca el cristal del {nombre}"


def _dist2d(ax, az, bx, bz):
    return math.sqrt((ax - bx) ** 2 + (az - bz) ** 2)


def _check_proximidad_y_colision():
    """Actualiza brillo por proximidad y detecta colisión."""
    global _cooldown, _mega_combo, _mega_timer

    if _cooldown > 0:
        _cooldown -= 1
        return

    jx = state.p1_x if state.turno == 1 else state.p2_x
    jz = state.p1_z if state.turno == 1 else state.p2_z

    for cristal in _CRISTALES:
        dist = _dist2d(jx, jz, cristal["x"], cristal["z"])

        # Calcular brillo de proximidad (1.0 cuando está muy cerca)
        if dist < _RADIO_PROX:
            _brillo[cristal["id"]] = 1.0 - (dist / _RADIO_PROX)
        else:
            _brillo[cristal["id"]] = 0.0

        # Colisión real
        if dist < (_RADIO_CRISTAL + _RADIO_JUG):
            if cristal["id"] == _cristal_correcto:
                # ── MEGA-COMBO ───────────────────────────────
                state.hud_feedback = "!MEGA-COMBO! !Cristal correcto!"
                state.hud_fb_timer  = 150
                if state.turno == 1: state.score_p1 += 3
                else:                state.score_p2 += 3
                _mega_combo = True
                _mega_timer = 120
            else:
                state.hud_feedback = "Ese cristal no suena igual..."
                state.hud_fb_timer  = 80

            state.turno = 2 if state.turno == 1 else 1
            _cooldown = 80
            _reset_cristales()
            break


def _reset_cristales():
    """Elige nuevo cristal correcto y actualiza instrucción."""
    global _cristal_correcto, _sonido_correcto
    _cristal_correcto = random.randint(0, len(_CRISTALES) - 1)
    _sonido_correcto  = _CRISTALES[_cristal_correcto]["sonido_idx"]
    _anunciar_sonido()


# ── Dibujo del escenario ──────────────────────────────────────
def _draw_cave():
    """Suelo de cueva oscuro con toques de púrpura."""
    glDisable(GL_LIGHTING)
    glColor3f(0.12, 0.08, 0.18)
    glBegin(GL_QUADS)
    glVertex3f(-16, -0.01,  16); glVertex3f( 16, -0.01,  16)
    glVertex3f( 16, -0.01, -16); glVertex3f(-16, -0.01, -16)
    glEnd()
    glEnable(GL_LIGHTING)


def _draw_cristales():
    """
    Dibuja los tres cristales.
    El brillo de proximidad mezcla el color base con blanco.
    Durante el mega-combo el cristal correcto pulsa con colores.
    """
    global _mega_timer

    for cristal in _CRISTALES:
        glPushMatrix()
        glTranslatef(cristal["x"], 0.0, cristal["z"])

        b = _brillo.get(cristal["id"], 0.0)

        if _mega_combo and cristal["id"] == _cristal_correcto:
            # Pulso de colores del mega-combo
            t = _mega_timer / 120.0
            r = 0.5 + 0.5 * math.sin(t * math.pi * 6)
            g = 0.5 + 0.5 * math.sin(t * math.pi * 6 + 2)
            blue = 0.5 + 0.5 * math.sin(t * math.pi * 6 + 4)
            glColor3f(r, g, blue)
        else:
            # Color base: azul-cian, aclarado por proximidad
            base_r = 0.30 + b * 0.50
            base_g = 0.70 + b * 0.30
            base_b = 0.90 + b * 0.10
            glColor3f(base_r, base_g, base_b)

        glDisable(GL_LIGHTING)

        # Cuerpo del cristal: prisma hexagonal simplificado
        q = gluNewQuadric()
        gluCylinder(q, 0.35, 0.05, 2.0, 6, 3)   # tronco que afina
        glPushMatrix(); glRotatef(180, 1, 0, 0)
        gluDisk(q, 0, 0.35, 6, 1)
        glPopMatrix()

        # Base más ancha (plataforma)
        glPushMatrix(); glTranslatef(0, -0.05, 0)
        gluCylinder(q, 0.55, 0.35, 0.15, 6, 1)
        glRotatef(180, 1, 0, 0); gluDisk(q, 0, 0.55, 6, 1)
        glPopMatrix()

        gluDeleteQuadric(q)
        glEnable(GL_LIGHTING)
        glPopMatrix()

    # Indicador de "brillo" encima del cristal objetivo (corona de luz)
    for cristal in _CRISTALES:
        if cristal["id"] == _cristal_correcto:
            b2 = _brillo.get(cristal["id"], 0.0)
            if b2 > 0.05:
                _draw_corona(cristal["x"], 2.3, cristal["z"], b2)


def _draw_corona(cx, cy, cz, intensidad):
    """Pequeños destellos en arco encima del cristal objetivo."""
    glDisable(GL_LIGHTING)
    glColor4f(1.0, 1.0, 0.6, intensidad)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glPointSize(4.0)
    glBegin(GL_POINTS)
    for i in range(8):
        angle = 2 * math.pi * i / 8
        glVertex3f(cx + 0.5 * math.cos(angle),
                   cy,
                   cz + 0.5 * math.sin(angle))
    glEnd()
    glPointSize(1.0)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)


# ── API pública ───────────────────────────────────────────────

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    # Luz tenue, azulada (cueva)
    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 8.0, 4.0, 0.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.10, 0.08, 0.20, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.50, 0.50, 0.80, 1.0])
    _reset_nivel()


def reset():
    _reset_nivel()


def display(draw_p1, draw_p2):
    w = state.WIN_W
    h = state.WIN_H

    # Durante mega-combo el fondo pulsa
    if _mega_combo:
        t = _mega_timer / 120.0
        glClearColor(0.05 + 0.15 * t, 0.0, 0.15 + 0.20 * t, 1.0)
    else:
        glClearColor(0.05, 0.02, 0.12, 1.0)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    camera.apply(w, h)
    _draw_cave()
    _draw_cristales()
    players.draw_players(draw_p1, draw_p2)
    hud.draw(nivel_num=3)

    glutSwapBuffers()


def update(_value):
    global _mega_combo, _mega_timer

    players.update()
    _check_proximidad_y_colision()

    if _mega_timer > 0:
        _mega_timer -= 1
        if _mega_timer == 0:
            _mega_combo = False

    if state.hud_fb_timer > 0:
        state.hud_fb_timer -= 1
        if state.hud_fb_timer == 0:
            state.hud_feedback = ""


def keyboard(key, _x, _y):
    if key == b'w': state.k_w = True
    elif key == b's': state.k_s = True
    elif key == b'a': state.k_a = True
    elif key == b'd': state.k_d = True


def keyboard_up(key, _x, _y):
    if key == b'w': state.k_w = False
    elif key == b's': state.k_s = False
    elif key == b'a': state.k_a = False
    elif key == b'd': state.k_d = False


def special_keys(key, _x, _y):
    if key == GLUT_KEY_UP:    state.k_up    = True
    elif key == GLUT_KEY_DOWN:  state.k_down  = True
    elif key == GLUT_KEY_LEFT:  state.k_left  = True
    elif key == GLUT_KEY_RIGHT: state.k_right = True


def special_keys_up(key, _x, _y):
    if key == GLUT_KEY_UP:    state.k_up    = False
    elif key == GLUT_KEY_DOWN:  state.k_down  = False
    elif key == GLUT_KEY_LEFT:  state.k_left  = False
    elif key == GLUT_KEY_RIGHT: state.k_right = False
