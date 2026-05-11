# niveles/nivel1.py
# ─────────────────────────────────────────────────────────────
# NIVEL 1 — El Valle de los Colores
#
# Objetivo pedagógico: asociar instrucciones textuales con los
# tres colores primarios (Rojo, Azul, Amarillo).
#
# Dinámica:
#  - Escenario neutro (grises/blancos).
#  - Tres cajas idénticas de colores Rojo, Azul y Amarillo.
#  - El HUD indica "¡Toca la caja [COLOR]!" alternando colores.
#  - Acierto  → animación de la caja + feedback "¡Correcto!"
#  - Error    → feedback "Ups... era otra caja"
#  - Turno por turnos: J1 y J2 se alternan la instrucción.
# ─────────────────────────────────────────────────────────────
import math, random
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *
from niveles     import state, camera, hud, players

# ── Definición de las cajas ───────────────────────────────────
_CAJAS = [
    {"id": 0, "nombre": "Roja",     "color": (0.85, 0.15, 0.15), "x": -4.5, "z":  0.0},
    {"id": 1, "nombre": "Azul",     "color": (0.15, 0.30, 0.90), "x":  0.0, "z": -3.5},
    {"id": 2, "nombre": "Amarilla", "color": (0.95, 0.85, 0.10), "x":  4.5, "z":  0.0},
]

_RADIO_CAJA  = 0.9    # radio de colisión (AABB simplificada a esfera)
_LADO_CAJA   = 1.4    # mitad del lado de la caja visual
_RADIO_JUG   = 0.5    # radio del jugador

# ── Estado interno del nivel ──────────────────────────────────
_caja_objetivo = 0      # índice de la caja que hay que tocar
_anim_caja     = {}     # {caja_id: ángulo_giro}  (animación de acierto)
_cooldown      = 0      # frames de espera entre detecciones


def _reset_nivel():
    """Reinicia todas las variables del nivel."""
    global _caja_objetivo, _anim_caja, _cooldown

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

    _anim_caja = {c["id"]: 0.0 for c in _CAJAS}
    _cooldown   = 0
    _nueva_instruccion()


def _nueva_instruccion():
    """Elige una caja objetivo aleatoria y actualiza el HUD."""
    global _caja_objetivo
    _caja_objetivo = random.randint(0, len(_CAJAS) - 1)
    nombre = _CAJAS[_caja_objetivo]["nombre"]
    jugador = "J1" if state.turno == 1 else "J2"
    state.hud_msg = f"{jugador}: !Toca la caja {nombre}!"


# ── Colisión jugador-caja ─────────────────────────────────────
def _dist2d(ax, az, bx, bz):
    return math.sqrt((ax - bx) ** 2 + (az - bz) ** 2)


def _check_colisiones():
    global _cooldown

    if _cooldown > 0:
        _cooldown -= 1
        return

    jugador_x = state.p1_x if state.turno == 1 else state.p2_x
    jugador_z = state.p1_z if state.turno == 1 else state.p2_z

    for caja in _CAJAS:
        dist = _dist2d(jugador_x, jugador_z, caja["x"], caja["z"])
        if dist < (_RADIO_CAJA + _RADIO_JUG):
            if caja["id"] == _caja_objetivo:
                # ── Acierto ──────────────────────────────────
                state.hud_feedback = "!Correcto!"
                state.hud_fb_timer  = 90
                if state.turno == 1:
                    state.score_p1 += 1
                else:
                    state.score_p2 += 1
                # Activar animación de la caja
                _anim_caja[caja["id"]] = 1.0
            else:
                # ── Error ─────────────────────────────────────
                state.hud_feedback = "Ups... era otra caja"
                state.hud_fb_timer  = 80

            # Alternar turno y nueva instrucción
            state.turno = 2 if state.turno == 1 else 1
            _cooldown = 60   # ~1 segundo de pausa
            _nueva_instruccion()
            break


# ── Dibujo del escenario ──────────────────────────────────────
def _draw_floor():
    """Piso gris neutro, cuadrícula sutil."""
    glDisable(GL_LIGHTING)

    # Suelo base
    glColor3f(0.70, 0.70, 0.70)
    glBegin(GL_QUADS)
    glVertex3f(-15, -0.01,  15)
    glVertex3f( 15, -0.01,  15)
    glVertex3f( 15, -0.01, -15)
    glVertex3f(-15, -0.01, -15)
    glEnd()

    # Cuadrícula
    glColor3f(0.60, 0.60, 0.60)
    glLineWidth(0.5)
    glBegin(GL_LINES)
    for i in range(-15, 16, 3):
        glVertex3f(i, 0.0,  15); glVertex3f(i, 0.0, -15)
        glVertex3f(-15, 0.0, i); glVertex3f( 15, 0.0, i)
    glEnd()
    glLineWidth(1.0)

    glEnable(GL_LIGHTING)


def _draw_cajas():
    """Dibuja las tres cajas de color, con animación si hay acierto."""
    for caja in _CAJAS:
        glPushMatrix()
        glTranslatef(caja["x"], 0.0, caja["z"])

        # Animación de giro al acertar
        spin = _anim_caja.get(caja["id"], 0.0)
        if spin > 0.0:
            glRotatef(spin * 360.0, 0, 1, 0)

        # Color
        glDisable(GL_LIGHTING)
        r, g, b = caja["color"]

        # Si es la objetivo, resaltar con borde brillante
        if caja["id"] == _caja_objetivo:
            glColor3f(min(r + 0.20, 1.0),
                      min(g + 0.20, 1.0),
                      min(b + 0.20, 1.0))
        else:
            glColor3f(r, g, b)

        # Cara superior
        s = _LADO_CAJA
        glBegin(GL_QUADS)
        # Arriba
        glVertex3f(-s, s*2,  s); glVertex3f( s, s*2,  s)
        glVertex3f( s, s*2, -s); glVertex3f(-s, s*2, -s)
        # Frente
        glVertex3f(-s, 0,  s); glVertex3f( s, 0,  s)
        glVertex3f( s, s*2, s); glVertex3f(-s, s*2, s)
        # Atrás
        glVertex3f( s, 0, -s); glVertex3f(-s, 0, -s)
        glVertex3f(-s, s*2,-s); glVertex3f( s, s*2,-s)
        # Izquierda
        glVertex3f(-s, 0, -s); glVertex3f(-s, 0,  s)
        glVertex3f(-s, s*2, s); glVertex3f(-s, s*2,-s)
        # Derecha
        glVertex3f( s, 0,  s); glVertex3f( s, 0, -s)
        glVertex3f( s, s*2,-s); glVertex3f( s, s*2, s)
        # Abajo
        glVertex3f(-s, 0, -s); glVertex3f( s, 0, -s)
        glVertex3f( s, 0,  s); glVertex3f(-s, 0,  s)
        glEnd()

        glEnable(GL_LIGHTING)
        glPopMatrix()


# ── API pública (misma interfaz que los personajes) ───────────

def init():
    """Llamado por el arcade al entrar al nivel 1 por primera vez."""
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 10.0, 5.0, 0.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.35, 0.35, 0.35, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.80, 0.80, 0.80, 1.0])
    _reset_nivel()


def reset():
    """Llamado cada vez que se vuelve a entrar al nivel."""
    _reset_nivel()


def display(draw_p1, draw_p2):
    """
    Renderiza el nivel completo.
    draw_p1 / draw_p2 : funciones de dibujo del modelo del personaje
    seleccionado (sin argumentos, centrado en el origen).
    """
    w = state.WIN_W
    h = state.WIN_H

    # Fondo blanco-grisáceo
    glClearColor(0.88, 0.88, 0.88, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Cámara compartida
    camera.apply(w, h)

    # Escenario
    _draw_floor()
    _draw_cajas()

    # Personajes
    players.draw_players(draw_p1, draw_p2)

    # HUD 2D encima de todo
    hud.draw(nivel_num=1)

    glutSwapBuffers()


def update(_value):
    """Lógica por frame: mueve jugadores, detecta colisiones, temporizadores."""
    global _anim_caja

    players.update()
    _check_colisiones()

    # Avanzar animación de cajas
    for cid in _anim_caja:
        if _anim_caja[cid] > 0.0:
            _anim_caja[cid] = max(0.0, _anim_caja[cid] - 0.025)

    # Bajar temporizador de feedback
    if state.hud_fb_timer > 0:
        state.hud_fb_timer -= 1
        if state.hud_fb_timer == 0:
            state.hud_feedback = ""


def keyboard(key, _x, _y):
    """Teclas ASCII — controles de J1 (WASD)."""
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
    """Teclas especiales — controles de J2 (Flechas)."""
    if key == GLUT_KEY_UP:    state.k_up    = True
    elif key == GLUT_KEY_DOWN:  state.k_down  = True
    elif key == GLUT_KEY_LEFT:  state.k_left  = True
    elif key == GLUT_KEY_RIGHT: state.k_right = True


def special_keys_up(key, _x, _y):
    if key == GLUT_KEY_UP:    state.k_up    = False
    elif key == GLUT_KEY_DOWN:  state.k_down  = False
    elif key == GLUT_KEY_LEFT:  state.k_left  = False
    elif key == GLUT_KEY_RIGHT: state.k_right = False
