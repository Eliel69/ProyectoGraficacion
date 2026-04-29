# resources/scenes.py  –  5 escenarios planos 2D
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *
import math
from fallguy.actions import state

# ── utilidades de dibujo plano ──────────────────────────────────────────────
def _quad(x1, z1, x2, z2, y, c):
    glDisable(GL_LIGHTING); glColor3f(*c)
    glBegin(GL_QUADS)
    glVertex3f(x1,y,z1); glVertex3f(x2,y,z1)
    glVertex3f(x2,y,z2); glVertex3f(x1,y,z2)
    glEnd(); glEnable(GL_LIGHTING)

def _box(cx, cy, cz, w, h, d, c):
    x1,x2 = cx-w/2, cx+w/2
    y1,y2 = cy, cy+h
    z1,z2 = cz-d/2, cz+d/2
    glDisable(GL_LIGHTING); glColor3f(*c)
    glBegin(GL_QUADS)
    # top
    glVertex3f(x1,y2,z1);glVertex3f(x2,y2,z1);glVertex3f(x2,y2,z2);glVertex3f(x1,y2,z2)
    # front
    glVertex3f(x1,y1,z2);glVertex3f(x2,y1,z2);glVertex3f(x2,y2,z2);glVertex3f(x1,y2,z2)
    # back
    glVertex3f(x1,y1,z1);glVertex3f(x2,y1,z1);glVertex3f(x2,y2,z1);glVertex3f(x1,y2,z1)
    # left
    glVertex3f(x1,y1,z1);glVertex3f(x1,y1,z2);glVertex3f(x1,y2,z2);glVertex3f(x1,y2,z1)
    # right
    glVertex3f(x2,y1,z1);glVertex3f(x2,y1,z2);glVertex3f(x2,y2,z2);glVertex3f(x2,y2,z1)
    glEnd(); glEnable(GL_LIGHTING)

def _circle(cx, cz, r, y, c, n=28):
    glDisable(GL_LIGHTING); glColor3f(*c)
    glBegin(GL_TRIANGLE_FAN); glVertex3f(cx,y,cz)
    for i in range(n+1):
        a = 2*math.pi*i/n
        glVertex3f(cx+r*math.cos(a), y, cz+r*math.sin(a))
    glEnd(); glEnable(GL_LIGHTING)

def _tree(cx, cz):
    _box(cx,0,cz, 0.22,1.8,0.22, (0.45,0.28,0.10))
    _circle(cx,cz, 0.85,1.8,  (0.15,0.65,0.15))
    _circle(cx,cz, 0.55,2.5,  (0.20,0.75,0.20))

def _lines(pairs, y, c):
    glDisable(GL_LIGHTING); glColor3f(*c); glLineWidth(2)
    glBegin(GL_LINES)
    for x1,z1,x2,z2 in pairs:
        glVertex3f(x1,y,z1); glVertex3f(x2,y,z2)
    glEnd(); glLineWidth(1); glEnable(GL_LIGHTING)

# ── 1. PARQUE ────────────────────────────────────────────────────────────────
def draw_scene_park():
    state.scene_bounds = {"x":(-15,15), "z":(-15,15)}
    glClearColor(0.55,0.82,0.99,1)
    _quad(-20,-20,20,20, 0, (0.30,0.68,0.28))          # cesped
    _quad(-1,-15,  1,15, 0.01,(0.84,0.74,0.54))        # camino
    _circle(0,0, 2.8, 0.01,(0.25,0.50,0.90))            # estanque
    for tx,tz in [(-7,-7),(-7,7),(7,-7),(7,7),(-11,0),(11,0)]:
        _tree(tx,tz)
    for bx,bz in [(-4,4),(4,-4)]:
        _box(bx,0,bz, 1.6,0.45,0.45,(0.60,0.38,0.18)) # bancas

# ── 2. PISTA DE ATLETISMO ────────────────────────────────────────────────────
def draw_scene_track():
    state.scene_bounds = {"x":(-15,15), "z":(-16,16)}
    glClearColor(0.78,0.88,0.96,1)
    _quad(-20,-20,20,20, 0,(0.22,0.58,0.18))            # campo
    _quad(-3.2,-17,3.2,17, 0.01,(0.88,0.42,0.08))       # pista naranja
    _quad(-3.2,-17,3.2,-14.5,0.01,(1,1,1))              # linea salida
    _quad(-3.2,14.5,3.2,17,  0.01,(1,1,1))              # linea meta
    _lines([(-0.9,0.01,-0.9,0.01),(-0.9,-17,-0.9,17),   # carriles
            ( 0.9,-17, 0.9,17)], 0.02,(1,1,1))
    _box(-9,0,0, 4,2.8,14,(0.68,0.68,0.72))             # tribuna izq
    _box( 9,0,0, 4,2.8,14,(0.68,0.68,0.72))             # tribuna der

# ── 3. BOSQUE ────────────────────────────────────────────────────────────────
def draw_scene_forest():
    state.scene_bounds = {"x":(-15,15), "z":(-15,15)}
    glClearColor(0.10,0.20,0.12,1)
    _quad(-20,-20,20,20, 0,(0.12,0.30,0.12))            # suelo oscuro
    _quad(-0.7,-18,0.7,18, 0.01,(0.35,0.22,0.10))       # senda
    for tx,tz in [(-4,-9),(-6,0),(-5,8),(4,-6),(6,3),
                  (5,11),(-9,-3),(9,-9),(-3,14),(3,-14)]:
        _tree(tx,tz)
    for rx,rz in [(-2,5),(3,-3),(-4,11)]:
        _circle(rx,rz, 0.55,0.01,(0.44,0.44,0.48))      # rocas

# ── 4. CAMPO DE FUTBOL ───────────────────────────────────────────────────────
def draw_scene_soccer():
    state.scene_bounds = {"x":(-12,12), "z":(-18,18)}
    glClearColor(0.38,0.72,0.28,1)
    _quad(-20,-20,20,20, 0,(0.20,0.58,0.18))            # cesped
    _lines([
        (-11,-16,-11,16),(11,-16,11,16),                # banda
        (-11,-16,11,-16),(-11,16,11,16),                # fondo
        (-11,0,11,0),                                   # centro
        (-5,-10,5,-10),(-5,-10,-5,-16),( 5,-10, 5,-16), # area
        (-5, 10,5, 10),(-5, 10,-5, 16),( 5, 10, 5, 16),
    ], 0.02,(1,1,1))
    _circle(0,0, 3.0,0.02,(1,1,1))                      # circulo central
    _box(0,0,-17.8, 3.0,1.8,0.2,(1,1,1))                # porteria sur
    _box(0,0, 17.8, 3.0,1.8,0.2,(1,1,1))                # porteria norte

# ── 5. PARQUE DE DIVERSIONES ─────────────────────────────────────────────────
def draw_scene_funpark():
    state.scene_bounds = {"x":(-15,15), "z":(-15,15)}
    glClearColor(0.05,0.0,0.18,1)
    _quad(-20,-20,20,20, 0,(0.18,0.12,0.30))             # suelo festivo
    _quad(-1,-18,1,18,   0.01,(0.50,0.30,0.60))          # camino vertical
    _quad(-18,-1,18,1,   0.01,(0.50,0.30,0.60))          # camino horizontal
    # 4 puestos de colores
    for (px,pz),c in zip([(-7,-7),(-7,7),(7,-7),(7,7)],
                         [(0.9,0.1,0.1),(0.1,0.5,0.9),
                          (0.1,0.8,0.3),(0.9,0.7,0.0)]):
        _box(px,0,pz, 2,2,2,c)
    # Rueda de la fortuna (circulo + radios)
    glDisable(GL_LIGHTING); glColor3f(1.0,0.9,0.2); glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    for i in range(32):
        a = 2*math.pi*i/32
        glVertex3f(2.5*math.cos(a), 2.5, 2.5*math.sin(a))
    glEnd()
    glBegin(GL_LINES)
    for i in range(8):
        a = 2*math.pi*i/8
        glVertex3f(0,2.5,0); glVertex3f(2.5*math.cos(a),2.5,2.5*math.sin(a))
    glEnd(); glLineWidth(1); glEnable(GL_LIGHTING)
    _box(0,0,0, 0.22,2.5,0.22,(0.6,0.6,0.6))            # poste central

# ── dispatcher ───────────────────────────────────────────────────────────────
SCENES = {
    1: draw_scene_park,
    2: draw_scene_track,
    3: draw_scene_forest,
    4: draw_scene_soccer,
    5: draw_scene_funpark,
}

def draw_current_scene():
    SCENES.get(state.current_scene, draw_scene_park)()