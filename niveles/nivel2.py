# niveles/nivel2.py  — El Bosque de las Formas
# 8 formas distintas (misma paleta dorada), instrucciones independientes J1/J2.
# +2 acierto, -1 error. Meta 20 pts. Acumula al score global.
import math, random
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *
from niveles     import state, camera, players

_COLOR = (0.82,0.64,0.18)   # dorado unico para todas las formas

_FORMAS = [
    {"id":0,"nombre":"esfera",       "pista":"redonda",          "x":-8.0,"z":-6.0,"tipo":"esfera"},
    {"id":1,"nombre":"cubo",         "pista":"con esquinas",     "x": 8.0,"z":-6.0,"tipo":"cubo"},
    {"id":2,"nombre":"cilindro",     "pista":"como un tubo",     "x":-8.0,"z": 6.0,"tipo":"cilindro"},
    {"id":3,"nombre":"cono",         "pista":"con punta arriba", "x": 8.0,"z": 6.0,"tipo":"cono"},
    {"id":4,"nombre":"piramide",     "pista":"como una montania","x": 0.0,"z":-9.0,"tipo":"piramide"},
    {"id":5,"nombre":"toroide",      "pista":"como una dona",    "x": 0.0,"z": 9.0,"tipo":"toroide"},
    {"id":6,"nombre":"capsula",      "pista":"alargada y redonda","x":-4.5,"z": 0.0,"tipo":"capsula"},
    {"id":7,"nombre":"prisma",       "pista":"como un cristal",  "x": 4.5,"z": 0.0,"tipo":"prisma"},
]

_RADIO_OBJ=1.0; _RADIO_JUG=0.5; _LADO=1.1
_forma_p1=0; _forma_p2=1
_anim_forma={}; _cooldown_p1=0; _cooldown_p2=0
_mostrando_intro = True


def _reset_posiciones():
    state.p1_x=-1.5; state.p1_z=3.0; state.p1_rot=0.0
    state.p2_x= 1.5; state.p2_z=3.0; state.p2_rot=180.0
    state.p1_walking=state.p2_walking=False
    state.p1_anim=state.p2_anim=0.0
    state.k_w=state.k_s=state.k_a=state.k_d=False
    state.k_up=state.k_down=state.k_left=state.k_right=False


def _reset_nivel():
    global _forma_p1,_forma_p2,_anim_forma,_cooldown_p1,_cooldown_p2
    _reset_posiciones()
    state.nivel_score_p1=0; state.nivel_score_p2=0
    state.nivel_completado=False; state.nivel_ganador=0
    state.mostrar_resultado=False; state.resultado_timer=0
    state.hud_fb_p1=""; state.hud_fb_timer_p1=0
    state.hud_fb_p2=""; state.hud_fb_timer_p2=0
    global _mostrando_intro
    _anim_forma={f["id"]:0 for f in _FORMAS}
    _cooldown_p1=_cooldown_p2=0
    _mostrando_intro=True
    _nueva_p1(); _nueva_p2()


def _nueva_p1():
    global _forma_p1
    _forma_p1=random.randint(0,len(_FORMAS)-1)
    f=_FORMAS[_forma_p1]
    state.hud_msg="J1: Toca la figura "+f["pista"]+" ("+f["nombre"]+")!"

def _nueva_p2():
    global _forma_p2
    _forma_p2=random.randint(0,len(_FORMAS)-1)
    f=_FORMAS[_forma_p2]
    state.hud_msg2="J2: Toca la figura "+f["pista"]+" ("+f["nombre"]+")!"


def _dist2d(ax,az,bx,bz):
    return math.sqrt((ax-bx)**2+(az-bz)**2)


def _check_colisiones():
    global _cooldown_p1,_cooldown_p2
    if state.nivel_completado or _mostrando_intro: return

    if _cooldown_p1>0: _cooldown_p1-=1
    else:
        for f in _FORMAS:
            if _dist2d(state.p1_x,state.p1_z,f["x"],f["z"])<(_RADIO_OBJ+_RADIO_JUG):
                if f["id"]==_forma_p1:
                    state.nivel_score_p1=min(state.nivel_score_p1+2,state.META_PUNTOS)
                    state.hud_fb_p1="Correcto! +2"; state.hud_fb_timer_p1=80
                    _anim_forma[f["id"]]=80
                else:
                    state.nivel_score_p1=max(0,state.nivel_score_p1-1)
                    state.hud_fb_p1="Ups! -1"; state.hud_fb_timer_p1=70
                _cooldown_p1=120; _nueva_p1(); _check_meta(); break

    if _cooldown_p2>0: _cooldown_p2-=1
    else:
        for f in _FORMAS:
            if _dist2d(state.p2_x,state.p2_z,f["x"],f["z"])<(_RADIO_OBJ+_RADIO_JUG):
                if f["id"]==_forma_p2:
                    state.nivel_score_p2=min(state.nivel_score_p2+2,state.META_PUNTOS)
                    state.hud_fb_p2="Correcto! +2"; state.hud_fb_timer_p2=80
                    _anim_forma[f["id"]]=80
                else:
                    state.nivel_score_p2=max(0,state.nivel_score_p2-1)
                    state.hud_fb_p2="Ups! -1"; state.hud_fb_timer_p2=70
                _cooldown_p2=120; _nueva_p2(); _check_meta(); break


def _check_meta():
    if state.nivel_completado: return
    if state.nivel_score_p1>=state.META_PUNTOS: _terminar(1)
    elif state.nivel_score_p2>=state.META_PUNTOS: _terminar(2)

def _terminar(ganador):
    state.nivel_completado=True; state.nivel_ganador=ganador
    state.mostrar_resultado=True; state.resultado_timer=220
    state.score_p1+=state.nivel_score_p1
    state.score_p2+=state.nivel_score_p2


# -- Dibujo -------------------------------------------------------
def _draw_floor():
    glDisable(GL_LIGHTING)
    glColor3f(0.22,0.45,0.18)
    glBegin(GL_QUADS)
    glVertex3f(-16,-0.01, 16); glVertex3f(16,-0.01, 16)
    glVertex3f(16,-0.01,-16); glVertex3f(-16,-0.01,-16)
    glEnd()
    glEnable(GL_LIGHTING)
    for tx,tz in [(-12,-12),(12,-12),(-12,12),(12,12),(-8,-14),(8,-14),(0,-13)]:
        _draw_tree(tx,tz)


def _draw_tree(cx,cz):
    glDisable(GL_LIGHTING)
    q=gluNewQuadric()
    glColor3f(0.42,0.26,0.10)
    glPushMatrix(); glTranslatef(cx,0,cz); gluCylinder(q,0.18,0.14,2.0,8,2); glPopMatrix()
    glColor3f(0.15,0.55,0.12)
    glPushMatrix(); glTranslatef(cx,2.0,cz); gluSphere(q,1.0,10,10); glPopMatrix()
    gluDeleteQuadric(q); glEnable(GL_LIGHTING)


def _set_color(fid):
    glDisable(GL_LIGHTING)
    r,g,b=_COLOR
    if not state.nivel_completado:
        if fid==_forma_p1: glColor3f(min(r+0.15,1),min(g+0.15,1),min(b+0.15,1)); return
        if fid==_forma_p2: glColor3f(min(r+0.10,1),min(g+0.10,1),min(b+0.10,1)); return
    glColor3f(r,g,b)


def _draw_nombre_3d(f):
    """Dibuja el nombre de la forma en coordenadas locales (ya dentro de glPushMatrix)."""
    from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_12, glutBitmapCharacter
    lbl = f["nombre"].upper()
    col = (1.0,0.95,0.40) if (f["id"]==_forma_p1 or f["id"]==_forma_p2) else (0.85,0.85,0.85)
    glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST)
    glColor3fv(col)
    # Posicion LOCAL: centrado sobre la figura, altura fija 2.6
    glRasterPos3f(-0.30, 2.6, 0.0)
    for c in lbl: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)


def _draw_formas():
    for f in _FORMAS:
        glPushMatrix(); glTranslatef(f["x"],0.0,f["z"])
        anim=_anim_forma.get(f["id"],0)
        if anim>0: glTranslatef(0,math.sin(anim/80.0*math.pi)*1.5,0)
        _set_color(f["id"])
        t=f["tipo"]; q=gluNewQuadric()
        if t=="esfera":
            glTranslatef(0,1.0,0); gluSphere(q,0.9,18,18)
        elif t=="cubo":
            s=_LADO
            glBegin(GL_QUADS)
            for verts in [
                [(-s,s*2,s),(s,s*2,s),(s,s*2,-s),(-s,s*2,-s)],
                [(-s,0,-s),(s,0,-s),(s,0,s),(-s,0,s)],
                [(-s,0,s),(s,0,s),(s,s*2,s),(-s,s*2,s)],
                [(s,0,-s),(-s,0,-s),(-s,s*2,-s),(s,s*2,-s)],
                [(-s,0,-s),(-s,0,s),(-s,s*2,s),(-s,s*2,-s)],
                [(s,0,s),(s,0,-s),(s,s*2,-s),(s,s*2,s)],
            ]:
                for v in verts: glVertex3fv(v)
            glEnd()
        elif t=="cilindro":
            gluCylinder(q,0.55,0.55,1.8,14,3)
            glPushMatrix(); glRotatef(180,1,0,0); gluDisk(q,0,0.55,14,1); glPopMatrix()
            glPushMatrix(); glTranslatef(0,0,1.8); gluDisk(q,0,0.55,14,1); glPopMatrix()
        elif t=="cono":
            glPushMatrix(); glRotatef(-90,1,0,0)  # apuntar hacia arriba
            gluCylinder(q,0.80,0.0,2.0,14,4)
            glRotatef(180,1,0,0); gluDisk(q,0,0.80,14,1)
            glPopMatrix()
        elif t=="piramide":
            h2=2.0; b2=0.9
            glBegin(GL_TRIANGLES)
            apex=(0,h2,0)
            bases=[(-b2,0,-b2),(b2,0,-b2),(b2,0,b2),(-b2,0,b2)]
            for i in range(4):
                for v in [bases[i],bases[(i+1)%4],apex]: glVertex3fv(v)
            glEnd()
            glBegin(GL_QUADS)
            for v in bases: glVertex3fv(v)
            glEnd()
        elif t=="toroide":
            glTranslatef(0,0.8,0)
            R,r2,s1,s2=0.65,0.25,16,10
            for i in range(s1):
                a0=2*math.pi*i/s1; a1=2*math.pi*(i+1)/s1
                glBegin(GL_QUAD_STRIP)
                for j in range(s2+1):
                    b=2*math.pi*j/s2
                    for a in (a0,a1):
                        x=(R+r2*math.cos(b))*math.cos(a)
                        y=r2*math.sin(b)
                        z=(R+r2*math.cos(b))*math.sin(a)
                        glVertex3f(x,y,z)
                glEnd()
        elif t=="capsula":
            glTranslatef(0,0.5,0); gluCylinder(q,0.45,0.45,1.2,14,3)
            glPushMatrix(); glRotatef(180,1,0,0); gluSphere(q,0.45,14,10); glPopMatrix()
            glPushMatrix(); glTranslatef(0,0,1.2); gluSphere(q,0.45,14,10); glPopMatrix()
        elif t=="prisma":
            sides=6; r3=0.75; ht=1.8
            glBegin(GL_TRIANGLE_FAN); glVertex3f(0,ht,0)
            for i in range(sides+1):
                a=2*math.pi*i/sides; glVertex3f(r3*math.cos(a),ht,r3*math.sin(a))
            glEnd()
            glBegin(GL_TRIANGLE_FAN); glVertex3f(0,0,0)
            for i in range(sides+1):
                a=2*math.pi*i/sides; glVertex3f(r3*math.cos(a),0,r3*math.sin(a))
            glEnd()
            glBegin(GL_QUAD_STRIP)
            for i in range(sides+1):
                a=2*math.pi*i/sides
                glVertex3f(r3*math.cos(a),0,r3*math.sin(a))
                glVertex3f(r3*math.cos(a),ht,r3*math.sin(a))
            glEnd()
        # -- Aristas negras sobre la forma (solo formas con aristas) --
        if t in ("cubo","piramide","prisma"):
            glLineWidth(2.0)
            glColor3f(0.0,0.0,0.0)
            glPolygonOffset(1.0,1.0)
            glEnable(GL_POLYGON_OFFSET_LINE)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            if t=="cubo":
                s2=_LADO
                glBegin(GL_QUADS)
                for verts2 in [
                    [(-s2,s2*2,s2),(s2,s2*2,s2),(s2,s2*2,-s2),(-s2,s2*2,-s2)],
                    [(-s2,0,-s2),(s2,0,-s2),(s2,0,s2),(-s2,0,s2)],
                    [(-s2,0,s2),(s2,0,s2),(s2,s2*2,s2),(-s2,s2*2,s2)],
                    [(s2,0,-s2),(-s2,0,-s2),(-s2,s2*2,-s2),(s2,s2*2,-s2)],
                    [(-s2,0,-s2),(-s2,0,s2),(-s2,s2*2,s2),(-s2,s2*2,-s2)],
                    [(s2,0,s2),(s2,0,-s2),(s2,s2*2,-s2),(s2,s2*2,s2)],
                ]:
                    for v2 in verts2: glVertex3fv(v2)
                glEnd()
            elif t=="piramide":
                h3=2.0; b3=0.9
                bases2=[(-b3,0,-b3),(b3,0,-b3),(b3,0,b3),(-b3,0,b3)]
                apex2=(0,h3,0)
                glBegin(GL_TRIANGLES)
                for i2 in range(4):
                    for v2 in [bases2[i2],bases2[(i2+1)%4],apex2]: glVertex3fv(v2)
                glEnd()
                glBegin(GL_QUADS)
                for v2 in bases2: glVertex3fv(v2)
                glEnd()
            elif t=="prisma":
                import math as _m
                sides2=6; r4=0.75; ht2=1.8
                glBegin(GL_TRIANGLE_FAN); glVertex3f(0,ht2,0)
                for i2 in range(sides2+1):
                    a2=2*_m.pi*i2/sides2; glVertex3f(r4*_m.cos(a2),ht2,r4*_m.sin(a2))
                glEnd()
                glBegin(GL_QUAD_STRIP)
                for i2 in range(sides2+1):
                    a2=2*_m.pi*i2/sides2
                    glVertex3f(r4*_m.cos(a2),0,r4*_m.sin(a2))
                    glVertex3f(r4*_m.cos(a2),ht2,r4*_m.sin(a2))
                glEnd()
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glDisable(GL_POLYGON_OFFSET_LINE)
            glLineWidth(1.0)
        gluDeleteQuadric(q); glEnable(GL_LIGHTING)
        _draw_nombre_3d(f)
        glPopMatrix()


def _draw_hud():
    from OpenGL.GLUT import (GLUT_BITMAP_HELVETICA_18,GLUT_BITMAP_HELVETICA_12,
                              glutBitmapCharacter,glutGet,
                              GLUT_WINDOW_WIDTH,GLUT_WINDOW_HEIGHT)
    w=glutGet(GLUT_WINDOW_WIDTH); h=glutGet(GLUT_WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    from OpenGL.GLU import gluOrtho2D; gluOrtho2D(0,w,0,h)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST)

    def txt(x,y,s,font,col):
        glColor3fv(col); glRasterPos2f(x,y)
        for c in s: glutBitmapCharacter(font,ord(c))
    def panel(x,y,pw,ph,r,g,b,a=0.70):
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(r,g,b,a)
        glBegin(GL_QUADS)
        glVertex2f(x,y); glVertex2f(x+pw,y); glVertex2f(x+pw,y+ph); glVertex2f(x,y+ph)
        glEnd(); glDisable(GL_BLEND)

    if _mostrando_intro:
        panel(w//2-310,h//2-170,620,340,0.0,0.0,0.0,0.88)
        txt(w//2-200,h//2+145,"NIVEL 2 - Bosque de las Formas",
            GLUT_BITMAP_HELVETICA_18,(1.0,0.85,0.20))
        lineas = [
            ("OBJETIVO:", GLUT_BITMAP_HELVETICA_18, (0.95,0.90,0.40)),
            ("Ahora todos los objetos son del mismo color dorado.", GLUT_BITMAP_HELVETICA_12, (0.90,0.90,0.90)),
            ("Debes identificarlos por su FORMA, no por su color.", GLUT_BITMAP_HELVETICA_12, (0.90,0.90,0.90)),
            ("", None, None),
            ("+2 puntos por tocar la forma correcta.", GLUT_BITMAP_HELVETICA_12, (0.40,1.00,0.40)),
            ("-1 punto si tocas una forma equivocada.", GLUT_BITMAP_HELVETICA_12, (1.00,0.45,0.45)),
            ("El primero en llegar a 20 puntos gana el nivel.", GLUT_BITMAP_HELVETICA_12, (0.90,0.90,0.90)),
            ("", None, None),
            ("CONTROLES:", GLUT_BITMAP_HELVETICA_18, (0.95,0.90,0.40)),
            ("J1 (ROJO):  W/A/S/D para moverse", GLUT_BITMAP_HELVETICA_12, (1.00,0.65,0.65)),
            ("J2 (AZUL):  Flechas para moverse", GLUT_BITMAP_HELVETICA_12, (0.65,0.75,1.00)),
            ("Puntaje acumulado - J1: "+str(state.score_p1)+"   J2: "+str(state.score_p2), GLUT_BITMAP_HELVETICA_12, (0.75,0.75,0.75)),
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

    if state.mostrar_resultado:
        panel(w//2-300,h//2-120,600,240,0,0,0,0.85)
        txt(w//2-210,h//2+80,"NIVEL 2 COMPLETADO!",GLUT_BITMAP_HELVETICA_18,(0.95,0.85,0.20))
        txt(w//2-200,h//2+50,
            "J1: "+str(state.nivel_score_p1)+" pts     J2: "+str(state.nivel_score_p2)+" pts",
            GLUT_BITMAP_HELVETICA_18,(0.90,0.90,1.00))
        g_str="JUGADOR "+str(state.nivel_ganador)+" llego primero!"
        col=(0.90,0.20,0.20) if state.nivel_ganador==1 else (0.20,0.40,0.95)
        txt(w//2-160,h//2+15,g_str,GLUT_BITMAP_HELVETICA_18,col)
        txt(w//2-200,h//2-20,
            "Total acumulado - J1: "+str(state.score_p1)+"   J2: "+str(state.score_p2),
            GLUT_BITMAP_HELVETICA_12,(0.80,0.80,0.80))
        txt(w//2-140,h//2-55,"Pasando al Nivel 3...",GLUT_BITMAP_HELVETICA_12,(0.55,0.90,0.55))
        glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW);  glPopMatrix()
        return

    panel(0,h-52,w,52,0,0,0,0.55)
    txt(10,h-22,"NIVEL 2 - Bosque de las Formas",GLUT_BITMAP_HELVETICA_18,(1.0,0.85,0.20))
    txt(w-230,h-22,"J1: "+str(state.nivel_score_p1)+"/20   J2: "+str(state.nivel_score_p2)+"/20",
        GLUT_BITMAP_HELVETICA_18,(0.90,0.90,1.00))
    txt(w//2-200,h-44,"Total: J1="+str(state.score_p1)+"  J2="+str(state.score_p2),
        GLUT_BITMAP_HELVETICA_12,(0.65,0.65,0.65))

    panel(0,h-98,w//2-10,44,0.50,0.05,0.05,0.75)
    txt(8,h-76,state.hud_msg,GLUT_BITMAP_HELVETICA_12,(1.0,0.80,0.80))
    panel(w//2+10,h-98,w//2-10,44,0.05,0.10,0.55,0.75)
    txt(w//2+18,h-76,state.hud_msg2,GLUT_BITMAP_HELVETICA_12,(0.80,0.88,1.00))

    if state.hud_fb_p1:
        col=(0.20,1.0,0.30) if "orrecto" in state.hud_fb_p1 else (1.0,0.35,0.35)
        txt(20,h//2,state.hud_fb_p1,GLUT_BITMAP_HELVETICA_18,col)
    if state.hud_fb_p2:
        col=(0.20,1.0,0.30) if "orrecto" in state.hud_fb_p2 else (1.0,0.35,0.35)
        txt(w-250,h//2,state.hud_fb_p2,GLUT_BITMAP_HELVETICA_18,col)

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
    # -- Iluminacion Phong: Nivel 2 (Bosque de las Formas) ------
    # Luz solar cálida desde arriba-derecha
    glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 14.0, 3.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.18, 0.20, 0.14, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.90, 0.88, 0.75, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.00, 0.95, 0.80, 1.0])
    # Relleno desde izquierda (simula cielo)
    glEnable(GL_LIGHT1)
    glLightfv(GL_LIGHT1, GL_POSITION, [-8.0, 8.0,  0.0, 1.0])
    glLightfv(GL_LIGHT1, GL_AMBIENT,  [0.0,  0.0,  0.0,  1.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE,  [0.20, 0.28, 0.22, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.0,  0.0,  0.0,  1.0])
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    # Especular alto para que las aristas doradas brillen
    glMaterialfv(GL_FRONT, GL_SPECULAR,  [0.70, 0.65, 0.30, 1.0])
    glMaterialf (GL_FRONT, GL_SHININESS, 72.0)
    glShadeModel(GL_SMOOTH)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.08, 0.10, 0.06, 1.0])
    _reset_nivel()

def reset():
    _reset_nivel()

def display_sin_swap(draw_p1,draw_p2):
    glClearColor(0.30,0.55,0.85,1.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    camera.apply(state.WIN_W,state.WIN_H)
    _draw_floor(); _draw_formas()
    if not state.mostrar_resultado:
        players.draw_players(draw_p1,draw_p2)
    _draw_hud()


def display(draw_p1,draw_p2):
    display_sin_swap(draw_p1,draw_p2)
    glutSwapBuffers()

def update(_v):
    if not state.mostrar_resultado:
        if not _mostrando_intro: players.update()
        _check_colisiones()
        for fid in _anim_forma:
            if _anim_forma[fid]>0: _anim_forma[fid]-=1
        if state.hud_fb_timer_p1>0:
            state.hud_fb_timer_p1-=1
            if state.hud_fb_timer_p1==0: state.hud_fb_p1=""
        if state.hud_fb_timer_p2>0:
            state.hud_fb_timer_p2-=1
            if state.hud_fb_timer_p2==0: state.hud_fb_p2=""
    else:
        if state.resultado_timer>0: state.resultado_timer-=1

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
