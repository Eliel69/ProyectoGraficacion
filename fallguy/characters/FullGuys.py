# characters/FallGuy.py
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *
import math
from fallguy.actions import state

COLOR_SUIT = (0.9, 0.1, 0.1)
COLOR_FACE = (1.0, 1.0, 1.0)
COLOR_EYE  = (0.1, 0.1, 0.1)
COLOR_GOLD = (1.0, 0.85, 0.0)
COLOR_BOOT = (0.55, 0.27, 0.07)

def _c(color): glColor3f(*color)

def g2o(gx, gy, gz): return (-gy, gz, gx)

def draw_geo_sphere(gx, gy, gz, radius, color):
    _c(color); ox,oy,oz = g2o(gx,gy,gz)
    glPushMatrix(); glTranslatef(ox,oy,oz); glutSolidSphere(radius,32,32); glPopMatrix()

def draw_geo_cylinder(gx1,gy1,gz1,gx2,gy2,gz2,radius,color):
    _c(color)
    ox1,oy1,oz1 = g2o(gx1,gy1,gz1); ox2,oy2,oz2 = g2o(gx2,gy2,gz2)
    dx,dy,dz = ox2-ox1, oy2-oy1, oz2-oz1
    length = math.sqrt(dx*dx+dy*dy+dz*dz)
    glPushMatrix(); glTranslatef(ox1,oy1,oz1)
    if length > 0:
        angle = math.degrees(math.acos(max(-1.0,min(1.0,dz/length))))
        if angle != 0: glRotatef(angle,-dy,dx,0)
    q = gluNewQuadric(); gluCylinder(q,radius,radius,length,32,32); gluDeleteQuadric(q)
    glPopMatrix()

def get_normal(p1,p2,p3):
    u=[p2[i]-p1[i] for i in range(3)]; v=[p3[i]-p1[i] for i in range(3)]
    nx=u[1]*v[2]-u[2]*v[1]; ny=u[2]*v[0]-u[0]*v[2]; nz=u[0]*v[1]-u[1]*v[0]
    mag=math.sqrt(nx*nx+ny*ny+nz*nz)
    return (nx/mag,ny/mag,nz/mag) if mag>0 else (0,1,0)

def draw_geo_pyramid(p1,p2,p3,apex,color):
    _c(color)
    op1,op2,op3,oa=g2o(*p1),g2o(*p2),g2o(*p3),g2o(*apex)
    glBegin(GL_TRIANGLES)
    glNormal3f(*get_normal(op1,op2,oa));  glVertex3f(*op1);glVertex3f(*op2);glVertex3f(*oa)
    glNormal3f(*get_normal(op2,op3,oa));  glVertex3f(*op2);glVertex3f(*op3);glVertex3f(*oa)
    glNormal3f(*get_normal(op3,op1,oa));  glVertex3f(*op3);glVertex3f(*op1);glVertex3f(*oa)
    glNormal3f(*get_normal(op3,op2,op1)); glVertex3f(*op1);glVertex3f(*op2);glVertex3f(*op3)
    glEnd()

# ── EXPRESIONES ────────────────────────────────────────────────────────────
def draw_eyes():
    blink = math.sin(state.blink_timer*2.2) > 0.93
    expr  = state.expression
    for side,gy in [("L",-0.3),("R",0.3)]:
        ox,oy,oz = g2o(1.6,gy,3.0)
        glPushMatrix(); glTranslatef(ox,oy,oz)
        sy=1.0
        if blink and not(expr=="wink" and side=="R"): sy=0.1
        elif expr=="wink"  and side=="R": sy=0.1
        elif expr=="angry":               sy=0.45
        elif expr=="fear":                sy=1.6
        elif expr=="sad":                 sy=0.65
        glScalef(1.0,sy,1.0); _c(COLOR_EYE); glutSolidSphere(0.15,20,20)
        if sy>0.2:
            glTranslatef(0.08,0.05,0.0); glColor3f(1,1,1); glutSolidSphere(0.04,10,10)
        glPopMatrix()

def draw_mouth():
    glDisable(GL_LIGHTING); glLineWidth(3.0); _c(COLOR_EYE)
    expr=state.expression
    glBegin(GL_LINE_STRIP)
    for i in range(13):
        t=i/12; gy=-0.30+t*0.60
        if   expr=="angry": gz=2.60-abs(gy)*0.5
        elif expr=="sad":   gz=2.62-0.14*math.sin(math.pi*t)
        elif expr=="fear":  gz=2.60+0.07*math.sin(t*math.pi*5)
        elif expr=="wink":  gz=2.58+0.12*math.sin(math.pi*t)
        else:               gz=2.60+0.03*math.sin(math.pi*t)
        ox,oy,oz=g2o(1.62,gy,gz); glVertex3f(ox,oy,oz)
    glEnd(); glLineWidth(1.0); glEnable(GL_LIGHTING)

# ── BRAZOS ────────────────────────────────────────────────────────────────
def draw_arms_animated():
    swing   = math.sin(state.animation_angle)*25 if state.walking else 0.0
    arms_up = (state.reaction_type=="arms")
    for side,gx1,gy1,gx2,gy2 in [("L",-0.5,1.2,-0.5,2.0),("R",-0.5,-1.2,-0.5,-2.0)]:
        angle = swing if side=="L" else -swing
        if arms_up: angle=90
        ox,oy,oz=g2o(gx1,gy1,2.0)
        glPushMatrix()
        glTranslatef(ox,oy,oz); glRotatef(angle,1,0,0); glTranslatef(-ox,-oy,-oz)
        draw_geo_cylinder(gx1,gy1,2.0,gx2,gy2,1.5,0.3,COLOR_SUIT)
        draw_geo_sphere(gx2,gy2,1.5,0.35,COLOR_SUIT)
        glPopMatrix()

# ── PIERNAS + PIES VISIBLES ───────────────────────────────────────────────
def draw_legs_animated():
    swing = math.sin(state.animation_angle)*22 if state.walking else 0.0
    # gz va de 0.8 (cadera) a 0.05 (tobillo) — queda por encima del suelo
    for side,gy in [("L",0.5),("R",-0.5)]:
        angle = -swing if side=="L" else swing
        ox,oy,oz=g2o(0,gy,0.8)
        glPushMatrix()
        glTranslatef(ox,oy,oz); glRotatef(angle,1,0,0); glTranslatef(-ox,-oy,-oz)
        # pierna
        draw_geo_cylinder(0,gy,0.8, 0,gy,0.05, 0.35,COLOR_SUIT)
        # pie achatado
        glPushMatrix()
        px,py,pz=g2o(0,gy,0.0)
        glTranslatef(px,py,pz)
        glScalef(1.6,0.5,1.1)
        _c(COLOR_BOOT); glutSolidSphere(0.40,20,20)
        glPopMatrix()
        glPopMatrix()

# ── DIBUJO COMPLETO ───────────────────────────────────────────────────────
def draw_fallguy_full():
    glPushMatrix()
    glScalef(0.4,0.4,0.4)
    glTranslatef(0,0.16,0)   # sube para que los pies toquen y=0

    t=state.reaction_timer; md=state.reaction_duration
    if state.reaction_type=="jump":
        glTranslatef(0,math.sin(math.pi*t/md)*1.8,0)
    elif state.reaction_type=="spin":
        glRotatef(360*(t/md),0,1,0)
    elif state.reaction_type=="idle":
        glTranslatef(0,math.sin(state.idle_bob)*0.12,0)

    # CODIGO ORIGINAL 
    draw_geo_cylinder(0,0,1,  0,0,3,  1.2,COLOR_SUIT)
    draw_geo_sphere(0,0,3, 1.2,COLOR_SUIT)
    draw_geo_sphere(0,0,1, 1.2,COLOR_SUIT)
    draw_geo_sphere(1,0,2.8, 0.7,COLOR_FACE)
    draw_eyes()
    draw_mouth()
    draw_arms_animated()
    draw_legs_animated()
    draw_geo_cylinder(0,0,4.1, 0,0,4.4, 0.6,COLOR_GOLD)
    glPushMatrix()
    ox,oy,oz=g2o(0,0,4.4); glTranslatef(ox,oy,oz); glRotatef(-90,1,0,0)
    q=gluNewQuadric(); _c(COLOR_GOLD); gluDisk(q,0,0.6,32,1); gluDeleteQuadric(q)
    glPopMatrix()
    draw_geo_pyramid((0.6,0,4.5),(0.4,0.2,4.5),(0.4,-0.2,4.5),(0.8,0,5),COLOR_GOLD)
    draw_geo_pyramid((-0.6,0,4.5),(-0.4,0.2,4.5),(-0.4,-0.2,4.5),(-0.8,0,5),COLOR_GOLD)
    draw_geo_pyramid((0,0.6,4.5),(0.2,0.4,4.5),(-0.2,0.4,4.5),(0,0.8,5),COLOR_GOLD)
    draw_geo_pyramid((0,-0.6,4.5),(0.2,-0.4,4.5),(-0.2,-0.4,4.5),(0,-0.8,5),COLOR_GOLD)
    glPopMatrix()