# niveles/nivel1.py
# NIVEL 1 — El Valle de los Colores
# Ambos jugadores tienen instrucción simultánea independiente.
# 6 objetos de distintas formas y colores dispersos por el mapa.
import math, random
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *
from niveles     import state, camera, hud, players

# ── Objetos del nivel: forma + color, bien dispersos ──────────
_OBJETOS = [
    {"id":0, "nombre":"Roja",      "color":(0.88,0.12,0.12), "x":-7.0, "z":-5.0, "forma":"cubo"},
    {"id":1, "nombre":"Azul",      "color":(0.12,0.28,0.92), "x": 7.0, "z":-5.0, "forma":"esfera"},
    {"id":2, "nombre":"Amarilla",  "color":(0.95,0.88,0.05), "x":-7.0, "z": 5.0, "forma":"cubo"},
    {"id":3, "nombre":"Verde",     "color":(0.12,0.80,0.22), "x": 7.0, "z": 5.0, "forma":"cilindro"},
    {"id":4, "nombre":"Naranja",   "color":(0.98,0.52,0.05), "x": 0.0, "z":-8.0, "forma":"esfera"},
    {"id":5, "nombre":"Morada",    "color":(0.65,0.12,0.90), "x": 0.0, "z": 8.0, "forma":"cubo"},
]

_RADIO_OBJ = 1.0
_LADO      = 1.4
_RADIO_JUG = 0.5

_obj_p1    = 0   # objeto que J1 debe tocar
_obj_p2    = 1   # objeto que J2 debe tocar
_anim_obj  = {}  # {id: angulo_giro}
_cooldown_p1 = 0
_cooldown_p2 = 0


def _reset_nivel():
    global _obj_p1, _obj_p2, _anim_obj, _cooldown_p1, _cooldown_p2
    state.p1_x=-4.0; state.p1_z=0.0; state.p1_rot=0.0
    state.p2_x= 4.0; state.p2_z=0.0; state.p2_rot=180.0
    state.p1_walking=state.p2_walking=False
    state.p1_anim=state.p2_anim=0.0
    state.k_w=state.k_s=state.k_a=state.k_d=False
    state.k_up=state.k_down=state.k_left=state.k_right=False
    state.score_p1=state.score_p2=0
    state.hud_feedback=""; state.hud_fb_timer=0
    state.nivel_completado=False
    _anim_obj={o["id"]:0.0 for o in _OBJETOS}
    _cooldown_p1=_cooldown_p2=0
    _nueva_instruccion_p1()
    _nueva_instruccion_p2()


def _nueva_instruccion_p1():
    global _obj_p1
    _obj_p1 = random.randint(0, len(_OBJETOS)-1)
    nombre = _OBJETOS[_obj_p1]["nombre"]
    state.hud_msg = f"J1: !Toca la figura {nombre}!"

def _nueva_instruccion_p2():
    global _obj_p2
    _obj_p2 = random.randint(0, len(_OBJETOS)-1)
    # guardar segunda instrucción en un campo extra
    state.hud_msg2 = f"J2: !Toca la figura {_OBJETOS[_obj_p2]['nombre']}!"


def _dist2d(ax,az,bx,bz):
    return math.sqrt((ax-bx)**2+(az-bz)**2)


def _check_colisiones():
    global _cooldown_p1, _cooldown_p2

    # J1
    if _cooldown_p1 > 0:
        _cooldown_p1 -= 1
    else:
        for obj in _OBJETOS:
            if _dist2d(state.p1_x,state.p1_z,obj["x"],obj["z"]) < (_RADIO_OBJ+_RADIO_JUG):
                if obj["id"] == _obj_p1:
                    state.hud_fb_p1="!J1 Correcto!"; state.hud_fb_timer_p1=90
                    state.score_p1 += 1
                    _anim_obj[obj["id"]] = 1.0
                else:
                    state.hud_fb_p1="J1: Ups..."; state.hud_fb_timer_p1=70
                _cooldown_p1=55
                _nueva_instruccion_p1()
                break

    # J2
    if _cooldown_p2 > 0:
        _cooldown_p2 -= 1
    else:
        for obj in _OBJETOS:
            if _dist2d(state.p2_x,state.p2_z,obj["x"],obj["z"]) < (_RADIO_OBJ+_RADIO_JUG):
                if obj["id"] == _obj_p2:
                    state.hud_fb_p2="!J2 Correcto!"; state.hud_fb_timer_p2=90
                    state.score_p2 += 1
                    _anim_obj[obj["id"]] = 1.0
                else:
                    state.hud_fb_p2="J2: Ups..."; state.hud_fb_timer_p2=70
                _cooldown_p2=55
                _nueva_instruccion_p2()
                break


# ── Dibujo ────────────────────────────────────────────────────
def _draw_floor():
    glDisable(GL_LIGHTING)
    glColor3f(0.72,0.72,0.72)
    glBegin(GL_QUADS)
    glVertex3f(-16,-0.01, 16); glVertex3f(16,-0.01, 16)
    glVertex3f(16,-0.01,-16); glVertex3f(-16,-0.01,-16)
    glEnd()
    glColor3f(0.62,0.62,0.62); glLineWidth(0.5)
    glBegin(GL_LINES)
    for i in range(-16,17,2):
        glVertex3f(i,0, 16); glVertex3f(i,0,-16)
        glVertex3f(-16,0,i); glVertex3f(16,0,i)
    glEnd(); glLineWidth(1.0)
    glEnable(GL_LIGHTING)

def _draw_cubo(s=_LADO):
    glBegin(GL_QUADS)
    glVertex3f(-s,s*2, s); glVertex3f(s,s*2, s); glVertex3f(s,s*2,-s); glVertex3f(-s,s*2,-s)
    glVertex3f(-s,0,-s);   glVertex3f(s,0,-s);   glVertex3f(s,0, s);   glVertex3f(-s,0, s)
    glVertex3f(-s,0, s);   glVertex3f(s,0, s);   glVertex3f(s,s*2, s); glVertex3f(-s,s*2, s)
    glVertex3f(s,0,-s);    glVertex3f(-s,0,-s);  glVertex3f(-s,s*2,-s);glVertex3f(s,s*2,-s)
    glVertex3f(-s,0,-s);   glVertex3f(-s,0, s);  glVertex3f(-s,s*2, s);glVertex3f(-s,s*2,-s)
    glVertex3f(s,0, s);    glVertex3f(s,0,-s);   glVertex3f(s,s*2,-s); glVertex3f(s,s*2, s)
    glEnd()

def _draw_objetos():
    for obj in _OBJETOS:
        glPushMatrix()
        glTranslatef(obj["x"],0.0,obj["z"])
        spin = _anim_obj.get(obj["id"],0.0)
        if spin > 0.0:
            glRotatef(spin*360.0,0,1,0)
        glDisable(GL_LIGHTING)
        r,g,b = obj["color"]
        # Resaltar los objetivos activos
        if obj["id"] == _obj_p1:
            glColor3f(min(r+0.18,1),min(g+0.18,1),min(b+0.18,1))
        elif obj["id"] == _obj_p2:
            glColor3f(min(r+0.12,1),min(g+0.12,1),min(b+0.12,1))
        else:
            glColor3f(r,g,b)
        forma = obj["forma"]
        if forma == "cubo":
            _draw_cubo()
        elif forma == "esfera":
            q=gluNewQuadric(); glTranslatef(0,0.9,0); gluSphere(q,0.9,18,18); gluDeleteQuadric(q)
        elif forma == "cilindro":
            q=gluNewQuadric()
            gluCylinder(q,0.55,0.55,1.8,14,3)
            glPushMatrix(); glRotatef(180,1,0,0); gluDisk(q,0,0.55,14,1); glPopMatrix()
            glPushMatrix(); glTranslatef(0,0,1.8); gluDisk(q,0,0.55,14,1); glPopMatrix()
            gluDeleteQuadric(q)
        glEnable(GL_LIGHTING)
        glPopMatrix()


# ── HUD extendido para nivel 1 (dos instrucciones) ───────────
def _draw_hud_nivel1():
    from niveles.hud import _enter_2d, _leave_2d, _txt
    from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_HELVETICA_12
    w,h = _enter_2d()

    # Barra superior
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0,0,0,0.55)
    glBegin(GL_QUADS)
    glVertex2f(0,h); glVertex2f(w,h); glVertex2f(w,h-52); glVertex2f(0,h-52)
    glEnd(); glDisable(GL_BLEND)

    _txt(10,h-20,"NIVEL 1 — Valle de los Colores",GLUT_BITMAP_HELVETICA_18,(1.0,0.85,0.20))
    _txt(w-220,h-20,f"J1: {state.score_p1}   J2: {state.score_p2}",
         GLUT_BITMAP_HELVETICA_18,(0.90,0.90,1.00))

    # Instrucción J1 (rojo, izquierda)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.55,0.05,0.05,0.70)
    glBegin(GL_QUADS)
    glVertex2f(0,h-52); glVertex2f(300,h-52); glVertex2f(300,h-90); glVertex2f(0,h-90)
    glEnd(); glDisable(GL_BLEND)
    _txt(8,h-68, getattr(state,"hud_msg",""),  GLUT_BITMAP_HELVETICA_18,(1.0,0.55,0.55))

    # Instrucción J2 (azul, derecha)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.05,0.10,0.55,0.70)
    glBegin(GL_QUADS)
    glVertex2f(w-300,h-52); glVertex2f(w,h-52); glVertex2f(w,h-90); glVertex2f(w-300,h-90)
    glEnd(); glDisable(GL_BLEND)
    _txt(w-295,h-68, getattr(state,"hud_msg2",""), GLUT_BITMAP_HELVETICA_18,(0.55,0.75,1.0))

    # Feedback J1
    if getattr(state,"hud_fb_p1",""):
        col=(0.20,1.0,0.30) if "orrecto" in state.hud_fb_p1 else (1.0,0.35,0.35)
        _txt(30, h//2, state.hud_fb_p1, GLUT_BITMAP_HELVETICA_18, col)
    # Feedback J2
    if getattr(state,"hud_fb_p2",""):
        col=(0.20,1.0,0.30) if "orrecto" in state.hud_fb_p2 else (1.0,0.35,0.35)
        _txt(w-280, h//2, state.hud_fb_p2, GLUT_BITMAP_HELVETICA_18, col)

    # Etiquetas inferiores
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.50,0.05,0.05,0.70)
    glBegin(GL_QUADS); glVertex2f(0,0); glVertex2f(200,0); glVertex2f(200,36); glVertex2f(0,36); glEnd()
    glColor4f(0.05,0.10,0.55,0.70)
    glBegin(GL_QUADS); glVertex2f(w-200,0); glVertex2f(w,0); glVertex2f(w,36); glVertex2f(w-200,36); glEnd()
    glDisable(GL_BLEND)
    _txt(8,14,"J1  WASD — mover",GLUT_BITMAP_HELVETICA_12,(1.0,0.75,0.75))
    _txt(w-195,14,"J2  Flechas — mover",GLUT_BITMAP_HELVETICA_12,(0.75,0.85,1.0))
    _txt(w//2-80,14,"ESC: lobby",GLUT_BITMAP_HELVETICA_12,(0.55,0.55,0.55))

    _leave_2d()


# ── API pública ───────────────────────────────────────────────
def init():
    # Inicializar campos de feedback individuales en state
    if not hasattr(state,"hud_msg2"):    state.hud_msg2=""
    if not hasattr(state,"hud_fb_p1"):   state.hud_fb_p1=""
    if not hasattr(state,"hud_fb_p2"):   state.hud_fb_p2=""
    if not hasattr(state,"hud_fb_timer_p1"): state.hud_fb_timer_p1=0
    if not hasattr(state,"hud_fb_timer_p2"): state.hud_fb_timer_p2=0
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING); glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL); glColorMaterial(GL_FRONT,GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    glLightfv(GL_LIGHT0,GL_POSITION,[0.0,10.0,5.0,0.0])
    glLightfv(GL_LIGHT0,GL_AMBIENT,[0.35,0.35,0.35,1.0])
    glLightfv(GL_LIGHT0,GL_DIFFUSE,[0.80,0.80,0.80,1.0])
    _reset_nivel()

def reset():
    init()

def display(draw_p1,draw_p2):
    glClearColor(0.88,0.88,0.88,1.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    camera.apply(state.WIN_W,state.WIN_H)
    _draw_floor(); _draw_objetos()
    players.draw_players(draw_p1,draw_p2)
    _draw_hud_nivel1()
    glutSwapBuffers()

def update(_v):
    players.update(); _check_colisiones()
    for oid in _anim_obj:
        if _anim_obj[oid]>0.0: _anim_obj[oid]=max(0.0,_anim_obj[oid]-0.025)
    for attr in ("hud_fb_timer_p1","hud_fb_timer_p2"):
        if not hasattr(state,attr): setattr(state,attr,0)
    if state.hud_fb_timer_p1>0:
        state.hud_fb_timer_p1-=1
        if state.hud_fb_timer_p1==0: state.hud_fb_p1=""
    if state.hud_fb_timer_p2>0:
        state.hud_fb_timer_p2-=1
        if state.hud_fb_timer_p2==0: state.hud_fb_p2=""

def keyboard(key,_x,_y):
    if key==b'w': state.k_w=True
    elif key==b's': state.k_s=True
    elif key==b'a': state.k_a=True
    elif key==b'd': state.k_d=True

def keyboard_up(key,_x,_y):
    if key==b'w': state.k_w=False
    elif key==b's': state.k_s=False
    elif key==b'a': state.k_a=False
    elif key==b'd': state.k_d=False

def special_keys(key,_x,_y):
    if key==GLUT_KEY_UP:    state.k_up=True
    elif key==GLUT_KEY_DOWN:  state.k_down=True
    elif key==GLUT_KEY_LEFT:  state.k_left=True
    elif key==GLUT_KEY_RIGHT: state.k_right=True

def special_keys_up(key,_x,_y):
    if key==GLUT_KEY_UP:    state.k_up=False
    elif key==GLUT_KEY_DOWN:  state.k_down=False
    elif key==GLUT_KEY_LEFT:  state.k_left=False
    elif key==GLUT_KEY_RIGHT: state.k_right=False
