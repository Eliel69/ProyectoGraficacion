# ============================================================
# niveles/nivel1.py  — El Valle de los Colores
# ------------------------------------------------------------
# OBJETIVO PEDAGOGICO: Discriminacion cromatica.
# El nino debe asociar una instruccion textual ("Toca el cubo Rojo!")
# con el objeto correcto del mapa, usando solo el color como pista.
#
# MECANICA:
#   - 10 objetos (5 cubos + 5 esferas) de 10 colores distintos.
#   - J1 y J2 reciben instrucciones INDEPENDIENTES Y ALEATORIAS.
#   - +2 pts por acierto, -1 pt por error (minimo 0).
#   - Al llegar a META_PUNTOS=20 se congela el nivel.
#
# ALEATORIEDAD: random.randint(0, len(_OBJETOS)-1) elige el
# siguiente objetivo. Cada jugador tiene su propio _obj_p1/_obj_p2
# y su propio cooldown, por eso las instrucciones son independientes.
#
# COLISION: distancia euclidiana 2D en el plano XZ.
#   dist = sqrt((px-ox)^2 + (pz-oz)^2) < (RADIO_OBJ + RADIO_JUG)
# ============================================================
# niveles/nivel1.py  — El Valle de los Colores
# Dos formas (cubo y esfera), 10 colores distintos.
# +2 por acierto, -1 por error. Meta: 20 puntos.
# Instrucciones independientes para J1 y J2.
import math, random
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *
from niveles     import state, camera, players

# -- 10 colores, 2 formas (5 cubos + 5 esferas) dispersos --
_OBJETOS = [
    {"id":0,  "nombre":"Rojo",       "color":(0.90,0.10,0.10), "x":-9.0, "z":-7.0, "forma":"cubo"},
    {"id":1,  "nombre":"Azul",       "color":(0.10,0.25,0.95), "x": 9.0, "z":-7.0, "forma":"esfera"},
    {"id":2,  "nombre":"Amarillo",   "color":(0.95,0.88,0.05), "x": 6.0, "z": 7.0, "forma":"cubo"},
    {"id":3,  "nombre":"Verde",      "color":(0.10,0.80,0.20), "x":-6.0, "z": 7.0, "forma":"esfera"},
    {"id":4,  "nombre":"Naranja",    "color":(0.98,0.52,0.05), "x": 2.0, "z":-9.0, "forma":"esfera"},
    {"id":5,  "nombre":"Morado",     "color":(0.65,0.10,0.90), "x":-2.0, "z": 9.0, "forma":"cubo"},
    {"id":6,  "nombre":"Rosa",       "color":(0.98,0.45,0.75), "x": 9.0, "z": 2.0, "forma":"cubo"},
    {"id":7,  "nombre":"Celeste",    "color":(0.30,0.85,0.98), "x":-9.0, "z": 2.0, "forma":"esfera"},
    {"id":8,  "nombre":"Cafe",       "color":(0.60,0.35,0.10), "x":-4.0, "z":-5.0, "forma":"esfera"},
    {"id":9,  "nombre":"Blanco",     "color":(0.95,0.95,0.95), "x": 4.0, "z": 5.0, "forma":"cubo"},
]

_RADIO_OBJ = 1.0
_LADO      = 1.2
_RADIO_JUG = 0.5

_obj_p1 = 0
_obj_p2 = 1
_anim_obj = {}
_cooldown_p1 = 0
_cooldown_p2 = 0
_mostrando_intro = True   # True = mostrar instrucciones antes de jugar


def _reset_posiciones():
    state.p1_x=-4.0; state.p1_z=0.0; state.p1_rot=0.0
    state.p2_x= 4.0; state.p2_z=0.0; state.p2_rot=180.0
    state.p1_walking=state.p2_walking=False
    state.p1_anim=state.p2_anim=0.0
    state.k_w=state.k_s=state.k_a=state.k_d=False
    state.k_up=state.k_down=state.k_left=state.k_right=False


def _reset_nivel():
    global _obj_p1,_obj_p2,_anim_obj,_cooldown_p1,_cooldown_p2
    _reset_posiciones()
    state.nivel_score_p1=0
    state.nivel_score_p2=0
    state.nivel_completado=False
    state.nivel_ganador=0
    state.mostrar_resultado=False
    state.resultado_timer=0
    state.hud_fb_p1=""; state.hud_fb_timer_p1=0
    state.hud_fb_p2=""; state.hud_fb_timer_p2=0
    global _mostrando_intro
    _anim_obj={o["id"]:0.0 for o in _OBJETOS}
    _cooldown_p1=_cooldown_p2=0
    _mostrando_intro=True
    _nueva_p1(); _nueva_p2()


def _nueva_p1():
    global _obj_p1
    _obj_p1 = random.randint(0,len(_OBJETOS)-1)
    o = _OBJETOS[_obj_p1]
    state.hud_msg = "J1: Toca el " + o["forma"] + " " + o["nombre"] + "!"

def _nueva_p2():
    global _obj_p2
    _obj_p2 = random.randint(0,len(_OBJETOS)-1)
    o = _OBJETOS[_obj_p2]
    state.hud_msg2 = "J2: Toca el " + o["forma"] + " " + o["nombre"] + "!"


def _dist2d(ax,az,bx,bz):
    return math.sqrt((ax-bx)**2+(az-bz)**2)


def _check_colisiones():
    """
    Detecta colision entre cada jugador y los objetos del nivel.

    Cooldown: despues de una colision, el jugador tiene ~1.8s
    (110 frames a 60fps) de inmunidad. Esto evita que al quedarse
    parado sobre un objeto se acumulen puntos/penalizaciones.

    Flujo por jugador:
      1. Si cooldown > 0: decrementar y saltar.
      2. Para cada objeto: calcular distancia 2D.
      3. Si distancia < (radio_obj + radio_jug): colision detectada.
         - Si es el objetivo: +2 pts, animacion, nueva instruccion.
         - Si no es el objetivo: -1 pt, feedback de error.
      4. Activar cooldown y generar nueva instruccion.
    """
    global _cooldown_p1,_cooldown_p2
    if state.nivel_completado or _mostrando_intro:
        return

    if _cooldown_p1>0:
        _cooldown_p1-=1
    else:
        for obj in _OBJETOS:
            if _dist2d(state.p1_x,state.p1_z,obj["x"],obj["z"])<(_RADIO_OBJ+_RADIO_JUG):
                if obj["id"]==_obj_p1:
                    state.nivel_score_p1=min(state.nivel_score_p1+2, state.META_PUNTOS)
                    state.hud_fb_p1="Correcto! +2"; state.hud_fb_timer_p1=80
                    _anim_obj[obj["id"]]=1.0
                else:
                    state.nivel_score_p1=max(0,state.nivel_score_p1-1)
                    state.hud_fb_p1="Ups! -1"; state.hud_fb_timer_p1=70
                _cooldown_p1=110
                _nueva_p1()
                _check_meta()
                break

    if _cooldown_p2>0:
        _cooldown_p2-=1
    else:
        for obj in _OBJETOS:
            if _dist2d(state.p2_x,state.p2_z,obj["x"],obj["z"])<(_RADIO_OBJ+_RADIO_JUG):
                if obj["id"]==_obj_p2:
                    state.nivel_score_p2=min(state.nivel_score_p2+2, state.META_PUNTOS)
                    state.hud_fb_p2="Correcto! +2"; state.hud_fb_timer_p2=80
                    _anim_obj[obj["id"]]=1.0
                else:
                    state.nivel_score_p2=max(0,state.nivel_score_p2-1)
                    state.hud_fb_p2="Ups! -1"; state.hud_fb_timer_p2=70
                _cooldown_p2=110
                _nueva_p2()
                _check_meta()
                break


def _check_meta():
    if state.nivel_completado:
        return
    if state.nivel_score_p1>=state.META_PUNTOS:
        _terminar_nivel(1)
    elif state.nivel_score_p2>=state.META_PUNTOS:
        _terminar_nivel(2)


def _terminar_nivel(ganador):
    state.nivel_completado=True
    state.nivel_ganador=ganador
    state.mostrar_resultado=True
    state.resultado_timer=220   # ~3.7s antes de pasar al nivel 2
    # Acumular puntaje
    state.score_p1+=state.nivel_score_p1
    state.score_p2+=state.nivel_score_p2


# -- Dibujo -------------------------------------------------------
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


def _draw_cubo(s):
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
        spin=_anim_obj.get(obj["id"],0.0)
        if spin>0.0:
            glRotatef(spin*360.0,0,1,0)
        glDisable(GL_LIGHTING)
        r,g,b=obj["color"]
        bright=0.22 if (not state.nivel_completado and obj["id"] not in (_obj_p1,_obj_p2)) else 0.0
        if not state.nivel_completado and obj["id"]==_obj_p1:
            glColor3f(min(r+0.18,1),min(g+0.18,1),min(b+0.18,1))
        elif not state.nivel_completado and obj["id"]==_obj_p2:
            glColor3f(min(r+0.12,1),min(g+0.12,1),min(b+0.12,1))
        else:
            glColor3f(r,g,b)
        if obj["forma"]=="cubo":
            _draw_cubo(_LADO)
        else:
            q=gluNewQuadric(); glTranslatef(0,1.0,0); gluSphere(q,1.0,18,18); gluDeleteQuadric(q)
        glEnable(GL_LIGHTING)
        glPopMatrix()


def _draw_hud():
    from OpenGL.GLUT import (GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_HELVETICA_12,
                              glutBitmapCharacter, glutGet,
                              GLUT_WINDOW_WIDTH, GLUT_WINDOW_HEIGHT)
    w=glutGet(GLUT_WINDOW_WIDTH); h=glutGet(GLUT_WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    from OpenGL.GLU import gluOrtho2D
    gluOrtho2D(0,w,0,h)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST)

    def txt(x,y,s,font,col):
        glColor3fv(col); glRasterPos2f(x,y)
        for c in s: glutBitmapCharacter(font,ord(c))

    def panel(x,y,pw,ph,r,g,b,a=0.70):
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(r,g,b,a)
        glBegin(GL_QUADS)
        glVertex2f(x,y); glVertex2f(x+pw,y)
        glVertex2f(x+pw,y+ph); glVertex2f(x,y+ph)
        glEnd(); glDisable(GL_BLEND)

    # -- Pantalla de instrucciones (intro) --
    if _mostrando_intro:
        panel(w//2-310,h//2-170,620,340,0.0,0.0,0.0,0.88)
        txt(w//2-200,h//2+145,"NIVEL 1 - Valle de los Colores",
            GLUT_BITMAP_HELVETICA_18,(1.0,0.85,0.20))
        lineas = [
            ("OBJETIVO:", GLUT_BITMAP_HELVETICA_18, (0.95,0.90,0.40)),
            ("Cada jugador tiene su propia instruccion en pantalla.", GLUT_BITMAP_HELVETICA_12, (0.90,0.90,0.90)),
            ("Camina hacia la figura del color y forma indicados.", GLUT_BITMAP_HELVETICA_12, (0.90,0.90,0.90)),
            ("", None, None),
            ("+2 puntos por tocar la figura correcta.", GLUT_BITMAP_HELVETICA_12, (0.40,1.00,0.40)),
            ("-1 punto si tocas una figura equivocada.", GLUT_BITMAP_HELVETICA_12, (1.00,0.45,0.45)),
            ("El primero en llegar a 20 puntos gana el nivel.", GLUT_BITMAP_HELVETICA_12, (0.90,0.90,0.90)),
            ("", None, None),
            ("CONTROLES:", GLUT_BITMAP_HELVETICA_18, (0.95,0.90,0.40)),
            ("J1 (ROJO):  W/A/S/D para moverse", GLUT_BITMAP_HELVETICA_12, (1.00,0.65,0.65)),
            ("J2 (AZUL):  Flechas para moverse", GLUT_BITMAP_HELVETICA_12, (0.65,0.75,1.00)),
        ]
        base_y = h//2+105
        for lbl,font,col in lineas:
            if font: txt(w//2-260, base_y, lbl, font, col)
            base_y -= 22
        txt(w//2-195, h//2-185,
            ">>> Presiona CUALQUIER TECLA para empezar <<<",
            GLUT_BITMAP_HELVETICA_12,(0.75,0.75,0.40))
        glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW);  glPopMatrix()
        return

    # -- Pantalla de resultado de nivel --
    if state.mostrar_resultado:
        panel(w//2-300,h//2-120,600,240,0,0,0,0.85)
        txt(w//2-210,h//2+80,"NIVEL 1 COMPLETADO!",GLUT_BITMAP_HELVETICA_18,(0.95,0.85,0.20))
        txt(w//2-200,h//2+50,
            "J1: "+str(state.nivel_score_p1)+" pts     J2: "+str(state.nivel_score_p2)+" pts",
            GLUT_BITMAP_HELVETICA_18,(0.90,0.90,1.00))
        g_str="JUGADOR "+str(state.nivel_ganador)+" llego primero!"
        col=(0.90,0.20,0.20) if state.nivel_ganador==1 else (0.20,0.40,0.95)
        txt(w//2-160,h//2+15,g_str,GLUT_BITMAP_HELVETICA_18,col)
        txt(w//2-180,h//2-20,
            "Total acumulado - J1: "+str(state.score_p1)+"   J2: "+str(state.score_p2),
            GLUT_BITMAP_HELVETICA_12,(0.80,0.80,0.80))
        txt(w//2-140,h//2-55,"Pasando al Nivel 2...",GLUT_BITMAP_HELVETICA_12,(0.55,0.90,0.55))
        glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW);  glPopMatrix()
        return

    # -- HUD normal --
    panel(0,h-52,w,52,0,0,0,0.55)
    txt(10,h-22,"NIVEL 1 - Valle de los Colores",GLUT_BITMAP_HELVETICA_18,(1.0,0.85,0.20))
    txt(w-230,h-22,"J1: "+str(state.nivel_score_p1)+"/20   J2: "+str(state.nivel_score_p2)+"/20",
        GLUT_BITMAP_HELVETICA_18,(0.90,0.90,1.00))
    txt(w//2-200,h-44,"Total: J1="+str(state.score_p1)+"  J2="+str(state.score_p2),
        GLUT_BITMAP_HELVETICA_12,(0.65,0.65,0.65))

    # Instruccion J1
    panel(0,h-92,310,38,0.50,0.05,0.05,0.75)
    txt(8,h-72,state.hud_msg,GLUT_BITMAP_HELVETICA_18,(1.0,0.70,0.70))

    # Instruccion J2
    panel(w-310,h-92,310,38,0.05,0.10,0.55,0.75)
    txt(w-305,h-72,state.hud_msg2,GLUT_BITMAP_HELVETICA_18,(0.70,0.80,1.00))

    # Feedback J1
    if state.hud_fb_p1:
        col=(0.20,1.0,0.30) if "orrecto" in state.hud_fb_p1 else (1.0,0.35,0.35)
        txt(20,h//2,state.hud_fb_p1,GLUT_BITMAP_HELVETICA_18,col)
    # Feedback J2
    if state.hud_fb_p2:
        col=(0.20,1.0,0.30) if "orrecto" in state.hud_fb_p2 else (1.0,0.35,0.35)
        txt(w-250,h//2,state.hud_fb_p2,GLUT_BITMAP_HELVETICA_18,col)

    # Etiquetas inferiores
    panel(0,0,200,36,0.50,0.05,0.05,0.70)
    panel(w-200,0,200,36,0.05,0.10,0.55,0.70)
    txt(8,14,"J1  WASD - mover",GLUT_BITMAP_HELVETICA_12,(1.0,0.75,0.75))
    txt(w-195,14,"J2  Flechas - mover",GLUT_BITMAP_HELVETICA_12,(0.75,0.85,1.0))
    txt(w//2-140,14,"ESC: confirmar salida al lobby",GLUT_BITMAP_HELVETICA_12,(0.55,0.55,0.55))

    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()


# -- API publica --------------------------------------------------
def init():
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING); glEnable(GL_LIGHT0)
    # -- Iluminacion Phong: Nivel 1 (Valle de los Colores) ------
    # Luz principal blanca desde arriba-adelante
    glLightfv(GL_LIGHT0, GL_POSITION, [2.0, 12.0, 6.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.22, 0.22, 0.22, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.85, 0.85, 0.85, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.00, 1.00, 1.00, 1.0])
    # Luz de relleno lateral suave (LIGHT1)
    glEnable(GL_LIGHT1)
    glLightfv(GL_LIGHT1, GL_POSITION, [-6.0, 6.0, -4.0, 1.0])
    glLightfv(GL_LIGHT1, GL_AMBIENT,  [0.0,  0.0,  0.0,  1.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE,  [0.25, 0.25, 0.30, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.0,  0.0,  0.0,  1.0])
    # Material global con especular moderado
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT, GL_SPECULAR,  [0.50, 0.50, 0.50, 1.0])
    glMaterialf (GL_FRONT, GL_SHININESS, 48.0)
    glShadeModel(GL_SMOOTH)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.10, 0.10, 0.10, 1.0])
    _reset_nivel()


def reset():
    _reset_nivel()


def display_sin_swap(draw_p1,draw_p2):
    glClearColor(0.88,0.88,0.88,1.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    camera.apply(state.WIN_W,state.WIN_H)
    _draw_floor(); _draw_objetos()
    if not state.mostrar_resultado:
        players.draw_players(draw_p1,draw_p2)
    _draw_hud()



def display(draw_p1,draw_p2):
    display_sin_swap(draw_p1,draw_p2)
    glutSwapBuffers()

def update(_v):
    global _cooldown_p1,_cooldown_p2
    if not state.mostrar_resultado:
        if not _mostrando_intro:
            players.update()
        _check_colisiones()
        for oid in _anim_obj:
            if _anim_obj[oid]>0.0: _anim_obj[oid]=max(0.0,_anim_obj[oid]-0.025)
        if state.hud_fb_timer_p1>0:
            state.hud_fb_timer_p1-=1
            if state.hud_fb_timer_p1==0: state.hud_fb_p1=""
        if state.hud_fb_timer_p2>0:
            state.hud_fb_timer_p2-=1
            if state.hud_fb_timer_p2==0: state.hud_fb_p2=""
    else:
        # Countdown para pasar al nivel 2
        if state.resultado_timer>0:
            state.resultado_timer-=1
        # La transicion la maneja main_arcade via nivel_completado


def keyboard(key,_x,_y):
    global _mostrando_intro
    if _mostrando_intro:
        _mostrando_intro=False; return
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
    global _mostrando_intro
    if _mostrando_intro:
        _mostrando_intro=False; return
    if key==GLUT_KEY_UP:    state.k_up=True
    elif key==GLUT_KEY_DOWN:  state.k_down=True
    elif key==GLUT_KEY_LEFT:  state.k_left=True
    elif key==GLUT_KEY_RIGHT: state.k_right=True

def special_keys_up(key,_x,_y):
    if key==GLUT_KEY_UP:    state.k_up=False
    elif key==GLUT_KEY_DOWN:  state.k_down=False
    elif key==GLUT_KEY_LEFT:  state.k_left=False
    elif key==GLUT_KEY_RIGHT: state.k_right=False
