# beru/caracteres/beru.py
# CORRECCIONES:
# 1. Import roto: 'import actions.state as state' → from beru.actions import state
# 2. BUG "DONA ENCIMA DEL PERSONAJE":
#    draw_shadow_base() se dibujaba en y = pos_y+0.48-0.10 = pos_y+0.38,
#    es decir DENTRO del cuerpo del personaje. La sombra con blend semitransparente
#    mostraba un aro plano atravesando el cuerpo, exactamente como una "dona".
#    SOLUCIÓN: La sombra se dibuja FUERA del glPushMatrix del personaje,
#    directamente en el suelo (y = 0.01).

from OpenGL.GL  import *
from OpenGL.GLU import *
from beru.actions import state                        # CORREGIDO

_BLACK     = (0.04, 0.04, 0.06)
_BLUE_NEON = (0.15, 0.55, 1.00)
_BLUE_GLOW = (0.00, 0.75, 1.00)
_DARK_BLUE = (0.05, 0.12, 0.30)
_PURPLE    = (0.35, 0.05, 0.55)
_WHITE     = (1.00, 1.00, 1.00)
_SHADOW    = (0.10, 0.00, 0.20)

def _c3(rgb):
    glColor3f(*rgb)

def _sph(r, sl=16, st=16):
    q = gluNewQuadric()
    gluSphere(q, r, sl, st)
    gluDeleteQuadric(q)

def _cyl(base, top, h, sl=12):
    q = gluNewQuadric()
    gluCylinder(q, base, top, h, sl, 3)
    gluDeleteQuadric(q)

def _cone(base, h, sl=8):
    q = gluNewQuadric()
    gluCylinder(q, base, 0.0, h, sl, 2)
    gluDeleteQuadric(q)

def draw_shadow_base(cx, cz):
    """Sombra plana usando quads — sin conflictos de depth test."""
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 0.0, 0.30)

    # Óvalo aproximado con una tira de triángulos en y=0.01
    import math
    rx, rz = 0.55, 0.45   # radios del óvalo
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(cx, 0.01, cz)
    steps = 18
    for i in range(steps + 1):
        a = 2 * math.pi * i / steps
        glVertex3f(cx + rx * math.cos(a), 0.01, cz + rz * math.sin(a))
    glEnd()

    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

def draw_body():
    glPushMatrix()
    _c3(_SHADOW)
    glScalef(0.62, 0.82, 0.48)
    _sph(1.0)
    glPopMatrix()

    for i in range(3):
        glPushMatrix()
        _c3(_BLUE_NEON)
        glTranslatef(0.0, 0.18 - i * 0.18, 0.43)
        glScalef(0.46, 0.05, 0.05)
        _sph(1.0)
        glPopMatrix()

    glPushMatrix()
    _c3(_PURPLE)
    glTranslatef(0.0, -0.02, -0.36)
    glScalef(0.56, 0.74, 0.20)
    _sph(1.0)
    glPopMatrix()

def draw_head():
    glPushMatrix()
    glTranslatef(0.0, 0.96, 0.08)
    _c3(_SHADOW)
    glScalef(0.72, 0.68, 0.62)
    _sph(1.0)
    glPopMatrix()

    for sx in (-0.42, 0.42):
        glPushMatrix()
        glTranslatef(sx, 0.94, 0.44)
        _c3(_DARK_BLUE)
        glScalef(1.0, 0.55, 0.35)
        _sph(0.20)
        glPopMatrix()

def draw_eyes():
    expr  = state.expression
    ey_sc = {
        'neutral': 1.0, 'smile': 0.80, 'sad': 0.65,
        'angry': 0.45, 'fear': 1.35, 'doubt': 0.55,
        'admire': 1.45, 'wink': 1.0
    }.get(expr, 1.0)

    for side, sx in enumerate((-0.30, 0.30)):
        glPushMatrix()
        glTranslatef(sx, 1.10, 0.50)

        if expr == 'wink' and side == 1:
            _c3(_SHADOW)
            glScalef(1.0, 0.12, 0.35)
            _sph(0.22)
            glPopMatrix()
            continue

        _c3(_BLUE_GLOW)
        glScalef(1.0, ey_sc, 0.48)
        _sph(0.26)

        glTranslatef(0.0, 0.0, 0.20)
        _c3(_BLACK)
        _sph(0.11)

        glTranslatef(0.05, 0.07, 0.05)
        _c3(_WHITE)
        _sph(0.045)
        glPopMatrix()

def draw_mouth():
    expr = state.expression
    cfgs = {
        'neutral': (0.00, 0.28, 7), 'smile':   (0.08, 0.30, 8),
        'sad':     (-0.08, 0.30, 8),'angry':   (-0.06, 0.26, 7),
        'fear':    (-0.10, 0.18, 5),'doubt':   (0.04,  0.16, 5),
        'admire':  (0.10,  0.26, 6),'wink':    (0.06,  0.26, 7),
    }
    cy, w, pts = cfgs.get(expr, (0.0, 0.26, 7))

    glPushMatrix()
    glTranslatef(0.0, 0.78, 0.58)
    _c3(_BLUE_NEON)

    for i in range(pts):
        t  = (i / (pts - 1)) - 0.5
        bx = t * w
        by = cy * (1.0 - (2 * t) ** 2)
        glPushMatrix()
        glTranslatef(bx, by, 0.0)
        _sph(0.032)
        glPopMatrix()

    glPopMatrix()

def draw_antennae():
    for sx in (-1.0, 1.0):
        glPushMatrix()
        glTranslatef(sx * 0.22, 1.48, 0.0)
        glRotatef(sx * 22, 0, 0, 1)
        _c3(_SHADOW)
        glRotatef(-82, 1, 0, 0)
        _cyl(0.030, 0.022, 0.42)
        glTranslatef(0.0, 0.0, 0.42)
        glRotatef(sx * 28, 0, 1, 0)
        _cyl(0.022, 0.014, 0.42)
        glTranslatef(0.0, 0.0, 0.42)
        _c3(_BLUE_NEON)
        _sph(0.060)
        glPopMatrix()

def draw_claws():
    for sx in (-1.0, 1.0):
        glPushMatrix()
        glTranslatef(sx * 0.56, 0.44, 0.0)
        glRotatef(sx * -24 + state.arm_angle, 0, 0, 1)

        _c3(_DARK_BLUE)
        _sph(0.13)

        _c3(_SHADOW)
        glRotatef(-90, 1, 0, 0)
        _cyl(0.08, 0.06, 0.34)

        glTranslatef(0.0, 0.0, 0.34)
        _c3(_DARK_BLUE)
        _sph(0.075)

        _c3(_SHADOW)
        _cyl(0.06, 0.045, 0.24)

        glTranslatef(0.0, 0.0, 0.24)
        for ci in range(3):
            glPushMatrix()
            glRotatef(-18 + ci * 18, 1, 0, 0)
            _c3(_BLUE_NEON)
            _cone(0.025, 0.14)
            glPopMatrix()

        glPopMatrix()

def draw_tail():
    glPushMatrix()
    glTranslatef(0.0, -0.12, -0.44)
    glRotatef(42, 1, 0, 0)
    _c3(_SHADOW)
    _cyl(0.06, 0.03, 0.38)
    glTranslatef(0.0, 0.0, 0.38)
    glRotatef(-68, 1, 0, 0)
    _cyl(0.03, 0.016, 0.24)
    glTranslatef(0.0, 0.0, 0.24)
    _c3(_BLUE_NEON)
    _sph(0.050)
    glPopMatrix()

def draw_wings():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    for sx in (-1.0, 1.0):
        glPushMatrix()
        glTranslatef(sx * 0.34, 0.50, -0.16)
        glRotatef(sx * 38, 0, 1, 0)
        glRotatef(-28, 1, 0, 0)

        glColor4f(0.10, 0.40, 0.90, 0.35)
        glBegin(GL_TRIANGLES)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(sx * 0.52,  0.30, -0.10)
        glVertex3f(sx * 0.36, -0.22, -0.10)
        glEnd()

        glColor4f(0.25, 0.70, 1.00, 0.75)
        glLineWidth(1.4)
        glBegin(GL_LINES)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(sx * 0.52, 0.30, -0.10)
        glEnd()

        glPopMatrix()

    glDisable(GL_BLEND)
    glLineWidth(1.0)

def draw_feet_basic():
    glPushMatrix()
    glTranslatef(-0.16, -0.32, 0.10)
    _c3(_BLUE_NEON)
    glScalef(0.14, 0.04, 0.10)
    _sph(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.16, -0.32, 0.10)
    _c3(_BLUE_NEON)
    glScalef(0.14, 0.04, 0.10)
    _sph(1.0)
    glPopMatrix()

def draw():
    # CORRECCIÓN: La sombra se dibuja ANTES del PushMatrix del personaje,
    # directamente en coordenadas de mundo → se posa en el suelo (y=0).
    draw_shadow_base(state.pos_x, state.pos_z)

    glPushMatrix()
    glTranslatef(state.pos_x, state.pos_y + 0.48, state.pos_z)
    glRotatef(state.rotation_y, 0, 1, 0)
    glScalef(state.scale, state.scale, state.scale)

    if any(o["hit"] for o in state.collision_objects):
        glColor3f(1.0, 0.25, 0.25)

    draw_tail()
    draw_wings()
    draw_body()
    draw_claws()
    draw_head()
    draw_eyes()
    draw_mouth()
    draw_antennae()
    draw_feet_basic()

    glPopMatrix()
