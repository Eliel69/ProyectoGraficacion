# cat_character/cat.py
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
from gato_3d.actions import state

# ── Paleta de colores del gato ────────────────────────────────────────────────
_SKIN   = (1.00, 0.95, 0.85)
_PINK   = (1.00, 0.65, 0.75)
_DRESS  = (0.40, 0.85, 0.88)
_HAND   = (0.70, 0.30, 0.80)
_DARK   = (0.20, 0.15, 0.15)
_CHEEK  = (1.00, 0.80, 0.85)
_WHISK  = (0.30, 0.25, 0.40)

# Altura base del personaje sobre el plano (y=-1.21 es el suelo en 3D)
# char_y=0 → pies tocan el suelo, así que desplazamos el personaje hacia arriba
_FEET_OFFSET = 1.10   # hace que los pies queden justo sobre el suelo

def draw_cat():
    glPushMatrix()

    # Desactivar iluminación temporal para que el color no cambie con la cámara
    glDisable(GL_LIGHTING)

    # Subir el personaje para que los pies queden sobre el plano
    glTranslatef(0, _FEET_OFFSET, 0)

    # Color del cuerpo reactivo a colisiones
    body_color = tuple(state.char_color)

    glRotatef(state.char_rotation, 0, 1, 0)
    glScalef(1.0, state.body_scale_y, 1.0)

    _draw_body(body_color)
    _draw_head()
    _draw_ears()
    _draw_left_arm()
    _draw_right_arm()
    _draw_left_leg()
    _draw_right_leg()
    _draw_tail()

    glEnable(GL_LIGHTING)
    glPopMatrix()


# ── Partes del cuerpo ─────────────────────────────────────────────────────────

def _draw_body(color):
    glColor3f(*color)
    glBegin(GL_QUADS)
    # Frente
    glVertex3f(-0.7,  0.4,  0.7); glVertex3f( 0.7,  0.4,  0.7)
    glVertex3f( 1.0, -1.2,  0.7); glVertex3f(-1.0, -1.2,  0.7)
    # Atrás
    glVertex3f(-0.7,  0.4, -0.7); glVertex3f( 0.7,  0.4, -0.7)
    glVertex3f( 1.0, -1.2, -0.7); glVertex3f(-1.0, -1.2, -0.7)
    # Lado izq
    glVertex3f(-0.7,  0.4,  0.7); glVertex3f(-0.7,  0.4, -0.7)
    glVertex3f(-1.0, -1.2, -0.7); glVertex3f(-1.0, -1.2,  0.7)
    # Lado der
    glVertex3f( 0.7,  0.4,  0.7); glVertex3f( 0.7,  0.4, -0.7)
    glVertex3f( 1.0, -1.2, -0.7); glVertex3f( 1.0, -1.2,  0.7)
    glEnd()
    flowers = [
        (( 0.30, -0.05, 0.71), (1.0, 0.85, 0.0)),
        ((-0.40, -0.40, 0.71), (0.9, 0.30, 0.9)),
        (( 0.50, -0.70, 0.71), (0.3, 0.85, 0.4)),
        ((-0.20, -0.85, 0.71), (1.0, 0.50, 0.0)),
        (( 0.00,  0.15, 0.71), (0.4, 0.95, 0.95)),
    ]
    for pos, col in flowers:
        _draw_flower(*pos, col)

def _draw_head():
    glPushMatrix()
    glTranslatef(0, 1.2, 0)
    glColor3f(*_SKIN)
    glutSolidCube(1.6)
    glColor3f(*_PINK)
    glBegin(GL_QUADS)
    glVertex3f(-0.8,  0.8, 0.81); glVertex3f( 0.8,  0.8, 0.81)
    glVertex3f( 0.8,  0.0, 0.81); glVertex3f(-0.8,  0.0, 0.81)
    glEnd()
    glColor3f(*_CHEEK)
    for sx in (-0.5, 0.5):
        _circle_2d(sx, -0.10, 0.15, 0.82)
    _draw_eyes_expression()
    glColor3f(*_DARK)
    _circle_2d(0, 0.05, 0.07, 0.82)
    glLineWidth(2)
    glBegin(GL_LINES)
    glVertex3f(0, 0.05, 0.82); glVertex3f(0, -0.15, 0.82)
    glEnd()
    _draw_mouth_expression()
    glColor3f(*_WHISK)
    glLineWidth(2)
    for s in (-1, 1):
        glBegin(GL_LINES)
        glVertex3f(s*0.35,  0.05, 0.82); glVertex3f(s*0.78,  0.15, 0.82)
        glVertex3f(s*0.35, -0.05, 0.82); glVertex3f(s*0.78, -0.05, 0.82)
        glVertex3f(s*0.35, -0.15, 0.82); glVertex3f(s*0.78, -0.20, 0.82)
        glEnd()
    glPopMatrix()

def _draw_eyes_expression():
    glColor3f(*_DARK)
    glLineWidth(3)
    expr = state.current_expression

    if expr == "guiño":
        glBegin(GL_LINES)
        glVertex3f(-0.42, 0.30, 0.82); glVertex3f(-0.18, 0.30, 0.82)
        glEnd()
        _circle_2d(0.30, 0.30, 0.12, 0.82)

    elif expr == "miedo":
        for sx in (-0.30, 0.30):
            _circle_2d(sx, 0.30, 0.18, 0.82)
        glColor3f(0.35, 0.25, 0.20)
        glBegin(GL_LINES)
        glVertex3f(-0.45, 0.55, 0.83); glVertex3f(-0.15, 0.60, 0.83)
        glVertex3f( 0.15, 0.60, 0.83); glVertex3f( 0.45, 0.55, 0.83)
        glEnd()
        glColor3f(*_DARK)

    elif expr == "enojo":
        glColor3f(0.80, 0.05, 0.05)
        for sx in (-0.30, 0.30):
            _circle_2d(sx, 0.30, 0.13, 0.82)
        glColor3f(0.30, 0.10, 0.10)
        glLineWidth(4)
        glBegin(GL_LINES)
        glVertex3f(-0.45, 0.50, 0.83); glVertex3f(-0.15, 0.38, 0.83)
        glVertex3f( 0.15, 0.38, 0.83); glVertex3f( 0.45, 0.50, 0.83)
        glEnd()
        glColor3f(*_DARK)

    elif expr == "tristeza":
        for sx in (-0.30, 0.30):
            _circle_2d(sx, 0.30, 0.12, 0.82)
        glColor3f(0.35, 0.25, 0.20)
        glLineWidth(3)
        glBegin(GL_LINES)
        glVertex3f(-0.45, 0.38, 0.83); glVertex3f(-0.15, 0.50, 0.83)
        glVertex3f( 0.15, 0.50, 0.83); glVertex3f( 0.45, 0.38, 0.83)
        glEnd()
        glColor3f(*_DARK)

    elif expr == "duda":
        _circle_2d(-0.30, 0.30, 0.12, 0.82)
        glBegin(GL_LINES)
        glVertex3f(0.18, 0.30, 0.82); glVertex3f(0.42, 0.30, 0.82)
        glVertex3f(0.15, 0.48, 0.83); glVertex3f(0.45, 0.52, 0.83)
        glEnd()

    elif expr == "admiracion":
        for sx in (-0.30, 0.30):
            glBegin(GL_LINE_LOOP)
            for i in range(10):
                a = math.radians(i * 36)
                r = 0.16 if i % 2 == 0 else 0.08
                glVertex3f(sx + r*math.cos(a), 0.30 + r*math.sin(a), 0.82)
            glEnd()

    else:
        for sx in (-0.30, 0.30):
            _circle_2d(sx, 0.30, 0.12, 0.82)
        if expr == "felicidad":
            glColor3f(1, 1, 1)
            for sx in (-0.25, 0.35):
                _circle_2d(sx, 0.35, 0.04, 0.83)
            glColor3f(*_DARK)

def _draw_mouth_expression():
    glColor3f(*_DARK)
    glLineWidth(3)
    expr = state.current_expression

    if expr in ("felicidad", "guiño", "admiracion"):
        glBegin(GL_LINE_STRIP)
        glVertex3f(-0.25, -0.12, 0.82); glVertex3f( 0.0, -0.30, 0.82); glVertex3f( 0.25, -0.12, 0.82)
        glEnd()
    elif expr in ("tristeza",):
        glBegin(GL_LINE_STRIP)
        glVertex3f(-0.25, -0.30, 0.82); glVertex3f( 0.0, -0.15, 0.82); glVertex3f( 0.25, -0.30, 0.82)
        glEnd()
    elif expr == "miedo":
        glBegin(GL_LINE_STRIP)
        for pt in [(-0.25,-0.22),(-.12,-0.12),(0,-0.22),(.12,-0.12),(.25,-0.22)]:
            glVertex3f(pt[0], pt[1], 0.82)
        glEnd()
    elif expr == "enojo":
        glBegin(GL_LINES)
        glVertex3f(-0.22, -0.22, 0.82); glVertex3f(0.22, -0.22, 0.82)
        glEnd()
    elif expr == "duda":
        glBegin(GL_LINE_STRIP)
        glVertex3f(-0.20, -0.20, 0.82); glVertex3f(-0.05, -0.18, 0.82)
        glVertex3f( 0.05, -0.24, 0.82); glVertex3f( 0.20, -0.22, 0.82)
        glEnd()
    else:
        glBegin(GL_LINE_STRIP)
        glVertex3f(-0.20, -0.15, 0.82); glVertex3f(0.0, -0.25, 0.82); glVertex3f(0.20, -0.15, 0.82)
        glEnd()

def _draw_ears():
    glColor3f(*_PINK)
    for s in (-1, 1):
        glBegin(GL_TRIANGLES)
        glVertex3f(s*0.7, 2.0,  0.4); glVertex3f(s*0.3, 2.0,  0.4); glVertex3f(s*0.5, 2.7, 0)
        glVertex3f(s*0.7, 2.0, -0.4); glVertex3f(s*0.3, 2.0, -0.4); glVertex3f(s*0.5, 2.7, 0)
        glEnd()

def _draw_left_arm():
    glPushMatrix()
    glTranslatef(-1.0, -0.1, 0)
    # Brazos arriba: rotar hacia arriba (pitch negativo = hacia arriba en OpenGL)
    glRotatef(-state.arm_L_pitch, 1, 0, 0)
    glColor3f(*_DRESS)
    glScalef(0.6, 0.25, 0.25)
    glutSolidCube(1.0)
    glScalef(1/0.6, 1/0.25, 1/0.25)
    # La mano se extiende en la dirección del brazo
    glTranslatef(-0.35, 0, 0)
    glColor3f(*_HAND)
    glutSolidSphere(0.20, 10, 10)
    glPopMatrix()

def _draw_right_arm():
    glPushMatrix()
    glTranslatef(1.0, -0.1, 0)
    glRotatef(-state.arm_R_pitch, 1, 0, 0)
    glColor3f(*_DRESS)
    glScalef(0.6, 0.25, 0.25)
    glutSolidCube(1.0)
    glScalef(1/0.6, 1/0.25, 1/0.25)
    glTranslatef(0.35, 0, 0)
    glColor3f(*_HAND)
    glutSolidSphere(0.20, 10, 10)
    glPopMatrix()

def _draw_left_leg():
    glPushMatrix()
    glTranslatef(-0.4, -1.2, 0)
    glRotatef(state.leg_L_pitch, 1, 0, 0)

    # Pierna
    glColor3f(*_DRESS)
    glPushMatrix()
    glTranslatef(0, -0.35, 0)   
    glScalef(0.25, 0.7, 0.25)
    glutSolidCube(1.0)
    glPopMatrix()

    # Pie 
    glPushMatrix()
    glTranslatef(0, -0.72, 0.18)
    glColor3f(0.1, 0.05, 0.05)
    glScalef(0.42, 0.18, 0.62)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()

def _draw_right_leg():
    glPushMatrix()
    glTranslatef(0.4, -1.2, 0)
    glRotatef(state.leg_R_pitch, 1, 0, 0)

    # Pierna
    glColor3f(*_DRESS)
    glPushMatrix()
    glTranslatef(0, -0.35, 0)
    glScalef(0.25, 0.7, 0.25)
    glutSolidCube(1.0)
    glPopMatrix()

    # Pie
    glPushMatrix()
    glTranslatef(0, -0.72, 0.18)
    glColor3f(0.1, 0.05, 0.05)
    glScalef(0.42, 0.18, 0.62)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()

def _draw_tail():
    glColor3f(*_PINK)
    glLineWidth(6)
    glBegin(GL_LINE_STRIP)
    for i in range(12):
        t = i / 11.0
        x = -1.0 - t * 0.8
        y = -0.8 + math.sin(t * math.pi) * 0.6
        z = -t * 0.5
        glVertex3f(x, y, z)
    glEnd()

# ── Utilidades ────────────────────────────────────────────────────────────────

def _circle_2d(cx, cy, r, z=0.82):
    glBegin(GL_POLYGON)
    for i in range(20):
        a = i * 18 * math.pi / 180
        glVertex3f(cx + r*math.cos(a), cy + r*math.sin(a), z)
    glEnd()

def _draw_flower(x, y, z, color, size=0.12):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*color)
    for i in range(6):
        angle = math.radians(i * 60)
        glBegin(GL_POLYGON)
        for j in range(8):
            a = angle + math.radians((j-4)*10)
            r = size * 1.2
            glVertex3f(r*math.cos(a), r*math.sin(a), 0.01)
        glEnd()
    glColor3f(1.0, 1.0, 0.5)
    glBegin(GL_POLYGON)
    for i in range(8):
        a = math.radians(i * 45)
        glVertex3f(size*0.35*math.cos(a), size*0.35*math.sin(a), 0.02)
    glEnd()
    glPopMatrix()
