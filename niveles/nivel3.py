# ============================================================
# niveles/nivel3.py  — El Salon de los Instrumentos
# ------------------------------------------------------------
# OBJETIVO PEDAGOGICO: Memoria auditiva de corto plazo.
# A diferencia de los niveles anteriores, la pista NO es visual:
# el juego reproduce un instrumento y el nino debe recordarlo
# mientras navega el mapa.
#
# MECANICA "ESCUCHA Y MEMORIZA":
#   1. Se reproduce UN sonido para AMBOS jugadores.
#   2. Los jugadores recorren el mapa buscando el instrumento.
#   3. Al acercarse a un objeto (radio < 3.5 uds) lo escuchan:
#      - Volumen 1.0 si es el correcto.
#      - Volumen 0.25 si es incorrecto (pista sonora atenuada).
#   4. Al tocar el correcto: +2 pts, pausa de 3.5s, nuevo sonido.
#   5. Al tocar incorrecto: -1 pts, instruccion NO cambia.
#      (El error no revela la respuesta; el nino debe seguir buscando)
#
# DISTRACTORES: 4 objetos con sonidos "graciosos" (resorte,
# burbuja, boing, silbato) que nunca son el objetivo correcto.
# Muestran "???" como nombre para mantener el misterio.
#
# INTERVALO DE SONIDO: _INTERVALO_FRAMES = 150 (~2.5s).
# Si _frame - _last_play < 150, no se reproduce nada nuevo.
# Evita que multiples colisiones simultane superponganan audio.
#
# PAUSA ENTRE RONDAS: _pausa_ronda = 210 (~3.5s).
# Cuando alguien acierta, se pausa el movimiento para que
# el sonido de acierto termine antes del nuevo instrumento.
# ============================================================
# niveles/nivel3.py  — El Salon de los Instrumentos
# Mecanica "Escucha y Memoriza" simplificada:
#   1. Pantalla de instrucciones -> cualquier tecla la cierra.
#   2. Se reproduce UN sonido SIMULTANEO para ambos jugadores.
#   3. Los jugadores buscan el instrumento en el mapa.
#   4. Al acercarse a un objeto, ese objeto reproduce su sonido
#      (a volumen completo si es el correcto, reducido si no).
#   5. Intervalo de 2.5s entre sonidos de proximidad para evitar superposicion.
#   6. Si toca incorrecto: -1 pt, pero NO cambia la instruccion.
#   7. Si toca correcto: +2 pts -> nueva ronda con nuevo instrumento.
#   8. Meta 20 pts. Puntaje acumulado al global.

import math, random, os
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *
from niveles     import state, camera, players

# -- Audio --------------------------------------------------------
_AUDIO = False
_sonidos_cache = {}
_last_play_p1 = 0   # frame en que J1 ultimo reprodujo sonido
_last_play_p2 = 0
_frame = 0
_INTERVALO_FRAMES = 150  # ~2.5s a 60fps

def _init_audio():
    global _AUDIO
    try:
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        _AUDIO = True
    except Exception as e:
        print(f"[nivel3] audio no disponible: {e}")

def _cargar(nombre):
    if not _AUDIO: return None
    if nombre in _sonidos_cache: return _sonidos_cache[nombre]
    import pygame
    base = os.path.join(os.path.dirname(__file__), 'sounds', nombre)
    try:
        s = pygame.mixer.Sound(base)
        _sonidos_cache[nombre] = s
        return s
    except Exception as e:
        print(f"[nivel3] no se cargó {nombre}: {e}")
        return None

def _play(nombre, volumen=1.0):
    s = _cargar(nombre)
    if s:
        s.set_volume(min(1.0, max(0.0, volumen)))
        s.play()

def _stop_all():
    if _AUDIO:
        import pygame; pygame.mixer.stop()

# -- Instrumentos y distractores ----------------------------------
_INSTRUMENTOS = [
    {"id":0,"nombre":"guitarra", "archivo":"guitarra.wav",
     "color":(0.65,0.35,0.10),"x":-9.0,"z":-7.0,"es_instrumento":True},
    {"id":1,"nombre":"piano",    "archivo":"piano.wav",
     "color":(0.20,0.20,0.20),"x": 9.0,"z":-7.0,"es_instrumento":True},
    {"id":2,"nombre":"trompeta", "archivo":"trompeta.wav",
     "color":(0.90,0.75,0.10),"x":-9.0,"z": 7.0,"es_instrumento":True},
    {"id":3,"nombre":"violin",   "archivo":"violin.wav",
     "color":(0.60,0.20,0.05),"x": 9.0,"z": 7.0,"es_instrumento":True},
    {"id":4,"nombre":"flauta",   "archivo":"flauta.wav",
     "color":(0.70,0.90,0.95),"x": 0.0,"z":-10.0,"es_instrumento":True},
    {"id":5,"nombre":"bateria",  "archivo":"bateria.wav",
     "color":(0.35,0.35,0.40),"x": 0.0,"z": 10.0,"es_instrumento":True},
    {"id":6,"nombre":"???",      "archivo":"distractor1_resorte.wav",
     "color":(0.90,0.20,0.70),"x":-5.0,"z": 0.0,"es_instrumento":False},
    {"id":7,"nombre":"???",      "archivo":"distractor2_burbuja.wav",
     "color":(0.20,0.80,0.90),"x": 5.0,"z": 0.0,"es_instrumento":False},
    {"id":8,"nombre":"???",      "archivo":"distractor3_boing.wav",
     "color":(0.40,0.90,0.20),"x":-6.0,"z": 4.0,"es_instrumento":False},
    {"id":9,"nombre":"???",      "archivo":"distractor4_silbato.wav",
     "color":(0.95,0.50,0.10),"x": 6.0,"z":-4.0,"es_instrumento":False},
]
_IDS_VALIDOS = [0,1,2,3,4,5]
_RADIO_OBJ=1.0; _RADIO_PROX=3.5; _RADIO_JUG=0.5

# -- Estado -------------------------------------------------------
_obj_objetivo = 0       # mismo objetivo para ambos jugadores
_anim_obj = {}
_brillo   = {}
_cooldown_p1 = 0
_cooldown_p2 = 0
_mostrando_intro = True
_pausa_ronda = 0      # frames de pausa entre rondas (3s = 180)

def _reset_posiciones():
    # Posiciones alejadas de todos los objetos
    state.p1_x= 0.0; state.p1_z= 0.0; state.p1_rot=  0.0
    state.p2_x= 0.0; state.p2_z= 2.5; state.p2_rot=180.0
    state.p1_walking=state.p2_walking=False
    state.p1_anim=state.p2_anim=0.0
    state.k_w=state.k_s=state.k_a=state.k_d=False
    state.k_up=state.k_down=state.k_left=state.k_right=False

def _reset_nivel():
    global _obj_objetivo,_anim_obj,_brillo,_cooldown_p1,_cooldown_p2
    global _mostrando_intro,_frame,_last_play_p1,_last_play_p2
    _reset_posiciones()
    state.nivel_score_p1=0; state.nivel_score_p2=0
    state.nivel_completado=False; state.nivel_ganador=0
    state.mostrar_resultado=False; state.resultado_timer=0
    state.hud_fb_p1=""; state.hud_fb_timer_p1=0
    state.hud_fb_p2=""; state.hud_fb_timer_p2=0
    _anim_obj={o["id"]:0.0 for o in _INSTRUMENTOS}
    _brillo   ={o["id"]:0.0 for o in _INSTRUMENTOS}
    _cooldown_p1=_cooldown_p2=0
    _frame=0; _last_play_p1=0; _last_play_p2=0
    _pausa_ronda=0
    _mostrando_intro=True
    # NO reproducir sonido aqui, se reproduce al cerrar la intro

def _nueva_ronda(con_pausa=True):
    """Elige nuevo instrumento objetivo. Si con_pausa=True espera 3s antes de reproducir."""
    global _obj_objetivo, _pausa_ronda
    _obj_objetivo = random.choice(_IDS_VALIDOS)
    nombre = _INSTRUMENTOS[_obj_objetivo]['nombre'].upper()
    state.hud_msg  = "J1: Espera..."
    state.hud_msg2 = "J2: Espera..."
    # NO llamar _stop_all() aqui: el sonido del acierto debe terminar
    if con_pausa:
        _pausa_ronda = 210   # 3.5 segundos; animacion corre durante la pausa
    else:
        _pausa_ronda = 0
        _play(_INSTRUMENTOS[_obj_objetivo]['archivo'])

def _dist2d(ax,az,bx,bz):
    return math.sqrt((ax-bx)**2+(az-bz)**2)

def _check_colisiones():
    global _cooldown_p1,_cooldown_p2,_last_play_p1,_last_play_p2,_brillo
    if state.nivel_completado or _mostrando_intro: return

    # Actualizar brillo por proximidad
    for obj in _INSTRUMENTOS:
        d1=_dist2d(state.p1_x,state.p1_z,obj["x"],obj["z"])
        d2=_dist2d(state.p2_x,state.p2_z,obj["x"],obj["z"])
        dm=min(d1,d2)
        _brillo[obj["id"]] = max(0.0, (1.0-dm/_RADIO_PROX)) if dm<_RADIO_PROX else max(0.0,_brillo[obj["id"]]-0.04)

    # J1
    if _cooldown_p1>0: _cooldown_p1-=1
    else:
        for obj in _INSTRUMENTOS:
            if _dist2d(state.p1_x,state.p1_z,obj["x"],obj["z"])<(_RADIO_OBJ+_RADIO_JUG):
                # Reproducir sonido del objeto con intervalo
                if _frame - _last_play_p1 >= _INTERVALO_FRAMES:
                    vol = 1.0 if obj["id"]==_obj_objetivo else 0.25
                    _play(obj["archivo"], vol)
                    _last_play_p1 = _frame
                if obj["id"]==_obj_objetivo:
                    state.nivel_score_p1=min(state.nivel_score_p1+2,state.META_PUNTOS)
                    state.hud_fb_p1="Correcto! +2"; state.hud_fb_timer_p1=90
                    _anim_obj[obj["id"]]=1.0
                    # Reproducir el sonido correcto ANTES de iniciar nueva ronda
                    _play(obj["archivo"], 1.0)
                    _last_play_p1 = _frame
                    _cooldown_p1=90
                    _check_meta()
                    if not state.nivel_completado: _nueva_ronda()
                else:
                    state.nivel_score_p1=max(0,state.nivel_score_p1-1)
                    state.hud_fb_p1="No es ese! -1"; state.hud_fb_timer_p1=80
                    _cooldown_p1=_INTERVALO_FRAMES
                    _check_meta()
                break

    # J2
    if _cooldown_p2>0: _cooldown_p2-=1
    else:
        for obj in _INSTRUMENTOS:
            if _dist2d(state.p2_x,state.p2_z,obj["x"],obj["z"])<(_RADIO_OBJ+_RADIO_JUG):
                if _frame - _last_play_p2 >= _INTERVALO_FRAMES:
                    vol = 1.0 if obj["id"]==_obj_objetivo else 0.25
                    _play(obj["archivo"], vol)
                    _last_play_p2 = _frame
                if obj["id"]==_obj_objetivo:
                    state.nivel_score_p2=min(state.nivel_score_p2+2,state.META_PUNTOS)
                    state.hud_fb_p2="Correcto! +2"; state.hud_fb_timer_p2=90
                    _anim_obj[obj["id"]]=1.0
                    _play(obj["archivo"], 1.0)
                    _last_play_p2 = _frame
                    _cooldown_p2=90
                    _check_meta()
                    if not state.nivel_completado: _nueva_ronda()
                else:
                    state.nivel_score_p2=max(0,state.nivel_score_p2-1)
                    state.hud_fb_p2="No es ese! -1"; state.hud_fb_timer_p2=80
                    _cooldown_p2=_INTERVALO_FRAMES
                    _check_meta()
                break

def _check_meta():
    if state.nivel_completado: return
    if state.nivel_score_p1>=state.META_PUNTOS: _terminar(1)
    elif state.nivel_score_p2>=state.META_PUNTOS: _terminar(2)

def _terminar(ganador):
    _stop_all()
    state.nivel_completado=True; state.nivel_ganador=ganador
    state.mostrar_resultado=True; state.resultado_timer=280
    state.score_p1+=state.nivel_score_p1; state.score_p2+=state.nivel_score_p2

# -- Dibujo de instrumentos ---------------------------------------
def _draw_instrumento(obj):
    r,g,b=obj["color"]
    b2=_brillo.get(obj["id"],0.0)
    glDisable(GL_LIGHTING)
    glColor3f(min(r+b2*0.4,1),min(g+b2*0.4,1),min(b+b2*0.4,1))
    q=gluNewQuadric(); oid=obj["id"]
    if oid==0:   # guitarra
        glPushMatrix(); glTranslatef(0,0.8,0); glScalef(0.7,1.0,0.4); gluSphere(q,0.8,16,16); glPopMatrix()
        glColor3f(min(r+0.2,1),min(g+0.1,1),b)
        glPushMatrix(); glTranslatef(0,1.8,0); gluCylinder(q,0.12,0.08,1.2,8,2); glPopMatrix()
    elif oid==1:  # piano
        s=1.0; hh=0.5
        faces=[
            [(-s,hh,0.4),(s,hh,0.4),(s,hh,-0.4),(-s,hh,-0.4)],
            [(-s,0,-0.4),(s,0,-0.4),(s,0,0.4),(-s,0,0.4)],
            [(-s,0,0.4),(s,0,0.4),(s,hh,0.4),(-s,hh,0.4)],
            [(s,0,-0.4),(-s,0,-0.4),(-s,hh,-0.4),(s,hh,-0.4)],
            [(-s,0,-0.4),(-s,0,0.4),(-s,hh,0.4),(-s,hh,-0.4)],
            [(s,0,0.4),(s,0,-0.4),(s,hh,-0.4),(s,hh,0.4)],
        ]
        glBegin(GL_QUADS)
        for f in faces:
            for v in f: glVertex3fv(v)
        glEnd()
        glColor3f(0.95,0.95,0.95)
        for i in range(7):
            x0=-0.85+i*0.25
            glBegin(GL_QUADS)
            glVertex3f(x0,hh+0.01,0.38); glVertex3f(x0+0.20,hh+0.01,0.38)
            glVertex3f(x0+0.20,hh+0.01,-0.05); glVertex3f(x0,hh+0.01,-0.05)
            glEnd()
    elif oid==2:  # trompeta
        glPushMatrix(); glRotatef(-30,1,0,0); gluCylinder(q,0.12,0.12,1.5,10,3); glPopMatrix()
        glPushMatrix(); glTranslatef(0,1.2,0); glRotatef(60,1,0,0); gluCylinder(q,0.12,0.35,0.6,12,2); glPopMatrix()
        for px in (-0.3,0,0.3):
            glPushMatrix(); glTranslatef(px,0.5,0.12); gluCylinder(q,0.08,0.08,0.3,8,1); glPopMatrix()
    elif oid==3:  # violin
        glPushMatrix(); glTranslatef(0,0.5,0); glScalef(0.5,1.1,0.25); gluSphere(q,0.85,16,16); glPopMatrix()
        glColor3f(min(r+0.15,1),min(g+0.08,1),b)
        glPushMatrix(); glTranslatef(0,1.65,0); gluCylinder(q,0.07,0.05,0.9,8,2); glPopMatrix()
        glPushMatrix(); glTranslatef(0,2.55,0); gluSphere(q,0.12,8,8); glPopMatrix()
    elif oid==4:  # flauta
        glPushMatrix(); glRotatef(90,0,1,0); glTranslatef(0,0.8,-1.2)
        gluCylinder(q,0.08,0.08,2.4,10,2)
        glPushMatrix(); glRotatef(180,1,0,0); gluDisk(q,0,0.08,10,1); glPopMatrix()
        glPushMatrix(); glTranslatef(0,0,2.4); gluDisk(q,0,0.08,10,1); glPopMatrix()
        glPopMatrix()
    elif oid==5:  # bateria
        gluCylinder(q,0.8,0.8,0.5,16,2)
        glPushMatrix(); glRotatef(180,1,0,0); gluDisk(q,0,0.8,16,1); glPopMatrix()
        glPushMatrix(); glTranslatef(0,0,0.5); gluDisk(q,0,0.8,16,1); glPopMatrix()
        glColor3f(0.85,0.75,0.15)
        glPushMatrix(); glTranslatef(0.6,1.4,0); glScalef(1,0.08,1); gluSphere(q,0.55,12,6); glPopMatrix()
    else:  # distractor: esfera con anillo
        glPushMatrix(); glTranslatef(0,0.8,0); gluSphere(q,0.75,14,14); glPopMatrix()
        glColor3f(1,1,1)
        glPushMatrix(); glTranslatef(0,0.8,0); glScalef(1,0.2,1); gluSphere(q,0.85,14,6); glPopMatrix()
    gluDeleteQuadric(q); glEnable(GL_LIGHTING)

def _draw_nombre(obj):
    from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_12, glutBitmapCharacter
    lbl = obj["nombre"].upper()
    col = (1.0,0.95,0.40) if obj["id"]==_obj_objetivo else (0.75,0.75,0.75)
    glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST)
    glColor3fv(col)
    glRasterPos3f(obj["x"]-0.35, 2.8, obj["z"])
    for c in lbl: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)

def _draw_floor():
    glDisable(GL_LIGHTING)
    glColor3f(0.10,0.06,0.18)
    glBegin(GL_QUADS)
    glVertex3f(-16,-0.01,16); glVertex3f(16,-0.01,16)
    glVertex3f(16,-0.01,-16); glVertex3f(-16,-0.01,-16)
    glEnd()
    glColor3f(0.18,0.10,0.28); glLineWidth(0.5)
    glBegin(GL_LINES)
    for i in range(-16,17,3):
        glVertex3f(i,0,16); glVertex3f(i,0,-16)
        glVertex3f(-16,0,i); glVertex3f(16,0,i)
    glEnd(); glLineWidth(1.0)
    glEnable(GL_LIGHTING)

# -- HUD ----------------------------------------------------------
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
    def panel(x,y,pw,ph,r,g,b,a=0.78):
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(r,g,b,a)
        glBegin(GL_QUADS)
        glVertex2f(x,y); glVertex2f(x+pw,y); glVertex2f(x+pw,y+ph); glVertex2f(x,y+ph)
        glEnd(); glDisable(GL_BLEND)

    # -- Intro --
    if _mostrando_intro:
        panel(w//2-320,h//2-200,640,400,0,0,0,0.92)
        txt(w//2-220,h//2+175,"NIVEL 3 - Salon de los Instrumentos",
            GLUT_BITMAP_HELVETICA_18,(1.0,0.85,0.20))
        lineas=[
            ("OBJETIVO:", GLUT_BITMAP_HELVETICA_18,(0.95,0.90,0.40)),
            ("Se reproducira un instrumento musical.", GLUT_BITMAP_HELVETICA_12,(0.90,0.90,0.90)),
            ("Ambos jugadores escuchan el MISMO sonido.", GLUT_BITMAP_HELVETICA_12,(0.90,0.90,0.90)),
            ("Busca ese instrumento en el mapa y tocalo.", GLUT_BITMAP_HELVETICA_12,(0.90,0.90,0.90)),
            ("Al acercarte a un objeto lo escucharas.", GLUT_BITMAP_HELVETICA_12,(0.75,0.75,0.75)),
            ("Los ??? son distractores. No confundas!", GLUT_BITMAP_HELVETICA_12,(1.0,0.55,0.55)),
            ("", None, None),
            ("+2 puntos: instrumento correcto.", GLUT_BITMAP_HELVETICA_12,(0.40,1.00,0.40)),
            ("-1 punto: instrumento incorrecto (no cambia la pista).", GLUT_BITMAP_HELVETICA_12,(1.0,0.45,0.45)),
            ("Meta: 20 puntos.", GLUT_BITMAP_HELVETICA_12,(0.90,0.90,0.90)),
            ("", None, None),
            ("CONTROLES:", GLUT_BITMAP_HELVETICA_18,(0.95,0.90,0.40)),
            ("J1 (ROJO):  W / A / S / D", GLUT_BITMAP_HELVETICA_12,(1.00,0.65,0.65)),
            ("J2 (AZUL):  Flechas", GLUT_BITMAP_HELVETICA_12,(0.65,0.75,1.00)),
            ("Total acumulado  J1:"+str(state.score_p1)+"  J2:"+str(state.score_p2),
             GLUT_BITMAP_HELVETICA_12,(0.60,0.80,0.60)),
        ]
        base_y=h//2+130
        for lbl,font,col in lineas:
            if font: txt(w//2-290,base_y,lbl,font,col)
            base_y-=22
        panel(w//2-240,h//2-215,480,32,0.25,0.25,0.0,0.88)
        txt(w//2-215,h//2-205,
            ">>> Presiona CUALQUIER TECLA para empezar <<<",
            GLUT_BITMAP_HELVETICA_12,(1.0,0.95,0.40))
        glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW);  glPopMatrix()
        return

    # -- Pantalla felicitaciones / resultado --
    if state.mostrar_resultado:
        panel(w//2-320,h//2-150,640,300,0,0,0,0.90)
        txt(w//2-195,h//2+115,"¡NIVEL 3 COMPLETADO!",
            GLUT_BITMAP_HELVETICA_18,(0.95,0.85,0.20))
        txt(w//2-210,h//2+80,
            "J1: "+str(state.nivel_score_p1)+" pts     J2: "+str(state.nivel_score_p2)+" pts",
            GLUT_BITMAP_HELVETICA_18,(0.90,0.90,1.00))
        g_str="¡JUGADOR "+str(state.nivel_ganador)+" llego primero al nivel 3!"
        col=(0.90,0.20,0.20) if state.nivel_ganador==1 else (0.20,0.40,0.95)
        txt(w//2-200,h//2+45,g_str,GLUT_BITMAP_HELVETICA_12,col)
        txt(w//2-210,h//2+15,
            "Total acumulado - J1: "+str(state.score_p1)+"   J2: "+str(state.score_p2),
            GLUT_BITMAP_HELVETICA_12,(0.82,0.82,0.82))
        # Ganador total
        if state.score_p1>state.score_p2:
            gfin="¡¡ FELICIDADES JUGADOR 1 !! Ganaste el juego completo!"; gcol=(0.90,0.20,0.20)
        elif state.score_p2>state.score_p1:
            gfin="¡¡ FELICIDADES JUGADOR 2 !! Ganaste el juego completo!"; gcol=(0.20,0.40,0.95)
        else:
            gfin="¡¡ EMPATE TOTAL !! Los dos son increibles!"; gcol=(0.90,0.85,0.20)
        panel(w//2-290,h//2-35,580,42,0.0,0.0,0.0,0.85)
        txt(w//2-270,h//2-18,gfin,GLUT_BITMAP_HELVETICA_18,gcol)
        txt(w//2-155,h//2-65,"Volviendo al lobby...",
            GLUT_BITMAP_HELVETICA_12,(0.55,0.90,0.55))
        glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW);  glPopMatrix()
        return

    # -- HUD normal --
    panel(0,h-52,w,52,0,0,0,0.60)
    txt(10,h-22,"NIVEL 3 - Salon de los Instrumentos",
        GLUT_BITMAP_HELVETICA_18,(1.0,0.85,0.20))
    txt(w-230,h-22,"J1: "+str(state.nivel_score_p1)+"/20   J2: "+str(state.nivel_score_p2)+"/20",
        GLUT_BITMAP_HELVETICA_18,(0.90,0.90,1.00))
    txt(w//2-200,h-44,"Total: J1="+str(state.score_p1)+"  J2="+str(state.score_p2),
        GLUT_BITMAP_HELVETICA_12,(0.65,0.65,0.65))
    # Instruccion compartida centrada
    nombre_obj=_INSTRUMENTOS[_obj_objetivo]["nombre"].upper()
    panel(w//2-280,h-98,560,44,0.30,0.10,0.45,0.80)
    txt(w//2-260,h-76,"Ambos: busca la "+nombre_obj,
        GLUT_BITMAP_HELVETICA_18,(1.0,0.90,0.50))
    # Feedbacks
    if state.hud_fb_p1:
        col=(0.20,1.0,0.30) if "orrecto" in state.hud_fb_p1 else (1.0,0.35,0.35)
        txt(20,h//2,state.hud_fb_p1,GLUT_BITMAP_HELVETICA_18,col)
    if state.hud_fb_p2:
        col=(0.20,1.0,0.30) if "orrecto" in state.hud_fb_p2 else (1.0,0.35,0.35)
        txt(w-270,h//2,state.hud_fb_p2,GLUT_BITMAP_HELVETICA_18,col)
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
    # -- Iluminacion Phong: Nivel 3 (Cueva) ----------------------
    # Luz principal azul-purpura desde arriba
    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 10.0, 3.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.05, 0.03, 0.12, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.45, 0.40, 0.80, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.80, 0.70, 1.00, 1.0])
    # Luz de acento magenta desde abajo (efecto cueva magico)
    glEnable(GL_LIGHT1)
    glLightfv(GL_LIGHT1, GL_POSITION, [0.0, -2.0, 0.0, 1.0])
    glLightfv(GL_LIGHT1, GL_AMBIENT,  [0.0,  0.0,  0.0,  1.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE,  [0.18, 0.05, 0.22, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.30, 0.10, 0.40, 1.0])
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    # Especular alto para efecto cristalino en los instrumentos
    glMaterialfv(GL_FRONT, GL_SPECULAR,  [0.60, 0.55, 0.90, 1.0])
    glMaterialf (GL_FRONT, GL_SHININESS, 96.0)
    glShadeModel(GL_SMOOTH)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.04, 0.03, 0.10, 1.0])
    _reset_nivel()

def reset():
    _reset_nivel()

def display_sin_swap(draw_p1,draw_p2):
    bmax=max(_anim_obj.values()) if _anim_obj else 0
    if bmax>0 and not state.mostrar_resultado:
        glClearColor(0.05+0.12*bmax,0.02,0.12+0.18*bmax,1.0)
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
        _draw_nombre(obj)
    if not _mostrando_intro and not state.mostrar_resultado:
        players.draw_players(draw_p1,draw_p2)
    _draw_hud()

def display(draw_p1,draw_p2):
    display_sin_swap(draw_p1,draw_p2)
    glutSwapBuffers()

def update(_v):
    global _frame, _pausa_ronda
    _frame+=1
    if _mostrando_intro: return
    if state.mostrar_resultado:
        if state.resultado_timer>0: state.resultado_timer-=1
        return
    # Pausa entre rondas: contar y reproducir al llegar a 0
    if _pausa_ronda > 0:
        _pausa_ronda -= 1
        if _pausa_ronda == 0:
            _stop_all()
            _play(_INSTRUMENTOS[_obj_objetivo]['archivo'])
            nombre = _INSTRUMENTOS[_obj_objetivo]['nombre'].upper()
            state.hud_msg  = "J1: Busca -> " + nombre
            state.hud_msg2 = "J2: Busca -> " + nombre
        # Durante la pausa: animar objetos y feedback, pero NO mover ni colisionar
        for oid in _anim_obj:
            if _anim_obj[oid]>0: _anim_obj[oid]=max(0.0,_anim_obj[oid]-0.02)
        if state.hud_fb_timer_p1>0:
            state.hud_fb_timer_p1-=1
            if state.hud_fb_timer_p1==0: state.hud_fb_p1=""
        if state.hud_fb_timer_p2>0:
            state.hud_fb_timer_p2-=1
            if state.hud_fb_timer_p2==0: state.hud_fb_p2=""
        return
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
    if _mostrando_intro:
        _mostrando_intro=False
        _nueva_ronda(con_pausa=False)   # primera vez: sin pausa
        return
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
        _mostrando_intro=False; _nueva_ronda(con_pausa=False); return
    if key==GLUT_KEY_UP:    state.k_up=True
    elif key==GLUT_KEY_DOWN:  state.k_down=True
    elif key==GLUT_KEY_LEFT:  state.k_left=True
    elif key==GLUT_KEY_RIGHT: state.k_right=True
def special_keys_up(key,_x,_y):
    if key==GLUT_KEY_UP:    state.k_up=False
    elif key==GLUT_KEY_DOWN:  state.k_down=False
    elif key==GLUT_KEY_LEFT:  state.k_left=False
    elif key==GLUT_KEY_RIGHT: state.k_right=False