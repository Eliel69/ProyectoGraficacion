# niveles/nivel2.py
# ─────────────────────────────────────────────────────────────
# NIVEL 2 — El Bosque de las Formas
#
# Objetivo pedagógico: reconocer geometría 3D básica
# (esfera, cubo, cilindro, cono).
#
# Dinámica:
#  - Escenario de bosque dorado (todos los objetos del mismo color
#    para no dar pista por color).
#  - 4 objetos: Esfera, Cubo, Cilindro, Cono.
#  - La instrucción pide "Encuentra el objeto redondo (Esfera)".
#  - Colisión por radio distinto según la geometría de cada forma.
#  - Turno alternado entre J1 y J2.
# ─────────────────────────────────────────────────────────────
import math, random
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *
from niveles     import state, camera, hud, players

# ── Color único para todos los objetos (dorado madera) ────────
_COLOR_OBJETO = (0.80, 0.62, 0.20)

# ── Definición de formas ──────────────────────────────────────
_FORMAS = [
    {"id": 0, "nombre": "Esfera",   "pista": "redondo",          "x": -5.0, "z":  0.0, "radio": 1.0},
    {"id": 1, "nombre": "Cubo",     "pista": "con esquinas",     "x":  0.0, "z": -4.5, "radio": 1.0},
    {"id": 2, "nombre": "Cilindro", "pista": "largo y redondo",  "x":  5.0, "z":  0.0, "radio": 0.9},
    {"id": 3, "nombre": "Cono",     "pista": "con punta arriba", "x":  0.0, "z":  4.5, "radio": 0.9},
]

_RADIO_JUG    = 0.5
_ANIM_DURACION = 80   # frames del anim de acierto

# ── Estado interno ────────────────────────────────────────────
_forma_objetivo = 0
_anim_forma     = {}   # {forma_id: frames_restantes}
_cooldown       = 0


def _reset_nivel():
    global _forma_objetivo, _anim_forma, _cooldown

    state.p1_x = -2.0;  state.p1_z =  1.0;  state.p1_rot = 0.0
    state.p2_x =  2.0;  state.p2_z =  1.0;  state.p2_rot = 180.0
    state.p1_walking = state.p2_walking = False
    state.p1_anim    = state.p2_anim    = 0.0
    state.k_w = state.k_s = state.k_a = state.k_d    = False
    state.k_up = state.k_down = state.k_left = state.k_right = False

    state.score_p1 = state.score_p2 = 0
    state.hud_feedback = ""
    state.hud_fb_timer  = 0
    state.turno = 1
    state.nivel_completado = False

    _anim_forma = {f["id"]: 0 for f in _FORMAS}
    _cooldown    = 0
    _nueva_instruccion()


def _nueva_instruccion():
    global _forma_objetivo
    _forma_objetivo = random.randint(0, len(_FORMAS) - 1)
    forma   = _FORMAS[_forma_objetivo]
    jugador = "J1" if state.turno == 1 else "J2"
    state.hud_msg = (f"{jugador}: Encuentra el objeto "
                     f"{forma['pista']} ({forma['nombre']})")


def _dist2d(ax, az, bx, bz):
    return math.sqrt((ax - bx) ** 2 + (az - bz) ** 2)


def _check_colisiones():
    global _cooldown
    if _cooldown > 0:
        _cooldown -= 1
        return

    jx = state.p1_x if state.turno == 1 else state.p2_x
    jz = state.p1_z if state.turno == 1 else state.p2_z

    for forma in _FORMAS:
        dist = _dist2d(jx, jz, forma["x"], forma["z"])
        if dist < (forma["radio"] + _RADIO_JUG):
            if forma["id"] == _forma_objetivo:
                state.hud_feedback = "!Forma correcta!"
                state.hud_fb_timer  = 90
                if state.turno == 1: state.score_p1 += 1
                else:                state.score_p2 += 1
                _anim_forma[forma["id"]] = _ANIM_DURACION
            else:
                state.hud_feedback = "No era esa forma..."
                state.hud_fb_timer  = 80

            state.turno = 2 if state.turno == 1 else 1
            _cooldown = 60
            _nueva_instruccion()
            break


# ── Dibujo del escenario ──────────────────────────────────────
def _draw_floor():
    glDisable(GL_LIGHTING)

    # Suelo verde-bosque oscuro
    glColor3f(0.22, 0.45, 0.18)
    glBegin(GL_QUADS)
    glVertex3f(-16, -0.01,  16); glVertex3f( 16, -0.01,  16)
    glVertex3f( 16, -0.01, -16); glVertex3f(-16, -0.01, -16)
    glEnd()

    glEnable(GL_LIGHTING)

    # Árboles decorativos en las esquinas
    for tx, tz in [(-12, -12), (12, -12), (-12, 12), (12, 12),
                   (-8, -14), (8, -14),  (0, -13)]:
        _draw_tree(tx, tz)


def _draw_tree(cx, cz):
    glDisable(GL_LIGHTING)
    # Tronco
    glColor3f(0.42, 0.26, 0.10)
    q = gluNewQuadric()
    glPushMatrix()
    glTranslatef(cx, 0, cz)
    gluCylinder(q, 0.18, 0.14, 2.0, 8, 2)
    glPopMatrix()
    # Copa
    glColor3f(0.15, 0.55, 0.12)
    glPushMatrix()
    glTranslatef(cx, 2.0, cz)
    gluSphere(q, 1.0, 10, 10)
    glPopMatrix()
    gluDeleteQuadric(q)
    glEnable(GL_LIGHTING)


def _draw_formas():
    r, g, b = _COLOR_OBJETO
    for forma in _FORMAS:
        glPushMatrix()
        glTranslatef(forma["x"], 0.0, forma["z"])

        # Animación de ascenso cuando se acierta
        anim = _anim_forma.get(forma["id"], 0)
        if anim > 0:
            t = anim / _ANIM_DURACION       # 1 → 0
            glTranslatef(0, math.sin(t * math.pi) * 1.5, 0)

        # Color: ligeramente más brillante si es el objetivo
        if forma["id"] == _forma_objetivo:
            glColor3f(min(r + 0.15, 1.0), min(g + 0.15, 1.0), min(b + 0.15, 1.0))
        else:
            glColor3f(r, g, b)

        glDisable(GL_LIGHTING)
        fid = forma["id"]

        if fid == 0:   # Esfera
            q = gluNewQuadric()
            glTranslatef(0, 0.9, 0)
            gluSphere(q, 0.9, 20, 20)
            gluDeleteQuadric(q)

        elif fid == 1:  # Cubo
            s = 0.8
            glBegin(GL_QUADS)
            # Arriba
            glVertex3f(-s, s*2, s); glVertex3f(s, s*2, s)
            glVertex3f(s, s*2,-s); glVertex3f(-s, s*2,-s)
            # Abajo
            glVertex3f(-s, 0,-s); glVertex3f(s, 0,-s)
            glVertex3f(s, 0, s); glVertex3f(-s, 0, s)
            # Frente
            glVertex3f(-s, 0, s); glVertex3f(s, 0, s)
            glVertex3f(s, s*2, s); glVertex3f(-s, s*2, s)
            # Atrás
            glVertex3f(s, 0,-s); glVertex3f(-s, 0,-s)
            glVertex3f(-s, s*2,-s); glVertex3f(s, s*2,-s)
            # Izq
            glVertex3f(-s, 0,-s); glVertex3f(-s, 0, s)
            glVertex3f(-s, s*2, s); glVertex3f(-s, s*2,-s)
            # Der
            glVertex3f(s, 0, s); glVertex3f(s, 0,-s)
            glVertex3f(s, s*2,-s); glVertex3f(s, s*2, s)
            glEnd()

        elif fid == 2:  # Cilindro
            q = gluNewQuadric()
            gluCylinder(q, 0.55, 0.55, 1.8, 16, 4)
            # Tapas
            glPushMatrix(); glRotatef(180, 1, 0, 0)
            gluDisk(q, 0, 0.55, 16, 1); glPopMatrix()
            glPushMatrix(); glTranslatef(0, 0, 1.8)
            gluDisk(q, 0, 0.55, 16, 1); glPopMatrix()
            gluDeleteQuadric(q)

        elif fid == 3:  # Cono
            q = gluNewQuadric()
            gluCylinder(q, 0.75, 0.0, 2.0, 16, 4)
            glPushMatrix(); glRotatef(180, 1, 0, 0)
            gluDisk(q, 0, 0.75, 16, 1); glPopMatrix()
            gluDeleteQuadric(q)

        glEnable(GL_LIGHTING)
        glPopMatrix()


# ── API pública ───────────────────────────────────────────────

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    glLightfv(GL_LIGHT0, GL_POSITION, [2.0, 10.0, 5.0, 0.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.30, 0.30, 0.30, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.85, 0.85, 0.85, 1.0])
    _reset_nivel()


def reset():
    _reset_nivel()


def display(draw_p1, draw_p2):
    w = state.WIN_W
    h = state.WIN_H

    glClearColor(0.30, 0.55, 0.85, 1.0)   # cielo azul de bosque
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    camera.apply(w, h)

    _draw_floor()
    _draw_formas()
    players.draw_players(draw_p1, draw_p2)
    hud.draw(nivel_num=2)

    glutSwapBuffers()


def update(_value):
    players.update()
    _check_colisiones()

    for fid in _anim_forma:
        if _anim_forma[fid] > 0:
            _anim_forma[fid] -= 1

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
