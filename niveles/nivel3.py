# niveles/nivel3.py  — El Salon de los Instrumentos
# Mecanica "Escucha y Memoriza":
#   1. Se reproduce UN sonido global (instrumento real).
#   2. Aparecen 10 objetos en el mapa (6 instrumentos + 4 distractores).
#   3. El jugador debe recordar el sonido y tocar el objeto correcto.
#   4. Al acercarse, cada objeto reproduce su propio sonido breve.
#   5. Acierto +2 pts, error -1 pt. Meta 20 pts. Puntaje acumulado.
#   6. J1 y J2 tienen instrucciones y puntuaciones independientes.

import math, random, os
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *
from niveles     import state, camera, players

# -- Audio --------------------------------------------------------
_AUDIO = False
_sonidos_cache = {}   # {nombre: pygame.mixer.Sound}

def _init_audio():
    global _AUDIO
    try:
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        _AUDIO = True
    except Exception as e:
        print(f"[nivel3] audio no disponible: {e}")

def _cargar_sonido(nombre):
    if not _AUDIO: return None
    if nombre in _sonidos_cache: return _sonidos_cache[nombre]
    import pygame
    base = os.path.join(os.path.dirname(__file__), 'sounds', nombre)
    try:
        s = pygame.mixer.Sound(base)
        _sonidos_cache[nombre] = s
        return s
    except Exception as e:
        print(f"[nivel3] no se pudo cargar {nombre}: {e}")
        return None

def _play(nombre, volumen=1.0):
    s = _cargar_sonido(nombre)
    if s:
        s.set_volume(volumen)
        s.play()

def _stop_all():
    if _AUDIO:
        import pygame
        pygame.mixer.stop()

# -- Definicion de objetos ----------------------------------------
# 6 instrumentos reales + 4 distractores
_INSTRUMENTOS = [
    {"id":0, "nombre":"guitarra",  "emoji":"Guitarra",  "archivo":"guitarra.wav",
     "color":(0.65,0.35,0.10), "x":-9.0, "z":-7.0},
    {"id":1, "nombre":"piano",     "emoji":"Piano",     "archivo":"piano.wav",
     "color":(0.20,0.20,0.20), "x": 9.0, "z":-7.0},
    {"id":2, "nombre":"trompeta",  "emoji":"Trompeta",  "archivo":"trompeta.wav",
     "color":(0.90,0.75,0.10), "x":-9.0, "z": 7.0},
    {"id":3, "nombre":"violin",    "emoji":"Violin",    "archivo":"violin.wav",
     "color":(0.60,0.20,0.05), "x": 9.0, "z": 7.0},
    {"id":4, "nombre":"flauta",    "emoji":"Flauta",    "archivo":"flauta.wav",
     "color":(0.70,0.90,0.95), "x": 0.0, "z":-10.0},
    {"id":5, "nombre":"bateria",   "emoji":"Bateria",   "archivo":"bateria.wav",
     "color":(0.35,0.35,0.40), "x": 0.0, "z": 10.0},
    # Distractores
    {"id":6, "nombre":"resorte",   "emoji":"???",       "archivo":"distractor1_resorte.wav",
     "color":(0.90,0.20,0.70), "x":-5.0, "z": 0.0},
    {"id":7, "nombre":"burbuja",   "emoji":"???",       "archivo":"distractor2_burbuja.wav",
     "color":(0.20,0.80,0.90), "x": 5.0, "z": 0.0},
    {"id":8, "nombre":"boing",     "emoji":"???",       "archivo":"distractor3_boing.wav",
     "color":(0.40,0.90,0.20), "x":-6.0, "z": 4.0},
    {"id":9, "nombre":"silbato",   "emoji":"???",       "archivo":"distractor4_silbato.wav",
     "color":(0.95,0.50,0.10), "x": 6.0, "z":-4.0},
]

# Solo los 6 instrumentos reales son posibles objetivos
_IDS_VALIDOS = [0,1,2,3,4,5]

_RADIO_OBJ  = 1.0
_RADIO_PROX = 3.5   # distancia para reproducir sonido de proximidad
_RADIO_JUG  = 0.5

# -- Estado interno -----------------------------------------------
_obj_p1 = 0    # id del instrumento objetivo de J1
_obj_p2 = 1    # id del instrumento objetivo de J2
_anim_obj = {}
_cooldown_p1 = 0
_cooldown_p2 = 0
_brillo = {}   # {obj_id: 0.0-1.0}
_mostrando_intro = True
# Fase de ronda: 'escuchar_p1','escuchar_p2','jugar'
# En la fase escuchar se reproduce el sonido global y se muestra el nombre
_fase_ronda = 'escuchar_p1'
_fase_timer = 0    # frames restantes en fase escuchar (180 = 3s)


def _reset_posiciones():
    state.p1_x=-4.0; state.p1_z=0.0; state.p1_rot=0.0
    state.p2_x= 4.0; state.p2_z=0.0; state.p2_rot=180.0
    state.p1_walking=state.p2_walking=False
    state.p1_anim=state.p2_anim=0.0
    state.k_w=state.k_s=state.k_a=state.k_d=False
    state.k_up=state.k_down=state.k_left=state.k_right=False


def _reset_nivel():
    global _obj_p1,_obj_p2,_anim_obj,_cooldown_p1,_cooldown_p2
    global _brillo,_mostrando_intro,_fase_ronda,_fase_timer
    _reset_posiciones()
    state.nivel_score_p1=0; state.nivel_score_p2=0
    state.nivel_completado=False; state.nivel_ganador=0
    state.mostrar_resultado=False; state.resultado_timer=0
    state.hud_fb_p1=""; state.hud_fb_timer_p1=0
    state.hud_fb_p2=""; state.hud_fb_timer_p2=0
    _anim_obj={o["id"]:0.0 for o in _INSTRUMENTOS}
    _brillo={o["id"]:0.0 for o in _INSTRUMENTOS}
    _cooldown_p1=_cooldown_p2=0
    _mostrando_intro=True
    _nueva_ronda()


def _nueva_ronda():
    """Elige nuevos objetivos independientes para J1 y J2 y arranca la fase de escucha."""
    global _obj_p1,_obj_p2,_fase_ronda,_fase_timer
    _obj_p1 = random.choice(_IDS_VALIDOS)
    # J2 puede tener el mismo o distinto, completamente independiente
    _obj_p2 = random.choice(_IDS_VALIDOS)
    _fase_ronda = 'escuchar_p1'
    _fase_timer = 200   # ~3.3s para escuchar J1
    _stop_all()
    # Reproducir sonido de J1 primero
    _play(_INSTRUMENTOS[_obj_p1]['archivo'])
    state.hud_msg  = "J1: Escucha y memoriza -> " + _INSTRUMENTOS[_obj_p1]['nombre'].upper()
    state.hud_msg2 = "J2: Espera tu turno..."


def _avanzar_fase():
    """Transicion entre fases escuchar_p1 -> escuchar_p2 -> jugar."""
    global _fase_ronda, _fase_timer
    if _fase_ronda == 'escuchar_p1':
        _fase_ronda = 'escuchar_p2'
        _fase_timer = 200
        _stop_all()
        _play(_INSTRUMENTOS[_obj_p2]['archivo'])
        state.hud_msg  = "J1: Recuerda -> " + _INSTRUMENTOS[_obj_p1]['nombre'].upper()
        state.hud_msg2 = "J2: Escucha y memoriza -> " + _INSTRUMENTOS[_obj_p2]['nombre'].upper()
    elif _fase_ronda == 'escuchar_p2':
        _fase_ronda = 'jugar'
        _fase_timer = 0
        _stop_all()
        state.hud_msg  = "J1: Busca -> " + _INSTRUMENTOS[_obj_p1]['nombre'].upper()
        state.hud_msg2 = "J2: Busca -> " + _INSTRUMENTOS[_obj_p2]['nombre'].upper()


def _dist2d(ax,az,bx,bz):
    return math.sqrt((ax-bx)**2+(az-bz)**2)


def _check_colisiones():
    global _cooldown_p1,_cooldown_p2,_brillo,_fase_timer
    if state.nivel_completado or _mostrando_intro: return
    if _fase_ronda != 'jugar': return

    # Actualizar brillo por proximidad para ambos jugadores
    for obj in _INSTRUMENTOS:
        d1 = _dist2d(state.p1_x,state.p1_z,obj["x"],obj["z"])
        d2 = _dist2d(state.p2_x,state.p2_z,obj["x"],obj["z"])
        dist_min = min(d1, d2)
        if dist_min < _RADIO_PROX:
            _brillo[obj["id"]] = max(_brillo[obj["id"]],
                                      1.0 - dist_min/_RADIO_PROX)
        else:
            _brillo[obj["id"]] = max(0.0, _brillo[obj["id"]] - 0.03)

    # J1
    if _cooldown_p1 > 0:
        _cooldown_p1 -= 1
    else:
        for obj in _INSTRUMENTOS:
            if _dist2d(state.p1_x,state.p1_z,obj["x"],obj["z"]) < (_RADIO_OBJ+_RADIO_JUG):
                # Reproducir sonido del objeto tocado
                _play(obj["archivo"], 0.9)
                if obj["id"] == _obj_p1:
                    state.nivel_score_p1=min(state.nivel_score_p1+2, state.META_PUNTOS)
                    state.hud_fb_p1="Correcto! +2"; state.hud_fb_timer_p1=90
                    _anim_obj[obj["id"]]=1.0
                else:
                    state.nivel_score_p1=max(0,state.nivel_score_p1-1)
                    state.hud_fb_p1="Eso no suena igual! -1"; state.hud_fb_timer_p1=80
                _cooldown_p1=120
                _check_meta()
                # Nueva ronda solo si ninguno ha ganado
                if not state.nivel_completado:
                    _nueva_ronda()
                break

    # J2
    if _cooldown_p2 > 0:
        _cooldown_p2 -= 1
    else:
        for obj in _INSTRUMENTOS:
            if _dist2d(state.p2_x,state.p2_z,obj["x"],obj["z"]) < (_RADIO_OBJ+_RADIO_JUG):
                _play(obj["archivo"], 0.9)
                if obj["id"] == _obj_p2:
                    state.nivel_score_p2=min(state.nivel_score_p2+2, state.META_PUNTOS)
                    state.hud_fb_p2="Correcto! +2"; state.hud_fb_timer_p2=90
                    _anim_obj[obj["id"]]=1.0
                else:
                    state.nivel_score_p2=max(0,state.nivel_score_p2-1)
                    state.hud_fb_p2="Eso no suena igual! -1"; state.hud_fb_timer_p2=80
                _cooldown_p2=120
                _check_meta()
                if not state.nivel_completado:
                    _nueva_ronda()
                break


def _check_meta():
    if state.nivel_completado: return
    if state.nivel_score_p1>=state.META_PUNTOS: _terminar(1)
    elif state.nivel_score_p2>=state.META_PUNTOS: _terminar(2)

def _terminar(ganador):
    _stop_all()
    state.nivel_completado=True; state.nivel_ganador=ganador
    state.mostrar_resultado=True; state.resultado_timer=220
    state.score_p1+=state.nivel_score_p1
    state.score_p2+=state.nivel_score_p2


# -- Formas de los instrumentos en OpenGL -------------------------
def _draw_instrumento(obj):
    """Dibuja una representacion simple del instrumento."""
    r,g,b = obj["color"]
    glDisable(GL_LIGHTING)

    b2 = _brillo.get(obj["id"], 0.0)
    glColor3f(min(r+b2*0.4,1), min(g+b2*0.4,1), min(b+b2*0.4,1))

    q = gluNewQuadric()
    oid = obj["id"]

    if oid == 0:   # guitarra: cuerpo ovalado + cuello
        glPushMatrix(); glTranslatef(0,0.8,0)
        glScalef(0.7,1.0,0.4); gluSphere(q,0.8,16,16)
        glPopMatrix()
        glColor3f(min(r+0.2+b2*0.4,1),min(g+0.1+b2*0.4,1),min(b+b2*0.4,1))
        glPushMatrix(); glTranslatef(0,1.8,0)
        gluCylinder(q,0.12,0.08,1.2,8,2)
        glPopMatrix()

    elif oid == 1:  # piano: paralelepipedo ancho
        s=1.0; h=0.5
        glBegin(GL_QUADS)
        faces = [
            [(-s,h,0.4),(s,h,0.4),(s,h,-0.4),(-s,h,-0.4)],
            [(-s,0,-0.4),(s,0,-0.4),(s,0,0.4),(-s,0,0.4)],
            [(-s,0,0.4),(s,0,0.4),(s,h,0.4),(-s,h,0.4)],
            [(s,0,-0.4),(-s,0,-0.4),(-s,h,-0.4),(s,h,-0.4)],
            [(-s,0,-0.4),(-s,0,0.4),(-s,h,0.4),(-s,h,-0.4)],
            [(s,0,0.4),(s,0,-0.4),(s,h,-0.4),(s,h,0.4)],
        ]
        for f in faces:
            for v in f: glVertex3fv(v)
        glEnd()
        # Teclas blancas
        glColor3f(0.95,0.95,0.95)
        for i in range(7):
            x0=-0.85+i*0.25
            glBegin(GL_QUADS)
            glVertex3f(x0,h+0.01,0.38); glVertex3f(x0+0.20,h+0.01,0.38)
            glVertex3f(x0+0.20,h+0.01,-0.05); glVertex3f(x0,h+0.01,-0.05)
            glEnd()

    elif oid == 2:  # trompeta: tubo curvo simplificado
        glPushMatrix(); glRotatef(-30,1,0,0)
        gluCylinder(q,0.12,0.12,1.5,10,3)
        glPopMatrix()
        glPushMatrix(); glTranslatef(0,1.2,0); glRotatef(60,1,0,0)
        gluCylinder(q,0.12,0.35,0.6,12,2)
        glPopMatrix()
        # Pistones
        for px in (-0.3,0,0.3):
            glPushMatrix(); glTranslatef(px,0.5,0.12)
            gluCylinder(q,0.08,0.08,0.3,8,1); glPopMatrix()

    elif oid == 3:  # violin: cuerpo con cintura
        glPushMatrix(); glTranslatef(0,0.5,0)
        glScalef(0.5,1.1,0.25); gluSphere(q,0.85,16,16)
        glPopMatrix()
        # Cuello
        glColor3f(min(r+0.15,1),min(g+0.08,1),b)
        glPushMatrix(); glTranslatef(0,1.65,0)
        gluCylinder(q,0.07,0.05,0.9,8,2)
        glPopMatrix()
        # Clavijero
        glPushMatrix(); glTranslatef(0,2.55,0)
        gluSphere(q,0.12,8,8); glPopMatrix()

    elif oid == 4:  # flauta: tubo horizontal largo
        glPushMatrix(); glRotatef(90,0,1,0); glTranslatef(0,0.8,-1.2)
        gluCylinder(q,0.08,0.08,2.4,10,2)
        glPushMatrix(); glRotatef(180,1,0,0)
        gluDisk(q,0,0.08,10,1); glPopMatrix()
        glPushMatrix(); glTranslatef(0,0,2.4)
        gluDisk(q,0,0.08,10,1); glPopMatrix()
        glPopMatrix()
        # Agujeros
        glColor3f(0,0,0)
        for hz in (-0.3,0,0.3,0.6):
            glPushMatrix(); glTranslatef(-0.09,0.8+hz,0)
            gluSphere(q,0.04,6,6); glPopMatrix()

    elif oid == 5:  # bateria: bombo + platillo
        glPushMatrix()
        gluCylinder(q,0.8,0.8,0.5,16,2)
        glPushMatrix(); glRotatef(180,1,0,0); gluDisk(q,0,0.8,16,1); glPopMatrix()
        glPushMatrix(); glTranslatef(0,0,0.5); gluDisk(q,0,0.8,16,1); glPopMatrix()
        glPopMatrix()
        # Platillo
        glColor3f(0.85,0.75,0.15)
        glPushMatrix(); glTranslatef(0.6,1.4,0); glScalef(1,0.08,1)
        gluSphere(q,0.55,12,6); glPopMatrix()

    else:   # distractores: esfera con signo de interrogacion (esfera con color)
        glPushMatrix(); glTranslatef(0,0.8,0)
        gluSphere(q,0.75,14,14)
        glPopMatrix()
        # Anillo decorativo
        glColor3f(1,1,1)
        glPushMatrix(); glTranslatef(0,0.8,0); glScalef(1,0.2,1)
        gluSphere(q,0.85,14,6); glPopMatrix()

    gluDeleteQuadric(q)
    glEnable(GL_LIGHTING)

    # Aristas negras para formas angulares (piano)
    if obj["id"] == 1:
        glLineWidth(1.5); glColor3f(0,0,0)
        glBegin(GL_LINE_LOOP)
        s=1.0; h=0.5
        glVertex3f(-s,h,0.4); glVertex3f(s,h,0.4)
        glVertex3f(s,h,-0.4); glVertex3f(-s,h,-0.4)
        glEnd()
        glLineWidth(1.0)


def _draw_etiqueta(obj):
    """Dibuja el nombre del instrumento flotando encima."""
    from OpenGL.GLUT import (GLUT_BITMAP_HELVETICA_12, glutBitmapCharacter,
                              glutGet, GLUT_WINDOW_WIDTH, GLUT_WINDOW_HEIGHT)
    # Solo mostrar nombre si es fase jugar
    if _fase_ronda != 'jugar': return
    lbl = obj["nombre"].upper() if obj["id"]<6 else "???"
    glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST)
    glColor3f(1.0,0.95,0.60)
    # Posicion 3D → texto encima del objeto (aproximado)
    glRasterPos3f(obj["x"]-0.3, 2.6, obj["z"])
    for c in lbl: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)


# -- Escenario ----------------------------------------------------
def _draw_floor():
    glDisable(GL_LIGHTING)
    glColor3f(0.10,0.06,0.18)
    glBegin(GL_QUADS)
    glVertex3f(-16,-0.01, 16); glVertex3f(16,-0.01, 16)
    glVertex3f(16,-0.01,-16); glVertex3f(-16,-0.01,-16)
    glEnd()
    glColor3f(0.20,0.12,0.32); glLineWidth(0.5)
    glBegin(GL_LINES)
    for i in range(-16,17,3):
        glVertex3f(i,0, 16); glVertex3f(i,0,-16)
        glVertex3f(-16,0,i); glVertex3f(16,0,i)
    glEnd(); glLineWidth(1.0)
    glEnable(GL_LIGHTING)


# -- HUD nivel 3 --------------------------------------------------
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
    def panel(x,y,pw,ph,r,g,b,a=0.75):
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(r,g,b,a)
        glBegin(GL_QUADS)
        glVertex2f(x,y); glVertex2f(x+pw,y)
        glVertex2f(x+pw,y+ph); glVertex2f(x,y+ph)
        glEnd(); glDisable(GL_BLEND)

    # -- Intro --
    if _mostrando_intro:
        panel(w//2-310,h//2-175,620,350,0,0,0,0.90)
        txt(w//2-190,h//2+145,"NIVEL 3 - Salon de los Instrumentos",
            GLUT_BITMAP_HELVETICA_18,(1.0,0.85,0.20))
        lineas = [
            ("OBJETIVO:", GLUT_BITMAP_HELVETICA_18,(0.95,0.90,0.40)),
            ("Escucha con atencion el instrumento que suena.", GLUT_BITMAP_HELVETICA_12,(0.90,0.90,0.90)),
            ("Luego busca ese instrumento en el mapa y tocalo.", GLUT_BITMAP_HELVETICA_12,(0.90,0.90,0.90)),
            ("Al acercarte a un objeto, lo escucharas de nuevo.", GLUT_BITMAP_HELVETICA_12,(0.75,0.75,0.75)),
            ("Cuidado con los objetos ??? que son distractores!", GLUT_BITMAP_HELVETICA_12,(1.00,0.50,0.50)),
            ("", None, None),
            ("+2 puntos por el instrumento correcto.", GLUT_BITMAP_HELVETICA_12,(0.40,1.00,0.40)),
            ("-1 punto si tocas el incorrecto.", GLUT_BITMAP_HELVETICA_12,(1.00,0.45,0.45)),
            ("Meta: 20 puntos.", GLUT_BITMAP_HELVETICA_12,(0.90,0.90,0.90)),
            ("", None, None),
            ("CONTROLES:", GLUT_BITMAP_HELVETICA_18,(0.95,0.90,0.40)),
            ("J1 (ROJO):  W/A/S/D", GLUT_BITMAP_HELVETICA_12,(1.00,0.65,0.65)),
            ("J2 (AZUL):  Flechas", GLUT_BITMAP_HELVETICA_12,(0.65,0.75,1.00)),
            ("Total acumulado - J1: "+str(state.score_p1)+"   J2: "+str(state.score_p2),
             GLUT_BITMAP_HELVETICA_12,(0.70,0.70,0.70)),
        ]
        base_y = h//2+105
        for lbl,font,col in lineas:
            if font: txt(w//2-265,base_y,lbl,font,col)
            base_y -= 22
        txt(w//2-195,h//2-185,"Presiona CUALQUIER TECLA para empezar",
            GLUT_BITMAP_HELVETICA_12,(0.55,0.55,0.55))
        glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW);  glPopMatrix()
        return

    # -- Resultado final --
    if state.mostrar_resultado:
        panel(w//2-300,h//2-130,600,260,0,0,0,0.88)
        txt(w//2-210,h//2+90,"NIVEL 3 COMPLETADO!",
            GLUT_BITMAP_HELVETICA_18,(0.95,0.85,0.20))
        txt(w//2-205,h//2+60,
            "J1: "+str(state.nivel_score_p1)+" pts     J2: "+str(state.nivel_score_p2)+" pts",
            GLUT_BITMAP_HELVETICA_18,(0.90,0.90,1.00))
        g_str="JUGADOR "+str(state.nivel_ganador)+" llego primero!"
        col=(0.90,0.20,0.20) if state.nivel_ganador==1 else (0.20,0.40,0.95)
        txt(w//2-160,h//2+25,g_str,GLUT_BITMAP_HELVETICA_18,col)
        txt(w//2-215,h//2-10,
            "Total acumulado - J1: "+str(state.score_p1)+"   J2: "+str(state.score_p2),
            GLUT_BITMAP_HELVETICA_12,(0.80,0.80,0.80))
        txt(w//2-170,h//2-40,"Fin del juego. Volviendo al lobby...",
            GLUT_BITMAP_HELVETICA_12,(0.55,0.90,0.55))
        # Marcador total
        if state.score_p1 > state.score_p2:
            ganador_txt="Ganador total: JUGADOR 1!"
            gcol=(0.90,0.20,0.20)
        elif state.score_p2 > state.score_p1:
            ganador_txt="Ganador total: JUGADOR 2!"
            gcol=(0.20,0.40,0.95)
        else:
            ganador_txt="Empate total!"
            gcol=(0.90,0.85,0.20)
        txt(w//2-160,h//2-75,ganador_txt,GLUT_BITMAP_HELVETICA_18,gcol)
        glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW);  glPopMatrix()
        return

    # -- HUD normal de juego --
    panel(0,h-52,w,52,0,0,0,0.60)
    txt(10,h-22,"NIVEL 3 - Salon de los Instrumentos",
        GLUT_BITMAP_HELVETICA_18,(1.0,0.85,0.20))
    txt(w-230,h-22,"J1: "+str(state.nivel_score_p1)+"/20   J2: "+str(state.nivel_score_p2)+"/20",
        GLUT_BITMAP_HELVETICA_18,(0.90,0.90,1.00))
    txt(w//2-200,h-44,"Total: J1="+str(state.score_p1)+"  J2="+str(state.score_p2),
        GLUT_BITMAP_HELVETICA_12,(0.65,0.65,0.65))

    # Fase escuchar: banner grande con el instrumento
    if _fase_ronda in ('escuchar_p1','escuchar_p2'):
        who = "JUGADOR 1" if _fase_ronda=='escuchar_p1' else "JUGADOR 2"
        instr = _INSTRUMENTOS[_obj_p1 if _fase_ronda=='escuchar_p1' else _obj_p2]['nombre'].upper()
        wcol = (1.0,0.55,0.55) if _fase_ronda=='escuchar_p1' else (0.55,0.75,1.0)
        panel(w//2-260,h//2-60,520,120,0,0,0,0.88)
        txt(w//2-240,h//2+28,who+" escucha tu instrumento:",
            GLUT_BITMAP_HELVETICA_18,wcol)
        txt(w//2-170,h//2-5,">>> "+instr+" <<<",
            GLUT_BITMAP_HELVETICA_18,(1.0,0.95,0.40))
        barra = int(200 * _fase_timer / 200)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.3,0.3,0.3,0.7)
        glBegin(GL_QUADS)
        glVertex2f(w//2-200,h//2-45); glVertex2f(w//2+200,h//2-45)
        glVertex2f(w//2+200,h//2-30); glVertex2f(w//2-200,h//2-30)
        glEnd()
        glColor4f(0.40,0.95,0.40,0.85)
        glBegin(GL_QUADS)
        glVertex2f(w//2-200,h//2-45); glVertex2f(w//2-200+barra,h//2-45)
        glVertex2f(w//2-200+barra,h//2-30); glVertex2f(w//2-200,h//2-30)
        glEnd(); glDisable(GL_BLEND)
    else:
        # Fase jugar: instrucciones por jugador
        panel(0,h-92,330,38,0.50,0.05,0.05,0.75)
        txt(8,h-72,state.hud_msg,GLUT_BITMAP_HELVETICA_18,(1.0,0.70,0.70))
        panel(w-330,h-92,330,38,0.05,0.10,0.55,0.75)
        txt(w-325,h-72,state.hud_msg2,GLUT_BITMAP_HELVETICA_18,(0.70,0.80,1.00))

    # Feedbacks
    if state.hud_fb_p1:
        col=(0.20,1.0,0.30) if "orrecto" in state.hud_fb_p1 else (1.0,0.35,0.35)
        txt(20,h//2,state.hud_fb_p1,GLUT_BITMAP_HELVETICA_18,col)
    if state.hud_fb_p2:
        col=(0.20,1.0,0.30) if "orrecto" in state.hud_fb_p2 else (1.0,0.35,0.35)
        txt(w-270,h//2,state.hud_fb_p2,GLUT_BITMAP_HELVETICA_18,col)

    # Barras inferiores
    panel(0,0,200,36,0.50,0.05,0.05,0.70)
    panel(w-200,0,200,36,0.05,0.10,0.55,0.70)
    txt(8,14,"J1  WASD - mover",GLUT_BITMAP_HELVETICA_12,(1.0,0.75,0.75))
    txt(w-195,14,"J2  Flechas - mover",GLUT_BITMAP_HELVETICA_12,(0.75,0.85,1.0))
    txt(w//2-140,14,"ESC: confirmar salida",GLUT_BITMAP_HELVETICA_12,(0.55,0.55,0.55))

    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()


# -- API publica --------------------------------------------------
def init():
    _init_audio()
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING); glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL); glColorMaterial(GL_FRONT,GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    glLightfv(GL_LIGHT0,GL_POSITION,[0.0,8.0,4.0,0.0])
    glLightfv(GL_LIGHT0,GL_AMBIENT,[0.12,0.08,0.22,1.0])
    glLightfv(GL_LIGHT0,GL_DIFFUSE,[0.55,0.50,0.85,1.0])
    _reset_nivel()

def reset():
    _reset_nivel()

def display(draw_p1,draw_p2):
    if _anim_obj and max(_anim_obj.values())>0 and not state.mostrar_resultado:
        t2=max(_anim_obj.values())
        glClearColor(0.05+0.12*t2,0.02,0.12+0.18*t2,1.0)
    else:
        glClearColor(0.05,0.02,0.12,1.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    camera.apply(state.WIN_W,state.WIN_H)
    _draw_floor()
    for obj in _INSTRUMENTOS:
        glPushMatrix(); glTranslatef(obj["x"],0.0,obj["z"])
        spin=_anim_obj.get(obj["id"],0.0)
        if spin>0: glRotatef(spin*360,0,1,0)
        _draw_instrumento(obj)
        glPopMatrix()
        _draw_etiqueta(obj)
    if not _mostrando_intro and not state.mostrar_resultado:
        players.draw_players(draw_p1,draw_p2)
    _draw_hud()
    glutSwapBuffers()

def update(_v):
    global _fase_timer,_mostrando_intro
    if _mostrando_intro: return
    if state.mostrar_resultado:
        if state.resultado_timer>0: state.resultado_timer-=1
        return
    if _fase_ronda in ('escuchar_p1','escuchar_p2'):
        if _fase_timer>0: _fase_timer-=1
        else: _avanzar_fase()
    else:
        players.update()
        _check_colisiones()
    for oid in _anim_obj:
        if _anim_obj[oid]>0: _anim_obj[oid]=max(0.0,_anim_obj[oid]-0.02)
    if state.hud_fb_timer_p1>0:
        state.hud_fb_timer_p1-=1
        if state.hud_fb_timer_p1==0: state.hud_fb_p1=""
    if state.hud_fb_timer_p2>0:
        state.hud_fb_timer_p2-=1
        if state.hud_fb_timer_p2==0: state.hud_fb_p2=""

def keyboard(key,_x,_y):
    global _mostrando_intro
    if _mostrando_intro: _mostrando_intro=False; return
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
    if _mostrando_intro: _mostrando_intro=False; return
    if key==GLUT_KEY_UP:    state.k_up=True
    elif key==GLUT_KEY_DOWN:  state.k_down=True
    elif key==GLUT_KEY_LEFT:  state.k_left=True
    elif key==GLUT_KEY_RIGHT: state.k_right=True
def special_keys_up(key,_x,_y):
    if key==GLUT_KEY_UP:    state.k_up=False
    elif key==GLUT_KEY_DOWN:  state.k_down=False
    elif key==GLUT_KEY_LEFT:  state.k_left=False
    elif key==GLUT_KEY_RIGHT: state.k_right=False
