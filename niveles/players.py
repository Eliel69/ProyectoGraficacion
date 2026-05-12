# niveles/players.py
import math
from OpenGL.GL  import *
from OpenGL.GLU import *
from niveles    import state

_BOUND = 14.0

def _clamp(v, lo, hi):
    return max(lo, min(hi, v))

def update():
    dx1, dz1 = 0.0, 0.0
    if state.k_w: dz1 -= 1.0
    if state.k_s: dz1 += 1.0
    if state.k_a: dx1 -= 1.0
    if state.k_d: dx1 += 1.0
    moving1 = (dx1 != 0.0 or dz1 != 0.0)
    if moving1:
        l = math.sqrt(dx1*dx1 + dz1*dz1)
        state.p1_x = _clamp(state.p1_x + (dx1/l)*state.p1_speed, -_BOUND, _BOUND)
        state.p1_z = _clamp(state.p1_z + (dz1/l)*state.p1_speed, -_BOUND, _BOUND)
        state.p1_rot = math.degrees(math.atan2(dx1, -dz1))
    state.p1_walking = moving1
    state.p1_anim = (state.p1_anim + 0.25) if moving1 else state.p1_anim * 0.8

    dx2, dz2 = 0.0, 0.0
    if state.k_up:    dz2 -= 1.0
    if state.k_down:  dz2 += 1.0
    if state.k_left:  dx2 -= 1.0
    if state.k_right: dx2 += 1.0
    moving2 = (dx2 != 0.0 or dz2 != 0.0)
    if moving2:
        l = math.sqrt(dx2*dx2 + dz2*dz2)
        state.p2_x = _clamp(state.p2_x + (dx2/l)*state.p2_speed, -_BOUND, _BOUND)
        state.p2_z = _clamp(state.p2_z + (dz2/l)*state.p2_speed, -_BOUND, _BOUND)
        state.p2_rot = math.degrees(math.atan2(dx2, -dz2))
    state.p2_walking = moving2
    state.p2_anim = (state.p2_anim + 0.25) if moving2 else state.p2_anim * 0.8

# Escala y offset Y por personaje en los niveles
# 0=FallGuy 1=AmongUs 2=Beru 3=Gato 4=MegaCaballero 5=Totoro
_NIVEL_SCALE = [0.55, 0.55, 0.55, 0.55, 0.55, 0.13]
_NIVEL_Y_OFF = [0.0,  0.0,  0.0,  0.0,  0.55, 0.0 ]

def _draw_disc_under(r, g, b, radius=0.8, alpha=0.75):
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(r, g, b, alpha)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, 0.02, 0.0)
    for i in range(21):
        a = 2 * math.pi * i / 20
        glVertex3f(math.cos(a)*radius, 0.02, math.sin(a)*radius)
    glEnd()
    glDisable(GL_BLEND); glEnable(GL_LIGHTING)

def _draw_label_dot(r, g, b):
    glDisable(GL_LIGHTING)
    glColor3f(r, g, b)
    q = gluNewQuadric()
    glPushMatrix()
    glTranslatef(0.0, 2.8, 0.0)
    gluSphere(q, 0.18, 10, 10)
    glPopMatrix()
    gluDeleteQuadric(q)
    glEnable(GL_LIGHTING)

def draw_players(draw_p1_fn, draw_p2_fn):
    idx1 = getattr(state, 'personaje_idx',    0)
    idx2 = getattr(state, 'personaje_idx_p2', 1)

    def _draw_one(px, pz, rot, fn, idx, disc_r, disc_g, disc_b):
        sc   = _NIVEL_SCALE[idx] if 0 <= idx < len(_NIVEL_SCALE) else 0.55
        yoff = _NIVEL_Y_OFF[idx] if 0 <= idx < len(_NIVEL_Y_OFF) else 0.0
        glPushMatrix()
        glTranslatef(px, 0.0, pz)
        glRotatef(rot, 0, 1, 0)
        _draw_disc_under(disc_r, disc_g, disc_b)
        glPushMatrix()
        glTranslatef(0.0, yoff, 0.0)
        glScalef(sc, sc, sc)
        fn()
        glPopMatrix()
        _draw_label_dot(disc_r, disc_g, disc_b)
        glPopMatrix()

    _draw_one(state.p1_x, state.p1_z, state.p1_rot, draw_p1_fn, idx1, 0.90, 0.12, 0.12)
    _draw_one(state.p2_x, state.p2_z, state.p2_rot, draw_p2_fn, idx2, 0.15, 0.35, 0.95)
