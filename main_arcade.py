# ============================================================
#  ARCADE SELECTOR MAESTRO  —  Lobby 3D
#  Instrucciones de navegación:
#    Flechas ← →  o  arrastrar mouse  :  cambiar personaje
#    Scroll del mouse                 :  cambiar personaje
#    ENTER o teclas 1-6              :  entrar al juego
#    ESC (en juego)                  :  volver al lobby
#    ESC (en lobby)                  :  salir
#
#  Niveles (desde el lobby, con personaje seleccionado):
#    N1 / N2 / N3                    :  entrar a cada nivel
# ============================================================
import sys
import math
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *

# ── Módulos de juego (modo interactivo completo) ─────────────
import fallguy.main        as p_fallguy
import AmongUsFinal.main   as p_amongus
import beru.main           as p_beru
import gato_3d.main        as p_gato
import MegaCaballero.main  as p_mega
import totoro.main         as p_totoro

MODULOS_PERSONAJES = [p_fallguy, p_amongus, p_beru, p_gato, p_mega, p_totoro]

# ── Módulos de niveles ────────────────────────────────────────
from niveles import nivel1, nivel2, nivel3
from niveles import state as nivel_state

MODULOS_NIVELES    = [None, nivel1, nivel2, nivel3]   # índice 1-3
_nivel_initialized = [False, False, False, False]     # [0] no se usa

# ── Módulos de dibujo directos para el lobby 3D ──────────────
from fallguy.characters       import FullGuys     as _fg
from AmongUsFinal.characters  import AmongUs      as _au
import beru.caracteres.beru                       as _beru
from gato_3d.cat_character    import cat          as _cat
from MegaCaballero.characters import MegaKknight  as _mk
from totoro.caracteres        import totoro       as _tot

# ════════════════════════════════════════════════════════════
# METADATA DE PERSONAJES
# ════════════════════════════════════════════════════════════
CHARACTERS = [
    {"label": "FallGuy",       "author": "Brenda Luz",
     "color": (0.90, 0.15, 0.15),
     "desc":  ["Inspirado en Fall Guys", "5 escenas  |  5 movimientos"]},
    {"label": "Among Us",      "author": "Eliel Figueroa",
     "color": (0.20, 0.60, 0.20),
     "desc":  ["Tripulante espacial",   "5 escenas  |  5 movimientos"]},
    {"label": "Beru",          "author": "Jose Bernardo",
     "color": (0.10, 0.45, 0.90),
     "desc":  ["Solo Leveling",         "7 escenas  |  7 movimientos"]},
    {"label": "Gato 3D",       "author": "Brenda Luz",
     "color": (0.85, 0.55, 0.10),
     "desc":  ["Gatita con flores",     "7 escenas  |  7 movimientos"]},
    {"label": "MegaCaballero", "author": "Eliel Figueroa",
     "color": (0.55, 0.10, 0.80),
     "desc":  ["Caballero con mazas",   "7 escenas  |  7 movimientos"]},
    {"label": "TotoRin",       "author": "Equipo",
     "color": (0.25, 0.65, 0.55),
     "desc":  ["Guardian del bosque",   "4 escenas  |  5 movimientos"]},
]
N = len(CHARACTERS)

# ════════════════════════════════════════════════════════════
# AJUSTES VISUALES POR PERSONAJE PARA EL LOBBY
# ════════════════════════════════════════════════════════════
# scale : escala uniforme (ajustar si se ve muy grande/pequeño).
# y_off : corrección vertical adicional (ajustar si flota o se hunde).
#
# Notas de calibración basadas en los draw internos:
#  FallGuy    → draw hace glScalef(0.4,0.4,0.4)+glTranslatef(0,0.16,0) internamente
#  AmongUs    → sin auto-escala; tamaño moderado
#  Beru       → sub-funciones manuales, offset +0.48 aplicado aquí
#  Cat        → _FEET_OFFSET=1.10 interno; draw_cat() ya pone pies en 0
#  MegaKnight → draw aplica total_y_offset (0 en reposo)
#  Totoro     → main usa glScalef(0.7) y coloca en y=5; draw_totoro desde origen
_LOBBY_CFG = [
    {"scale": 2.5,  "y_off": 0.0 },   # 0  FallGuy   (draw ya hace ×0.4 interno)
    {"scale": 1.0,  "y_off": 0.0 },   # 1  AmongUs
    {"scale": 1.6,  "y_off": 0.0 },   # 2  Beru
    {"scale": 1.1,  "y_off": 0.0 },   # 3  Gato 3D   (draw ya pone pies en 0)
    {"scale": 1.0,  "y_off": 0.55},   # 4  MegaCaballero  (levantado para compensar hundimiento)
    {"scale": 0.22, "y_off": 0.0 },   # 5  Totoro         (reducido: body radius=4-5)
]

# ════════════════════════════════════════════════════════════
# ESTADO GLOBAL
# ════════════════════════════════════════════════════════════
WIN_W, WIN_H = 960, 620
# Personaje seleccionado por cada jugador en el lobby
selected_p1  = 0   # J1
selected_p2  = 1   # J2
# Flujo de selección: 0=intro, 1=elige J1, 2=elige J2, 3=confirmar, 4=en juego
_lobby_fase  = 0
estado_juego = -1          # -1 = lobby,  0..5 = personaje activo
estado_nivel = 0           # 0 = sin nivel, 1..3 = nivel activo
_nivel_siguiente = 1       # nivel al que entrar cuando se pulse N
_initialized = [False] * N

# Animación del carrusel
SPACING       = 3.8        # distancia entre personajes (unidades mundo)
_lob_offset   = 0.0        # offset visual actual (lerpeado)
_lob_target   = 0.0        # offset objetivo = selected * SPACING
_lob_timer    = 0          # reloj para idle (frames)

# Entrada de mouse
_mouse_down   = False
_mouse_last_x = 0
_drag_accum   = 0          # píxeles arrastrados acumulados
DRAG_THRESH   = 70         # píxeles para cambiar selección


# ════════════════════════════════════════════════════════════
# FUNCIÓN DE DIBUJO DE BERU PARA EL LOBBY
# (evita la auto-traslación y la sombra en coordenadas absolutas)
# ════════════════════════════════════════════════════════════
def _draw_beru_lobby():
    glPushMatrix()
    glTranslatef(0.0, 0.48, 0.0)   # mismo offset que draw() original con pos_y=0
    _beru.draw_tail()
    _beru.draw_wings()
    _beru.draw_body()
    _beru.draw_claws()
    _beru.draw_head()
    _beru.draw_eyes()
    _beru.draw_mouth()
    _beru.draw_antennae()
    _beru.draw_feet_basic()
    glPopMatrix()

# Tabla de funciones de dibujo del lobby (índice = personaje)
_LOBBY_DRAW = [
    lambda: _fg.draw_fallguy_full(),
    lambda: _au.draw_amongus_full(),
    _draw_beru_lobby,
    lambda: _cat.draw_cat(),
    lambda: _mk.draw_megaknight_full(),
    lambda: _tot.draw_totoro_full(),
]


# ════════════════════════════════════════════════════════════
# HELPERS VISUALES
# ════════════════════════════════════════════════════════════
def _txt(x, y, text, font=GLUT_BITMAP_HELVETICA_12, color=(1, 1, 1)):
    glColor3f(*color)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))


def _brightness(dist):
    """Luminosidad según distancia al centro de selección."""
    return max(0.28, 1.0 - (dist / SPACING) * 0.45)


def _scale_fac(dist):
    """Factor de escala según distancia al centro de selección."""
    return max(0.42, 1.0 - (dist / SPACING) * 0.30)


def _draw_disc(r, g, b, radius=1.0, alpha=0.55):
    """Disco plano semitransparente a y=0.01 (plataforma/sombra)."""
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(r, g, b, alpha)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, 0.01, 0.0)
    for i in range(33):
        a = 2 * math.pi * i / 32
        glVertex3f(radius * math.cos(a), 0.01, radius * math.sin(a))
    glEnd()
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)


def _draw_floor():
    """Suelo oscuro con cuadrícula sutil."""
    glDisable(GL_LIGHTING)
    glColor3f(0.07, 0.06, 0.14)
    glBegin(GL_QUADS)
    glVertex3f(-50, 0.0, -20)
    glVertex3f( 50, 0.0, -20)
    glVertex3f( 50, 0.0,  12)
    glVertex3f(-50, 0.0,  12)
    glEnd()
    glColor3f(0.12, 0.10, 0.22)
    glLineWidth(0.7)
    glBegin(GL_LINES)
    for xi in range(-30, 31, 2):
        glVertex3f(xi, 0.01, -20); glVertex3f(xi, 0.01, 12)
    for zi in range(-10, 7, 2):
        glVertex3f(-50, 0.01, zi); glVertex3f(50, 0.01, zi)
    glEnd()
    glLineWidth(1.0)
    glEnable(GL_LIGHTING)


# ════════════════════════════════════════════════════════════
# INICIALIZACIÓN GL DEL LOBBY
# ════════════════════════════════════════════════════════════
def arcade_init():
    global _lobby_fase
    _lobby_fase = 0
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)

    # Luz principal: blanca, direccional desde arriba-frente
    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 10.0, 8.0, 0.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.25, 0.25, 0.25, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.90, 0.90, 0.90, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.0,  0.0,  0.0,  1.0])

    # Luz de acento: coloreada según personaje seleccionado (empieza apagada)
    glLightfv(GL_LIGHT1, GL_AMBIENT,  [0.0, 0.0, 0.0, 1.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE,  [0.0, 0.0, 0.0, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
    glLightfv(GL_LIGHT1, GL_POSITION, [0.0, 3.0, 5.0, 1.0])


# ════════════════════════════════════════════════════════════
# ESCENA 3D DEL LOBBY
# ════════════════════════════════════════════════════════════
def _draw_lobby_3d():
    global _lob_offset, _lob_timer

    # ── Lerp del offset de animación ─────────────────────────
    diff = _lob_target - _lob_offset
    _lob_offset += diff * 0.10
    if abs(diff) < 0.001:
        _lob_offset = _lob_target

    _lob_timer += 1

    # ── Limpiar y configurar perspectiva ─────────────────────
    glClearColor(0.04, 0.03, 0.12, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(46.0, WIN_W / WIN_H, 0.1, 200.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Cámara del lobby: ligeramente elevada, mirando al centro de la línea
    gluLookAt(
        0.0,  2.8, 11.5,   # ojo
        0.0,  0.9,  0.0,   # objetivo
        0.0,  1.0,  0.0    # arriba
    )

    # Reposicionar luz 0 en espacio del mundo (después del lookAt)
    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 10.0, 8.0, 0.0])

    # ── Suelo ────────────────────────────────────────────────
    _draw_floor()

    # ── Línea de personajes ───────────────────────────────────
    for i in range(N):
        world_x  = i * SPACING - _lob_offset
        dist     = abs(world_x)
        is_sel_p1 = (i == selected_p1) and (_lobby_fase in (1, 3))
        is_sel_p2 = (i == selected_p2) and (_lobby_fase in (2, 3))
        # El carrusel sigue al jugador cuya fase es activa
        is_sel    = (i == selected_p1 and _lobby_fase == 1) or \
                    (i == selected_p2 and _lobby_fase == 2) or \
                    (_lobby_fase == 3 and i in (selected_p1, selected_p2))
        brt      = _brightness(dist)
        sf       = _scale_fac(dist) * _LOBBY_CFG[i]["scale"]
        y_off    = _LOBBY_CFG[i]["y_off"]
        z_push   = -dist * 0.08       # leve recesión de los laterales
        bob      = math.sin(_lob_timer * 0.045) * 0.08 if is_sel else 0.0

        # ── Ajustar iluminación para este personaje ───────────
        glLightfv(GL_LIGHT0, GL_DIFFUSE,
                  [brt,       brt,       brt,      1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT,
                  [brt*0.28,  brt*0.28,  brt*0.28, 1.0])

        if is_sel:
            # Luz de acento coloreada encima del personaje seleccionado
            cr, cg, cb = CHARACTERS[i]["color"]
            glLightfv(GL_LIGHT1, GL_POSITION,
                      [world_x, 4.0, 3.0, 1.0])
            glLightfv(GL_LIGHT1, GL_DIFFUSE,
                      [cr*0.35, cg*0.35, cb*0.35, 1.0])
        else:
            glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.0, 0.0, 0.0, 1.0])

        # ── Plataforma bajo el personaje ─────────────────────
        glPushMatrix()
        glTranslatef(world_x, 0.0, z_push)
        if is_sel_p1 and is_sel_p2:
            _draw_disc(0.90, 0.12, 0.12, radius=0.85, alpha=0.75)   # rojo  J1
            _draw_disc(0.12, 0.35, 0.95, radius=1.25, alpha=0.45)   # azul  J2 (aura exterior)
        elif is_sel_p1:
            _draw_disc(0.90, 0.12, 0.12, radius=1.15, alpha=0.70)   # rojo  J1
        elif is_sel_p2:
            _draw_disc(0.12, 0.35, 0.95, radius=1.15, alpha=0.70)   # azul  J2
        else:
            _draw_disc(0.22, 0.20, 0.35, radius=0.70, alpha=0.28)
        glPopMatrix()

        # ── Personaje ─────────────────────────────────────────
        glPushMatrix()
        glTranslatef(world_x, y_off + bob, z_push)
        glScalef(sf, sf, sf)
        try:
            _LOBBY_DRAW[i]()
        except Exception as e:
            # Cubo de sustitución si algo falla
            cr, cg, cb = CHARACTERS[i]["color"]
            glDisable(GL_LIGHTING)
            glColor3f(cr, cg, cb)
            glutSolidCube(1.0)
            glEnable(GL_LIGHTING)
        glPopMatrix()

    # ── Restaurar luces a valores por defecto ─────────────────
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.9,  0.9,  0.9,  1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.25, 0.25, 0.25, 1.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE,  [0.0,  0.0,  0.0,  1.0])


# ════════════════════════════════════════════════════════════
# HUD 2D SOBRE EL LOBBY
# ════════════════════════════════════════════════════════════
def _hud_panel(x, y, w, h, r, g, b, a=0.55):
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(r, g, b, a)
    glBegin(GL_QUADS)
    glVertex2f(x, y); glVertex2f(x+w, y)
    glVertex2f(x+w, y+h); glVertex2f(x, y+h)
    glEnd(); glDisable(GL_BLEND)


def _draw_lobby_hud():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix(); glLoadIdentity()
    glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST)
    cx = WIN_W // 2

    # ── Encabezado ────────────────────────────────────────────
    _hud_panel(0, WIN_H-56, WIN_W, 56, 0.0, 0.0, 0.0, 0.60)
    _txt(cx - 200, WIN_H - 24,
         "ARCADE 3D  —  Graficacion 2026",
         GLUT_BITMAP_HELVETICA_18, (0.95, 0.85, 0.20))
    _txt(cx - 170, WIN_H - 46,
         "Instituto Tecnologico de Toluca  |  Equipo",
         GLUT_BITMAP_HELVETICA_12, (0.65, 0.75, 0.95))

    # ══════════════════════════════════════
    #  FASE 0 — Pantalla de instrucciones
    # ══════════════════════════════════════
    if _lobby_fase == 0:
        _hud_panel(cx-310, WIN_H//2-140, 620, 280, 0.0, 0.0, 0.0, 0.75)
        lines = [
            ("¡BIENVENIDO AL ARCADE 3D!", GLUT_BITMAP_HELVETICA_18, (0.95, 0.85, 0.20)),
            ("", None, None),
            ("Paso 1:  Jugador 1 elige su personaje",   GLUT_BITMAP_HELVETICA_12, (1.00, 0.35, 0.35)),
            ("         Usa las Flechas  ←  →  para navegar", GLUT_BITMAP_HELVETICA_12, (0.88, 0.88, 0.88)),
            ("         Presiona  ENTER  para confirmar",      GLUT_BITMAP_HELVETICA_12, (0.88, 0.88, 0.88)),
            ("", None, None),
            ("Paso 2:  Jugador 2 elige su personaje",   GLUT_BITMAP_HELVETICA_12, (0.40, 0.60, 1.00)),
            ("         Usa  A / D  para navegar",              GLUT_BITMAP_HELVETICA_12, (0.88, 0.88, 0.88)),
            ("         Presiona  ESPACIO  para confirmar",     GLUT_BITMAP_HELVETICA_12, (0.88, 0.88, 0.88)),
            ("", None, None),
            ("Paso 3:  Presiona  N  para jugar juntos", GLUT_BITMAP_HELVETICA_12, (0.40, 0.95, 0.55)),
            ("         (N  avanza de nivel: 1 → 2 → 3)",      GLUT_BITMAP_HELVETICA_12, (0.65, 0.75, 0.65)),
        ]
        base_y = WIN_H//2 + 120
        for lbl, font, col in lines:
            if font:
                _txt(cx - 260, base_y, lbl, font, col)
            base_y -= 20
        _txt(cx - 130, WIN_H//2 - 155,
             "Presiona CUALQUIER TECLA para empezar",
             GLUT_BITMAP_HELVETICA_12, (0.60, 0.60, 0.60))

    # ══════════════════════════════════════
    #  FASE 1 — J1 elige
    # ══════════════════════════════════════
    elif _lobby_fase == 1:
        ch1 = CHARACTERS[selected_p1]
        # Banner J1
        _hud_panel(cx-200, WIN_H-110, 400, 50, 0.55, 0.05, 0.05, 0.80)
        _txt(cx-185, WIN_H-78,
             "JUGADOR 1  —  Usa  ←  →  y presiona ENTER",
             GLUT_BITMAP_HELVETICA_12, (1.00, 0.55, 0.55))
        _txt(cx-170, WIN_H-98,
             "Elige tu personaje  (circulo ROJO = tu seleccion)",
             GLUT_BITMAP_HELVETICA_12, (0.90, 0.75, 0.75))
        # Tarjeta personaje
        _hud_panel(0, WIN_H-200, 230, 140, 0.45, 0.05, 0.05, 0.65)
        _txt(8, WIN_H-78,  "JUGADOR 1", GLUT_BITMAP_HELVETICA_12, (1.00, 0.35, 0.35))
        _txt(8, WIN_H-98,  ch1["label"],GLUT_BITMAP_HELVETICA_18, (1.00, 0.55, 0.55))
        _txt(8, WIN_H-122, f"Autor: {ch1['author']}",
             GLUT_BITMAP_HELVETICA_12, (0.85, 0.75, 0.75))
        for k, line in enumerate(ch1["desc"]):
            _txt(8, WIN_H-142-k*16, line, GLUT_BITMAP_HELVETICA_12, (0.80, 0.70, 0.70))
        # Dot indicadores
        _draw_lobby_dots(selected_p1, -1, (0.90,0.10,0.10), None)

    # ══════════════════════════════════════
    #  FASE 2 — J2 elige
    # ══════════════════════════════════════
    elif _lobby_fase == 2:
        ch1 = CHARACTERS[selected_p1]
        ch2 = CHARACTERS[selected_p2]
        # Banner J2
        _hud_panel(cx-200, WIN_H-110, 400, 50, 0.05, 0.10, 0.55, 0.80)
        _txt(cx-175, WIN_H-78,
             "JUGADOR 2  —  Usa  A  D  y presiona ESPACIO",
             GLUT_BITMAP_HELVETICA_12, (0.55, 0.75, 1.00))
        _txt(cx-170, WIN_H-98,
             "Elige tu personaje  (circulo AZUL = tu seleccion)",
             GLUT_BITMAP_HELVETICA_12, (0.70, 0.80, 0.95))
        # Tarjeta J1 (ya confirmado, izquierda)
        _hud_panel(0, WIN_H-200, 230, 140, 0.45, 0.05, 0.05, 0.50)
        _txt(8, WIN_H-78,  "J1 listo:", GLUT_BITMAP_HELVETICA_12, (1.00, 0.35, 0.35))
        _txt(8, WIN_H-98,  ch1["label"],GLUT_BITMAP_HELVETICA_18, (1.00, 0.55, 0.55))
        # Tarjeta J2 (derecha)
        _hud_panel(WIN_W-230, WIN_H-200, 230, 140, 0.05, 0.10, 0.55, 0.65)
        _txt(WIN_W-225, WIN_H-78,  "JUGADOR 2", GLUT_BITMAP_HELVETICA_12, (0.40, 0.60, 1.00))
        _txt(WIN_W-225, WIN_H-98,  ch2["label"],GLUT_BITMAP_HELVETICA_18, (0.55, 0.75, 1.00))
        _txt(WIN_W-225, WIN_H-122, f"Autor: {ch2['author']}",
             GLUT_BITMAP_HELVETICA_12, (0.75, 0.82, 0.95))
        for k, line in enumerate(ch2["desc"]):
            _txt(WIN_W-225, WIN_H-142-k*16, line, GLUT_BITMAP_HELVETICA_12, (0.70, 0.78, 0.90))
        _draw_lobby_dots(selected_p1, selected_p2, (0.90,0.10,0.10), (0.10,0.35,0.95))

    # ══════════════════════════════════════
    #  FASE 3 — Confirmar / cambiar
    # ══════════════════════════════════════
    elif _lobby_fase == 3:
        ch1 = CHARACTERS[selected_p1]
        ch2 = CHARACTERS[selected_p2]
        # Panel central de confirmación
        _hud_panel(cx-300, WIN_H//2-80, 600, 160, 0.0, 0.0, 0.0, 0.82)
        _txt(cx-230, WIN_H//2+55,
             "¡Listos! ¿Quieren cambiar de personaje?",
             GLUT_BITMAP_HELVETICA_18, (0.95, 0.90, 0.30))
        _txt(cx-270, WIN_H//2+28,
             f"  J1 (ROJO):  {ch1['label']}          J2 (AZUL):  {ch2['label']}",
             GLUT_BITMAP_HELVETICA_12, (0.90, 0.90, 0.90))
        _txt(cx-255, WIN_H//2+8,
             "Presiona  1  para que J1 vuelva a elegir",
             GLUT_BITMAP_HELVETICA_12, (1.00, 0.55, 0.55))
        _txt(cx-255, WIN_H//2-12,
             "Presiona  2  para que J2 vuelva a elegir",
             GLUT_BITMAP_HELVETICA_12, (0.55, 0.75, 1.00))
        _txt(cx-200, WIN_H//2-38,
             "Presiona  N  para jugar  (Nivel 1→2→3)",
             GLUT_BITMAP_HELVETICA_12, (0.40, 0.95, 0.55))
        _txt(cx-170, WIN_H//2-58,
             "Presiona  ENTER  para jugar en modo individual",
             GLUT_BITMAP_HELVETICA_12, (0.65, 0.65, 0.65))
        _draw_lobby_dots(selected_p1, selected_p2, (0.90,0.10,0.10), (0.10,0.35,0.95))

    # ── Barra de controles inferior ───────────────────────────
    _hud_panel(0, 0, WIN_W, 38, 0.0, 0.0, 0.0, 0.60)
    if _lobby_fase == 0:
        hint = "Cualquier tecla : continuar     ESC : salir"
    elif _lobby_fase == 1:
        hint = "Flechas : navegar    ENTER : confirmar personaje de J1    ESC : salir"
    elif _lobby_fase == 2:
        hint = "A/D : navegar    ESPACIO : confirmar personaje de J2    ESC : volver"
    else:
        hint = "N : jugar nivel    1 : cambiar J1    2 : cambiar J2    ENTER : modo individual    ESC : salir"
    _txt(WIN_W//2 - len(hint)*3, 14, hint,
         GLUT_BITMAP_HELVETICA_12, (0.78, 0.78, 0.78))

    glEnable(GL_LIGHTING); glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()


def _draw_lobby_dots(p1_idx, p2_idx, col1, col2):
    """Dibuja los indicadores de personaje en la barra inferior del lobby."""
    dot_spacing = 22
    dot_start_x = WIN_W//2 - (N - 1) * dot_spacing // 2
    glDisable(GL_LIGHTING)
    for i in range(N):
        r2, g2, b2 = CHARACTERS[i]["color"]
        if col1 and i == p1_idx:
            glPointSize(14); glColor3f(*col1)
            glBegin(GL_POINTS); glVertex2f(dot_start_x + i*dot_spacing - 5, 56); glEnd()
        if col2 and i == p2_idx:
            glPointSize(14); glColor3f(*col2)
            glBegin(GL_POINTS); glVertex2f(dot_start_x + i*dot_spacing + 5, 56); glEnd()
        glPointSize(6 if i in (p1_idx, p2_idx) else 4)
        glColor3f(r2, g2, b2)
        glBegin(GL_POINTS); glVertex2f(dot_start_x + i*dot_spacing, 56); glEnd()
    glPointSize(1.0)


# ════════════════════════════════════════════════════════════
# ACTIVACIÓN DE PERSONAJE (ENTRAR AL JUEGO)
# ════════════════════════════════════════════════════════════
def _activate_character(idx):
    global estado_juego
    estado_juego = idx
    mod = MODULOS_PERSONAJES[idx]

    # Reconfigurar GL para el modo 3D del personaje
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    # Apagar la luz de acento del lobby
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.0, 0.0, 0.0, 1.0])

    if not _initialized[idx]:
        if hasattr(mod, 'init'):
            try:
                mod.init()
            except Exception as e:
                print(f"[Arcade] init() error en personaje {idx}: {e}")
        _initialized[idx] = True

    if hasattr(mod, 'reshape'):
        try:
            mod.reshape(WIN_W, WIN_H)
        except Exception as e:
            print(f"[Arcade] reshape() error en personaje {idx}: {e}")

    glutPostRedisplay()


def _activate_nivel(num):
    """
    Entra al nivel num (1, 2 o 3) usando el personaje actualmente
    seleccionado en el lobby como modelo visual de los jugadores.
    """
    global estado_nivel, estado_juego
    estado_nivel = num
    estado_juego = -1          # desactiva el modo personaje individual

    # Guardar los índices de personaje en el state del nivel
    nivel_state.personaje_idx   = selected_p1
    nivel_state.personaje_idx_p2 = selected_p2
    nivel_state.WIN_W = WIN_W
    nivel_state.WIN_H = WIN_H

    mod = MODULOS_NIVELES[num]
    if not _nivel_initialized[num]:
        try:
            mod.init()
        except Exception as e:
            print(f"[Arcade] init() error en nivel {num}: {e}")
        _nivel_initialized[num] = True
    else:
        # Ya inicializado: solo resetear el estado del nivel
        try:
            mod.reset()
        except Exception as e:
            print(f"[Arcade] reset() error en nivel {num}: {e}")

    glutPostRedisplay()


def _navigate(delta):
    """Mueve la selección del jugador activo delta posiciones."""
    global selected_p1, selected_p2, _lob_target
    if _selecting == 1:
        new_sel = selected_p1 + delta
        if 0 <= new_sel < N:
            selected_p1 = new_sel
            _lob_target = selected_p1 * SPACING
    else:
        new_sel = selected_p2 + delta
        if 0 <= new_sel < N:
            selected_p2 = new_sel
    glutPostRedisplay()


def _navigate_to(idx):
    """Salta directamente a un índice de personaje para el jugador activo."""
    global selected_p1, selected_p2
    if _selecting == 1:
        selected_p1 = max(0, min(N - 1, idx))
        _lob_target = selected_p1 * SPACING
    else:
        selected_p2 = max(0, min(N - 1, idx))
    glutPostRedisplay()


# ════════════════════════════════════════════════════════════
# CALLBACKS GLUT
# ════════════════════════════════════════════════════════════
# CALLBACKS GLUT
# ════════════════════════════════════════════════════════════

def _get_draw_fns():
    """
    Devuelve (draw_p1, draw_p2) según los personajes seleccionados.
    Si ambos jugadores eligieron el mismo personaje, P2 se dibuja
    con un tinte verde para diferenciarse (glColor llama antes del draw).
    """
    fns = [
        _fg.draw_fallguy_full,
        _au.draw_amongus_full,
        _beru.draw,
        _cat.draw_cat,
        _mk.draw_megaknight_full,
        _tot.draw_totoro_full,
    ]
    idx1 = getattr(nivel_state, 'personaje_idx',    0)
    idx2 = getattr(nivel_state, 'personaje_idx_p2', 1)

    fn1 = fns[idx1] if 0 <= idx1 < len(fns) else _au.draw_amongus_full
    fn2 = fns[idx2] if 0 <= idx2 < len(fns) else _au.draw_amongus_full

    if idx1 == idx2:
        # Mismo personaje: P2 con tinte verdoso (glColor4f afecta GL_COLOR_MATERIAL)
        def fn2_tinted():
            from OpenGL.GL import glColor4f, GL_LIGHTING, glIsEnabled
            glColor4f(0.40, 1.00, 0.50, 1.0)
            fn2()
            glColor4f(1.0, 1.0, 1.0, 1.0)   # restaurar
        return fn1, fn2_tinted

    return fn1, fn2


def display_maestro():
    global estado_nivel
    if estado_nivel > 0:
        mod = MODULOS_NIVELES[estado_nivel]
        draw_p1, draw_p2 = _get_draw_fns()
        mod.display(draw_p1, draw_p2)
    elif estado_juego == -1:
        _draw_lobby_3d()
        _draw_lobby_hud()
        glutSwapBuffers()
    else:
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        MODULOS_PERSONAJES[estado_juego].display()


def keyboard_maestro(key, x, y):
    global estado_juego, estado_nivel, _lobby_fase, selected_p1, selected_p2
    global _lob_target, _nivel_siguiente

    if key == b'\x1b':
        if estado_nivel > 0:
            estado_nivel = 0
            arcade_init()
            glutPostRedisplay()
        elif estado_juego == -1:
            if _lobby_fase == 0:
                sys.exit(0)
            elif _lobby_fase == 2:
                _lobby_fase = 1   # J2 vuelve atrás
            elif _lobby_fase == 3:
                _lobby_fase = 2
            else:
                sys.exit(0)
            glutPostRedisplay()
        else:
            estado_juego = -1
            arcade_init()
            glutPostRedisplay()
        return

    if estado_nivel > 0:
        MODULOS_NIVELES[estado_nivel].keyboard(key, x, y)
        return

    if estado_juego == -1:
        # ── Fase 0: instrucciones ─────────────────────────────
        if _lobby_fase == 0:
            _lobby_fase = 1
            glutPostRedisplay()
            return

        # ── Fase 1: J1 elige con Flechas + ENTER ─────────────
        elif _lobby_fase == 1:
            if key in (b'\r', b'\n'):
                _lobby_fase = 2       # J1 confirmado → ahora J2
                # Centrar carrusel en selección de J2
                _lob_target = selected_p2 * SPACING
            glutPostRedisplay()
            return

        # ── Fase 2: J2 elige con A/D + ESPACIO ───────────────
        elif _lobby_fase == 2:
            if key == b' ':          # ESPACIO confirma J2
                _lobby_fase = 3
            elif key in (b'a', b'A'):
                new = selected_p2 - 1
                if new >= 0:
                    selected_p2 = new
                    _lob_target = selected_p2 * SPACING
            elif key in (b'd', b'D'):
                new = selected_p2 + 1
                if new < N:
                    selected_p2 = new
                    _lob_target = selected_p2 * SPACING
            glutPostRedisplay()
            return

        # ── Fase 3: confirmación ──────────────────────────────
        elif _lobby_fase == 3:
            if key in (b'n', b'N'):
                _activate_nivel(_nivel_siguiente)
                _nivel_siguiente = (_nivel_siguiente % 3) + 1  # prepara el siguiente
            elif key in (b'\r', b'\n'):
                _activate_character(selected_p1)
            elif key == b'1':
                _lobby_fase = 1
                _lob_target = selected_p1 * SPACING
            elif key == b'2':
                _lobby_fase = 2
                _lob_target = selected_p2 * SPACING
            glutPostRedisplay()
            return
    else:
        MODULOS_PERSONAJES[estado_juego].keyboard(key, x, y)


def keyboard_up_maestro(key, x, y):
    if estado_nivel > 0:
        mod = MODULOS_NIVELES[estado_nivel]
        if hasattr(mod, 'keyboard_up'):
            mod.keyboard_up(key, x, y)


def special_maestro(key, x, y):
    global selected_p1, _lob_target
    if estado_nivel > 0:
        MODULOS_NIVELES[estado_nivel].special_keys(key, x, y)
        return
    if estado_juego == -1:
        if _lobby_fase == 1:   # solo J1 con flechas
            if key == GLUT_KEY_LEFT:
                new = selected_p1 - 1
                if new >= 0:
                    selected_p1 = new; _lob_target = selected_p1 * SPACING
            elif key == GLUT_KEY_RIGHT:
                new = selected_p1 + 1
                if new < N:
                    selected_p1 = new; _lob_target = selected_p1 * SPACING
            glutPostRedisplay()
    else:
        if hasattr(MODULOS_PERSONAJES[estado_juego], 'special_keys'):
            MODULOS_PERSONAJES[estado_juego].special_keys(key, x, y)


def special_up_maestro(key, x, y):
    if estado_nivel > 0:
        mod = MODULOS_NIVELES[estado_nivel]
        if hasattr(mod, 'special_keys_up'):
            mod.special_keys_up(key, x, y)


def mouse_maestro(button, state_btn, x, y):
    global _mouse_down, _mouse_last_x, _drag_accum
    if estado_nivel > 0:
        return
    if estado_juego == -1:
        if button == GLUT_LEFT_BUTTON:
            _mouse_down  = (state_btn == GLUT_DOWN)
            _mouse_last_x = x
            _drag_accum  = 0
        elif button == 3 and state_btn == GLUT_DOWN:
            _navigate(-1)
        elif button == 4 and state_btn == GLUT_DOWN:
            _navigate(1)
    else:
        if hasattr(MODULOS_PERSONAJES[estado_juego], 'mouse'):
            MODULOS_PERSONAJES[estado_juego].mouse(button, state_btn, x, y)


def motion_maestro(x, y):
    global _mouse_last_x, _drag_accum
    if estado_nivel > 0:
        return
    if estado_juego == -1:
        if _mouse_down:
            dx = x - _mouse_last_x
            _drag_accum  += dx
            _mouse_last_x  = x
            if _drag_accum > DRAG_THRESH:
                _navigate(1)
                _drag_accum = 0
            elif _drag_accum < -DRAG_THRESH:
                _navigate(-1)
                _drag_accum = 0
    else:
        if hasattr(MODULOS_PERSONAJES[estado_juego], 'motion'):
            MODULOS_PERSONAJES[estado_juego].motion(x, y)


def timer_maestro(value):
    if estado_nivel > 0:
        MODULOS_NIVELES[estado_nivel].update(value)
    elif estado_juego != -1:
        if hasattr(MODULOS_PERSONAJES[estado_juego], 'update'):
            MODULOS_PERSONAJES[estado_juego].update(value)
    glutPostRedisplay()
    glutTimerFunc(16, timer_maestro, 0)


def reshape_maestro(w, h):
    global WIN_W, WIN_H
    WIN_W, WIN_H = w, max(h, 1)
    nivel_state.WIN_W = WIN_W
    nivel_state.WIN_H = WIN_H
    glViewport(0, 0, WIN_W, WIN_H)
    if estado_nivel == 0 and estado_juego != -1:
        mod = MODULOS_PERSONAJES[estado_juego]
        if hasattr(mod, 'reshape'):
            mod.reshape(w, h)


# ════════════════════════════════════════════════════════════
# ENTRADA
# ════════════════════════════════════════════════════════════
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutInitWindowPosition(100, 80)
    glutCreateWindow(b"Arcade 3D  -  Graficacion 2026")

    arcade_init()

    glutDisplayFunc(display_maestro)
    glutKeyboardFunc(keyboard_maestro)
    glutKeyboardUpFunc(keyboard_up_maestro)
    glutSpecialFunc(special_maestro)
    glutSpecialUpFunc(special_up_maestro)
    glutMouseFunc(mouse_maestro)
    glutMotionFunc(motion_maestro)
    glutReshapeFunc(reshape_maestro)
    glutTimerFunc(16, timer_maestro, 0)
    glutMainLoop()


if __name__ == "__main__":
    main()