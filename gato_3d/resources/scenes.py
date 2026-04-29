# resources/scenes.py
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from gato_3d.actions import state

# Dimensiones del canvas 2D (igual que ui_overlay)
_W, _H = 1000, 700

# ── Colores de suelo 3D por escena ───────────────────────────────────────────
_FLOOR_COLORS = {
    1: (0.25, 0.72, 0.25),   # jardín
    2: (0.55, 0.85, 0.55),   # arcoíris
    3: (0.35, 0.60, 0.30),   # columpio
    4: (0.45, 0.32, 0.18),   # habitación
    5: (0.92, 0.82, 0.55),   # playa
    6: (0.08, 0.12, 0.06),   # bosque
    7: (0.04, 0.04, 0.12),   # espacio
}

# ── Entrada principal ─────────────────────────────────────────────────────────
def draw_scenarios():
    # 1. Fondo 2D (detrás de todo)
    _draw_2d_background()

    # 2. Suelo 3D
    fc = _FLOOR_COLORS.get(state.current_scene, (0.3, 0.3, 0.3))
    glColor3f(*fc)
    glBegin(GL_QUADS)
    glVertex3f(-20, -1.21,  20); glVertex3f( 20, -1.21,  20)
    glVertex3f( 20, -1.21, -20); glVertex3f(-20, -1.21, -20)
    glEnd()

    # 3. Objetos de colisión 3D — sobre el plano (y=-1.21)
    _GROUND_Y = -1.21
    for obj in state.collision_objects:
        glPushMatrix()
        px, _, pz = obj["pos"]
        glTranslatef(px, _GROUND_Y, pz)
        glColor3f(*obj["color"])
        if obj["type"] == "cubo":
            # El cubo de 1.0 de lado → subir 0.5 para que quede sobre el suelo
            glTranslatef(0, 0.5, 0)
            glutSolidCube(1.0)
        elif obj["type"] == "esfera":
            # Esfera radio 0.6 → subir 0.6
            glTranslatef(0, 0.6, 0)
            glutSolidSphere(0.6, 16, 16)
        elif obj["type"] == "cono":
            # Cono altura 1.2 → subir 1.2, punta hacia arriba
            glTranslatef(0, 0.0, 0)
            glRotatef(-90, 1, 0, 0)
            glutSolidCone(0.6, 1.2, 16, 16)
        glPopMatrix()


def _draw_2d_background():
    """Cambia a proyección ortográfica, dibuja el fondo 2D y restaura."""
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, _W, 0, _H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()

    _scenes = {
        1: _bg_casa,
        2: _bg_arcoiris,
        3: _bg_columpio,
        4: _bg_habitacion,
        5: _bg_playa,
        6: _bg_bosque,
        7: _bg_espacio,
    }
    _scenes.get(state.current_scene, _bg_casa)()

    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)


# ════════════════════════════════════════════════════════════════════
#  ESCENA 1 — Casa / Jardín
# ════════════════════════════════════════════════════════════════════
def _bg_casa():
    # Cielo celeste
    _rect(0, 350, _W, _H, (0.55, 0.82, 1.00))
    # Pasto
    _rect(0, 0, _W, 350, (0.30, 0.75, 0.28))

    # Sol
    _circle(860, 620, 55, (1.0, 0.95, 0.20))

    # Nubes
    for cx, cy in ((200, 600), (550, 640), (750, 580)):
        _cloud(cx, cy)

    # Casa — cuerpo
    _rect(340, 160, 660, 380, (0.90, 0.80, 0.68))
    # Techo
    _triangle(300, 380, 700, 380, 500, 530, (0.75, 0.25, 0.22))
    # Puerta
    _rect(455, 160, 545, 310, (0.55, 0.35, 0.18))
    # Ventana izq
    _rect(365, 255, 435, 325, (0.60, 0.85, 0.95))
    _cross(365, 255, 435, 325)
    # Ventana der
    _rect(565, 255, 635, 325, (0.60, 0.85, 0.95))
    _cross(565, 255, 635, 325)

    # Flores
    for fx, fy, col in [(130,330,(1,.3,.6)),(180,345,(1,.9,0)),
                        (230,330,(0.6,.2,1)),(750,335,(0,.8,.5)),
                        (810,345,(1,.5,0)),(860,330,(.9,.2,.9))]:
        _flower(fx, fy, 18, col)

    # Arbustos
    for bx in (280, 710):
        _circle(bx, 185, 28, (0.20, 0.65, 0.20))
        _circle(bx+30, 178, 22, (0.25, 0.70, 0.25))


# ════════════════════════════════════════════════════════════════════
#  ESCENA 2 — Arcoíris
# ════════════════════════════════════════════════════════════════════
def _bg_arcoiris():
    # Cielo degradado simulado con dos quads
    _rect(0, 350, _W, _H, (0.50, 0.78, 1.00))
    _rect(0, 0,   _W, 350, (0.38, 0.68, 0.95))
    # Pasto
    _rect(0, 0, _W, 200, (0.35, 0.80, 0.32))

    # Arcoíris (bandas gruesas)
    colors = [(1,.10,.10),(1,.55,.0),(1,.95,.0),(0,.80,.20),(0,.45,.95),(0.55,.0,.95)]
    for i, c in enumerate(colors):
        r = 420 - i * 38
        glColor3f(*c)
        glLineWidth(22)
        glBegin(GL_LINE_STRIP)
        for a in range(0, 181, 3):
            ar = math.radians(a)
            glVertex2f(500 + r*math.cos(ar), 180 + r*math.sin(ar))
        glEnd()
    glLineWidth(1)

    # Nubes en los extremos del arcoíris
    _cloud(90, 220)
    _cloud(870, 215)

    # Sol
    _circle(500, 660, 50, (1.0, 0.95, 0.20))

    # Flores en el suelo
    for fx, fy, col in [(80,160,(1,.3,.6)),(200,175,(1,.9,0)),
                        (400,165,(0.5,.1,1)),(600,170,(1,.5,0)),
                        (800,160,(.2,.9,.5)),(920,172,(.9,.2,.9))]:
        _flower(fx, fy, 14, col)


# ════════════════════════════════════════════════════════════════════
#  ESCENA 3 — Columpio / Parque
# ════════════════════════════════════════════════════════════════════
def _bg_columpio():
    # Cielo
    _rect(0, 300, _W, _H, (0.55, 0.82, 1.00))
    # Pasto
    _rect(0, 0,   _W, 300, (0.28, 0.72, 0.26))

    # Sol
    _circle(880, 620, 48, (1.0, 0.95, 0.20))
    _cloud(200, 600)
    _cloud(620, 640)

    # Árbol izquierdo
    _rect(95, 200, 115, 310, (0.45, 0.28, 0.12))
    _circle(105, 340, 60, (0.20, 0.65, 0.22))
    _circle(70,  320, 44, (0.22, 0.68, 0.24))
    _circle(140, 318, 44, (0.22, 0.68, 0.24))

    # Árbol derecho
    _rect(870, 200, 890, 310, (0.45, 0.28, 0.12))
    _circle(880, 340, 60, (0.20, 0.65, 0.22))
    _circle(845, 318, 44, (0.22, 0.68, 0.24))
    _circle(915, 318, 44, (0.22, 0.68, 0.24))

    # Marco del columpio
    glColor3f(0.50, 0.38, 0.22)
    glLineWidth(8)
    glBegin(GL_LINES)
    glVertex2f(350, 200); glVertex2f(420, 420)   # pata izq
    glVertex2f(650, 200); glVertex2f(580, 420)   # pata der
    glVertex2f(350, 200); glVertex2f(650, 200)   # barra superior
    glEnd()
    # Cuerdas
    glColor3f(0.65, 0.52, 0.30)
    glLineWidth(4)
    glBegin(GL_LINES)
    glVertex2f(420, 200); glVertex2f(420, 310)
    glVertex2f(580, 200); glVertex2f(580, 310)
    glEnd()
    glLineWidth(1)
    # Asiento
    _rect(415, 300, 585, 325, (0.60, 0.38, 0.18))

    # Flores
    for fx, fy, col in [(180,278,(1,.3,.6)),(240,290,(1,.9,0)),
                        (720,282,(.5,.1,1)),(780,290,(1,.5,0))]:
        _flower(fx, fy, 14, col)


# ════════════════════════════════════════════════════════════════════
#  ESCENA 4 — Habitación interior
# ════════════════════════════════════════════════════════════════════
def _bg_habitacion():
    # Pared
    _rect(0, 0, _W, _H, (0.96, 0.92, 0.84))
    # Rodapié
    _rect(0, 0, _W, 60, (0.78, 0.68, 0.56))
    # Techo / zócalo superior
    _rect(0, _H-30, _W, _H, (0.78, 0.68, 0.56))

    # Ventana grande izq
    _rect(60, 380, 280, 620, (0.65, 0.88, 1.00))
    _outline(60, 380, 280, 620, (0.70, 0.58, 0.42), 6)
    _cross(60, 380, 280, 620)
    # Paisaje dentro de la ventana
    _rect(60, 380, 280, 500, (0.35, 0.72, 0.28))
    _circle(200, 595, 28, (1.0, 0.95, 0.20))

    # Cuadro decorativo der
    _rect(680, 420, 900, 600, (0.25, 0.45, 0.72))
    _outline(680, 420, 900, 600, (0.70, 0.55, 0.30), 8)
    # Detalle abstracto dentro del cuadro
    _circle(790, 510, 50, (1.0, 0.70, 0.20))
    _circle(790, 510, 30, (0.95, 0.95, 0.85))

    # Lámpara de techo
    _triangle(460, 680, 540, 680, 500, 640, (1.0, 0.95, 0.70))
    glColor3f(0.70, 0.70, 0.70)
    glLineWidth(3)
    glBegin(GL_LINES)
    glVertex2f(500, 700); glVertex2f(500, 682)
    glEnd()
    glLineWidth(1)
    # Brillo lámpara
    _circle(500, 655, 8, (1.0, 1.0, 0.85))

    # Mesa
    _rect(300, 100, 700, 130, (0.58, 0.40, 0.22))
    _rect(310,  60, 340, 102, (0.52, 0.36, 0.20))
    _rect(660,  60, 690, 102, (0.52, 0.36, 0.20))
    # Taza sobre la mesa
    _rect(460, 130, 510, 175, (0.90, 0.35, 0.25))
    _circle(485, 175, 18, (0.90, 0.35, 0.25))


# ════════════════════════════════════════════════════════════════════
#  ESCENA 5 — Playa
# ════════════════════════════════════════════════════════════════════
def _bg_playa():
    # Cielo
    _rect(0, 280, _W, _H, (0.45, 0.78, 1.00))
    # Mar
    _rect(0, 200, _W, 310, (0.10, 0.48, 0.82))
    # Olas (líneas blancas)
    glColor3f(1, 1, 1)
    glLineWidth(3)
    for oy in (245, 270, 295):
        glBegin(GL_LINE_STRIP)
        for x in range(0, _W+1, 40):
            glVertex2f(x, oy + 6*math.sin(math.radians(x*2)))
        glEnd()
    glLineWidth(1)
    # Arena
    _rect(0, 0, _W, 210, (0.95, 0.85, 0.58))

    # Sol con rayos
    cx, cy, r = 820, 630, 55
    _circle(cx, cy, r, (1.0, 0.95, 0.15))
    glColor3f(1.0, 0.92, 0.20)
    glLineWidth(3)
    for a in range(0, 360, 30):
        ar = math.radians(a)
        glBegin(GL_LINES)
        glVertex2f(cx + (r+6)*math.cos(ar),  cy + (r+6)*math.sin(ar))
        glVertex2f(cx + (r+22)*math.cos(ar), cy + (r+22)*math.sin(ar))
        glEnd()
    glLineWidth(1)

    # Nube
    _cloud(200, 630)
    _cloud(560, 610)

    # Palmera izq
    _rect(118, 130, 132, 330, (0.55, 0.36, 0.16))   # tronco
    glColor3f(0.22, 0.72, 0.26)
    glBegin(GL_TRIANGLES)
    glVertex2f(125, 330); glVertex2f( 10, 400); glVertex2f(125, 380)
    glVertex2f(125, 330); glVertex2f(240, 400); glVertex2f(125, 380)
    glVertex2f(125, 330); glVertex2f(125, 430); glVertex2f(125, 380)
    glEnd()
    # Coco
    _circle(125, 355, 10, (0.45, 0.28, 0.10))

    # Sombrilla de playa
    _triangle(480, 210, 680, 210, 580, 360, (1.0, 0.25, 0.25))
    glColor3f(1.0, 1.0, 0.30)
    glBegin(GL_TRIANGLES)
    glVertex2f(480, 210); glVertex2f(530, 210); glVertex2f(480, 290)
    glVertex2f(580, 210); glVertex2f(680, 210); glVertex2f(680, 290)
    glEnd()
    glColor3f(0.60, 0.40, 0.20)
    glLineWidth(4)
    glBegin(GL_LINES)
    glVertex2f(580, 210); glVertex2f(580, 100)
    glEnd()
    glLineWidth(1)

    # Estrellas de mar / conchitas en la arena
    for sx, sy, col in [(200,140,(1,.3,.5)),(350,100,(1,.7,.2)),
                        (700,120,(1,.4,.7)),(800,150,(1,.8,.2))]:
        _flower(sx, sy, 12, col)


# ════════════════════════════════════════════════════════════════════
#  ESCENA 6 — Bosque nocturno
# ════════════════════════════════════════════════════════════════════
def _bg_bosque():
    # Cielo nocturno
    _rect(0, 200, _W, _H, (0.04, 0.04, 0.16))
    # Suelo oscuro
    _rect(0, 0,   _W, 210, (0.06, 0.14, 0.06))

    # Estrellas
    glColor3f(1.0, 1.0, 0.90)
    glPointSize(3)
    glBegin(GL_POINTS)
    for sx, sy in [(80,650),(180,620),(300,660),(450,640),(600,655),
                   (720,625),(840,648),(920,615),(140,590),(500,600),
                   (670,580),(760,660),(350,595),(55,605),(980,640)]:
        glVertex2f(sx, sy)
    glEnd()
    glPointSize(1)

    # Luna
    _circle(820, 620, 52, (0.96, 0.96, 0.85))
    # Sombra de luna (cráter)
    _circle(840, 638, 10, (0.82, 0.82, 0.72))
    _circle(808, 608,  7, (0.82, 0.82, 0.72))

    # Árboles (siluetas oscuras)
    tree_data = [
        ( 60, 200, 45, 250, (0.04,0.12,0.04)),
        (180, 200, 55, 280, (0.05,0.14,0.05)),
        (300, 200, 40, 230, (0.04,0.12,0.04)),
        (500, 200, 60, 300, (0.04,0.13,0.04)),
        (680, 200, 50, 260, (0.05,0.14,0.05)),
        (820, 200, 45, 240, (0.04,0.12,0.04)),
        (940, 200, 55, 270, (0.04,0.13,0.04)),
    ]
    for tx, ty, tw, th, col in tree_data:
        # Tronco
        _rect(tx-8, ty, tx+8, ty+80, (0.08, 0.06, 0.04))
        # Copa triangular (3 capas)
        _triangle(tx-tw, ty+60, tx+tw, ty+60, tx, ty+th,      col)
        _triangle(tx-int(tw*.8), ty+int(th*.55), tx+int(tw*.8), ty+int(th*.55), tx, ty+th+50, col)
        _triangle(tx-int(tw*.6), ty+int(th*.78), tx+int(tw*.6), ty+int(th*.78), tx, ty+th+90, col)

    # Luciérnagas (puntitos amarillo-verdosos)
    glColor3f(0.70, 1.0, 0.40)
    glPointSize(4)
    glBegin(GL_POINTS)
    for lx, ly in [(160,350),(360,310),(480,380),(600,330),(740,360),(880,340)]:
        glVertex2f(lx, ly)
    glEnd()
    glPointSize(1)


# ════════════════════════════════════════════════════════════════════
#  ESCENA 7 — Espacio
# ════════════════════════════════════════════════════════════════════
def _bg_espacio():
    # Fondo negro
    _rect(0, 0, _W, _H, (0.0, 0.0, 0.0))

    # Estrellas de distintos tamaños
    glPointSize(1)
    glColor3f(1, 1, 1)
    glBegin(GL_POINTS)
    for sx, sy in [(50,650),(130,520),(220,680),(310,590),(420,660),(530,610),
                   (640,670),(750,530),(860,600),(950,655),(90,430),(200,460),
                   (380,500),(470,440),(600,480),(700,460),(810,510),(900,430),
                   (155,370),(285,340),(450,380),(620,355),(770,395),(910,350)]:
        glVertex2f(sx, sy)
    glEnd()
    glPointSize(3)
    glColor3f(1, 1, 0.85)
    glBegin(GL_POINTS)
    for sx, sy in [(170,600),(400,550),(650,620),(880,570),(300,420),(750,400)]:
        glVertex2f(sx, sy)
    glEnd()
    glPointSize(1)

    # Vía láctea (franja de puntos pequeños)
    glColor3f(0.50, 0.50, 0.75)
    glPointSize(2)
    glBegin(GL_POINTS)
    for i in range(80):
        x = 50 + i * 11
        y = 480 + 40*math.sin(math.radians(i*9)) + (i%5)*6
        glVertex2f(x, y)
    glEnd()
    glPointSize(1)

    # Planeta grande (rojizo con bandas)
    _circle(580, 520, 120, (0.72, 0.28, 0.22))
    _circle(580, 520, 120, (0.80, 0.38, 0.30))   # más claro encima
    # Bandas del planeta
    glColor3f(0.62, 0.20, 0.16)
    glLineWidth(10)
    for dy in (-25, 5, 35):
        glBegin(GL_LINE_STRIP)
        for a in range(-60, 61, 5):
            ar = math.radians(a)
            glVertex2f(580 + 120*math.sin(ar), 520 + dy + 15*math.cos(ar))
        glEnd()
    glLineWidth(1)
    # Anillo del planeta
    glColor3f(0.85, 0.72, 0.45)
    glLineWidth(6)
    glBegin(GL_LINE_LOOP)
    for a in range(0, 360, 5):
        ar = math.radians(a)
        glVertex2f(580 + 190*math.cos(ar), 520 + 45*math.sin(ar))
    glEnd()
    glLineWidth(1)

    # Luna pequeña
    _circle(280, 580, 38, (0.82, 0.82, 0.76))
    _circle(292, 572, 8,  (0.68, 0.68, 0.62))

    # Cohete
    # Cuerpo
    _rect(145, 340, 175, 430, (0.85, 0.85, 0.88))
    # Punta
    _triangle(145, 430, 175, 430, 160, 470, (0.90, 0.22, 0.22))
    # Alas
    _triangle(130, 340, 148, 340, 130, 300, (0.65, 0.65, 0.70))
    _triangle(152, 340, 170, 340, 170, 300, (0.65, 0.65, 0.70))
    # Ventanilla
    _circle(160, 400, 12, (0.55, 0.85, 1.00))
    # Fuego del cohete
    _triangle(148, 338, 172, 338, 160, 300, (1.0, 0.55, 0.05))
    _triangle(151, 338, 169, 338, 160, 315, (1.0, 0.92, 0.20))

    # Satélite pequeño
    _rect(820, 370, 870, 385, (0.75, 0.75, 0.80))   # cuerpo
    _rect(780, 375, 820, 380, (0.55, 0.75, 0.95))   # panel izq
    _rect(870, 375, 910, 380, (0.55, 0.75, 0.95))   # panel der


# ════════════════════════════════════════════════════════════════════
#  Utilidades de dibujo 2D
# ════════════════════════════════════════════════════════════════════

def _rect(x0, y0, x1, y1, color):
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x0, y0); glVertex2f(x1, y0)
    glVertex2f(x1, y1); glVertex2f(x0, y1)
    glEnd()

def _circle(cx, cy, r, color):
    glColor3f(*color)
    glBegin(GL_POLYGON)
    for i in range(36):
        a = math.radians(i * 10)
        glVertex2f(cx + r*math.cos(a), cy + r*math.sin(a))
    glEnd()

def _triangle(x0, y0, x1, y1, x2, y2, color):
    glColor3f(*color)
    glBegin(GL_TRIANGLES)
    glVertex2f(x0, y0); glVertex2f(x1, y1); glVertex2f(x2, y2)
    glEnd()

def _outline(x0, y0, x1, y1, color, lw=3):
    glColor3f(*color)
    glLineWidth(lw)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x0, y0); glVertex2f(x1, y0)
    glVertex2f(x1, y1); glVertex2f(x0, y1)
    glEnd()
    glLineWidth(1)

def _cross(x0, y0, x1, y1):
    mx, my = (x0+x1)/2, (y0+y1)/2
    glColor3f(0.70, 0.58, 0.42)
    glLineWidth(3)
    glBegin(GL_LINES)
    glVertex2f(mx, y0); glVertex2f(mx, y1)
    glVertex2f(x0, my); glVertex2f(x1, my)
    glEnd()
    glLineWidth(1)

def _cloud(cx, cy):
    glColor3f(1, 1, 1)
    for dx, dy, r in [(0,0,30),(30,10,26),(-30,10,24),(55,0,22),(-55,0,20),(20,-12,22),(-20,-12,20)]:
        _circle(cx+dx, cy+dy, r, (1, 1, 1))

def _flower(cx, cy, r, petal_color):
    for i in range(6):
        a = math.radians(i * 60)
        _circle(int(cx + r*math.cos(a)), int(cy + r*math.sin(a)), r//2+2, petal_color)
    _circle(cx, cy, r//2, (1.0, 0.95, 0.20))
