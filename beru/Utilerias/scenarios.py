# beru/Utilerias/scenarios.py
# CORRECCIONES:
# 1. Eliminado sys.path.insert
# 2. 'import actions.state as state'                       → from beru.actions import state
# 3. 'from resources.sound_manager import play_scenario'   → from beru.resources import sound_manager

import math
from OpenGL.GL  import *
from OpenGL.GLU import *
from beru.actions import state                            # CORREGIDO

def _c3(r, g, b): glColor3f(r, g, b)

def _floor(size, r, g, b):
    glBegin(GL_QUADS)
    glColor3f(r, g, b)
    glVertex3f(-size, 0, -size); glVertex3f( size, 0, -size)
    glVertex3f( size, 0,  size); glVertex3f(-size, 0,  size)
    glEnd()

def _cyl(x, y, z, base, top, h, r, g, b, sl=10):
    q = gluNewQuadric()
    glPushMatrix(); glTranslatef(x, y, z); glColor3f(r, g, b)
    gluCylinder(q, base, top, h, sl, 3)
    gluDeleteQuadric(q); glPopMatrix()

def _sph(x, y, z, rad, r, g, b, sl=12):
    q = gluNewQuadric()
    glPushMatrix(); glTranslatef(x, y, z); glColor3f(r, g, b)
    gluSphere(q, rad, sl, sl)
    gluDeleteQuadric(q); glPopMatrix()

def _scenario_dungeon():
    glClearColor(0.04, 0.02, 0.08, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    _floor(12.0, 0.08, 0.06, 0.12)
    walls = [(-6,0,-6),(6,0,-6),(-6,0,6),(6,0,6),(-6,0,0),(6,0,0),(0,0,-6)]
    for (wx, wy, wz) in walls:
        _cyl(wx, wy, wz, 0.30, 0.28, 4.0, 0.18, 0.12, 0.22)
    for i in range(6):
        ang = i * (2 * math.pi / 6)
        tx = math.cos(ang) * 5.0; tz = math.sin(ang) * 5.0
        _cyl(tx, 0, tz, 0.06, 0.04, 0.6, 0.85, 0.60, 0.10)
        _sph(tx, 0.7, tz, 0.10, 1.0, 0.80, 0.20)
    for (rx, rz) in [(-3,2),(3,-2),(0,4),(-4,-1),(4,1)]:
        _sph(rx, 0.15, rz, 0.22, 0.15, 0.10, 0.20)

def _scenario_ants():
    glClearColor(0.06, 0.03, 0.02, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    _floor(12.0, 0.18, 0.10, 0.06)
    for i in range(7):
        angle = i * (2 * math.pi / 7)
        cx = math.cos(angle) * 4.5; cz = math.sin(angle) * 4.5
        q = gluNewQuadric()
        glPushMatrix(); glTranslatef(cx, 0, cz)
        glColor3f(0.22, 0.12, 0.08)
        gluCylinder(q, 0.40, 0.10, 3.5, 8, 3)
        gluDeleteQuadric(q); glPopMatrix()
        _sph(cx, 3.6, cz, 0.18, 0.55, 0.28, 0.10)
    for (ex, ez) in [(-2,1),(2,-1),(0,3),(3,2),(-3,-2)]:
        _sph(ex, 0.10, ez, 0.30, 0.60, 0.22, 0.06)
        _sph(ex, 0.45, ez, 0.20, 0.50, 0.18, 0.05)
    glColor3f(0.80, 0.25, 0.05)
    glBegin(GL_QUADS)
    glVertex3f(-1.5, 0.01, -0.5); glVertex3f(1.5, 0.01, -0.5)
    glVertex3f( 1.5, 0.01,  3.0); glVertex3f(-1.5,0.01,  3.0)
    glEnd()

def _scenario_shadow():
    glClearColor(0.02, 0.00, 0.06, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    _floor(12.0, 0.06, 0.04, 0.14)
    for i in range(8):
        ang = i * (2 * math.pi / 8)
        cx = math.cos(ang) * 4.0; cz = math.sin(ang) * 4.0
        _cyl(cx, 0, cz, 0.14, 0.10, 3.0, 0.18, 0.05, 0.40)
        _sph(cx, 3.1, cz, 0.20, 0.30, 0.10, 0.80)
    _sph(0, 0.5, -2, 0.55, 0.25, 0.05, 0.60)
    _sph(0, 1.1, -2, 0.30, 0.40, 0.10, 0.80)
    _sph(0, 1.5, -2, 0.18, 0.60, 0.20, 1.00)
    for i in range(12):
        sx = math.sin(i * 1.2) * 4.0
        sy = (i * 0.3) % 3.5 + 0.2
        sz = math.cos(i * 1.0) * 3.5
        _sph(sx, sy, sz, 0.07, 0.50, 0.20, 1.00)

def _scenario_monarch():
    glClearColor(0.00, 0.02, 0.10, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    _floor(12.0, 0.04, 0.06, 0.18)
    q = gluNewQuadric()
    glPushMatrix(); glTranslatef(0, 0, -7)
    glColor3f(0.12, 0.08, 0.30)
    gluCylinder(q, 3.5, 0.8, 6.0, 10, 4)
    glPopMatrix(); gluDeleteQuadric(q)
    for i in range(5):
        ang = i * (2 * math.pi / 5)
        px = math.cos(ang) * 2.5; pz = -7 + math.sin(ang) * 2.5
        _sph(px, 6.2, pz, 0.22, 0.40, 0.60, 1.00)
    for i in range(6):
        ang = i * (2 * math.pi / 6)
        cx = math.cos(ang) * 5.5; cz = math.sin(ang) * 5.5
        _cyl(cx, 0, cz, 0.22, 0.16, 4.5, 0.20, 0.15, 0.50)
    import random; random.seed(7)
    glPointSize(2.0)
    glBegin(GL_POINTS); glColor3f(0.70, 0.80, 1.0)
    for _ in range(70):
        glVertex3f(random.uniform(-10,10), random.uniform(2,9), random.uniform(-10,-1))
    glEnd(); glPointSize(1.0)

def _scenario_chaos():
    glClearColor(0.10, 0.00, 0.02, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    _floor(12.0, 0.20, 0.04, 0.06)
    for i in range(6):
        ang = i * (2 * math.pi / 6)
        fx = math.cos(ang) * 4.5; fz = math.sin(ang) * 4.5
        _cyl(fx, 0, fz, 0.25, 0.0, 2.5, 0.90, 0.20, 0.02)
        _sph(fx, 2.6, fz, 0.20, 1.0, 0.40, 0.05)
    for (rx, rz) in [(-3,1),(3,-1),(1,3),(-1,-3),(4,3),(-4,-2)]:
        _sph(rx, 0.20, rz, 0.32, 0.60, 0.08, 0.04)
    q = gluNewQuadric()
    glPushMatrix(); glTranslatef(0, 0, -5)
    glColor3f(0.80, 0.10, 0.02)
    gluCylinder(q, 2.5, 0.3, 4.0, 10, 4)
    gluDeleteQuadric(q); glPopMatrix()

def _scenario_shadow_castle():
    glClearColor(0.01, 0.01, 0.04, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    _floor(12.0, 0.06, 0.06, 0.10)
    towers = [(-4,0,-5),(4,0,-5),(-4,0,5),(4,0,5),(0,0,-7)]
    for (tx, ty, tz) in towers:
        _cyl(tx, ty, tz, 0.5, 0.45, 5.0, 0.10, 0.10, 0.15)
        _sph(tx, 5.2, tz, 0.55, 0.15, 0.15, 0.25)
    glColor3f(0.10, 0.10, 0.16)
    glBegin(GL_QUADS)
    glVertex3f(-4, 0, -5); glVertex3f(4, 0, -5)
    glVertex3f( 4, 4, -5); glVertex3f(-4, 4, -5)
    glEnd()
    for i in range(10):
        bx = math.sin(i * 0.9) * 5.0
        by = (i * 0.4) % 4.0 + 0.5
        bz = math.cos(i * 0.7) * 5.0
        _sph(bx, by, bz, 0.06, 0.40, 0.40, 0.60)

def _scenario_gate():
    glClearColor(0.00, 0.04, 0.02, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    _floor(12.0, 0.08, 0.14, 0.08)
    glColor3f(0.05, 0.60, 0.30)
    glBegin(GL_QUADS)
    glVertex3f(-2.0, 0.01,  0.0); glVertex3f(2.0, 0.01, 0.0)
    glVertex3f( 2.0, 0.01, -0.5); glVertex3f(-2.0,0.01,-0.5)
    glEnd()
    for sx in (-2.0, 2.0):
        _cyl(sx, 0, 0, 0.18, 0.18, 4.5, 0.30, 0.20, 0.10)
    q = gluNewQuadric()
    glPushMatrix(); glTranslatef(0, 4.5, 0); glRotatef(90, 1, 0, 0)
    glColor3f(0.20, 0.15, 0.08)
    gluCylinder(q, 0.18, 0.18, 4.0, 8, 2)
    gluDeleteQuadric(q); glPopMatrix()
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.05, 0.70, 0.40, 0.55)
    glBegin(GL_QUADS)
    glVertex3f(-1.8, 0.05, 0); glVertex3f(1.8, 0.05, 0)
    glVertex3f( 1.8, 4.40, 0); glVertex3f(-1.8,4.40, 0)
    glEnd(); glDisable(GL_BLEND)
    trees = [(-5,0,-4),(-6,0,2),(5,0,-4),(5,0,3),(-3,0,5),(6,0,-1)]
    for (tx, ty, tz) in trees:
        _cyl(tx, ty, tz, 0.14, 0.10, 2.2, 0.28, 0.18, 0.06)
        _sph(tx, 2.4, tz, 0.85, 0.12, 0.45, 0.12)

_DRAW_FNS = [
    _scenario_dungeon,
    _scenario_ants,
    _scenario_shadow,
    _scenario_monarch,
    _scenario_chaos,
    _scenario_shadow_castle,
    _scenario_gate,
]

def draw():
    idx = state.current_scenario % len(_DRAW_FNS)
    _DRAW_FNS[idx]()

def next_scenario():
    from beru.resources import sound_manager           # CORREGIDO
    state.current_scenario = (state.current_scenario + 1) % len(_DRAW_FNS)
    sound_manager.play_scenario(state.current_scenario)

def set_scenario(idx):
    from beru.resources import sound_manager           # CORREGIDO
    state.current_scenario = idx % len(_DRAW_FNS)
    sound_manager.play_scenario(state.current_scenario)
