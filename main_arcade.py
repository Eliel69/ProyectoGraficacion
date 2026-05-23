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
import lobby_audio
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
# Flujo de seleccion: 0=intro, 1=elige J1, 2=elige J2, 3=confirmar, 4=explorar individual
# Fases 5 y 6 = animacion feliz de J1/J2 antes de continuar
_lobby_fase   = 0
selected_ind  = 0
_selecting    = 1   # 1=J1 navega, 2=J2 navega (usado en _navigate)
estado_juego = -1          # -1 = lobby,  0..5 = personaje activo
estado_nivel = 0           # 0 = sin nivel, 1..3 = nivel activo
_confirmando_salida = False # True cuando se muestra dialogo de salida en nivel
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
        is_sel_p1 = (i == selected_p1) and (_lobby_fase in (1, '1b', '2b'))
        is_sel_p2 = (i == selected_p2) and (_lobby_fase in (2, '2b'))
        is_sel_ind = (i == selected_ind) and (_lobby_fase == 4)
        is_sel    = (i == selected_p1 and _lobby_fase in (1, '1b')) or \
                    (i == selected_p2 and _lobby_fase in (2, '2b')) or \
                    (i == selected_ind and _lobby_fase == 4)
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
        if is_sel_ind:
            _draw_disc(0.90, 0.90, 0.90, radius=1.15, alpha=0.70)   # blanco individual
        elif is_sel_p1 and is_sel_p2:
            _draw_disc(0.90, 0.12, 0.12, radius=0.85, alpha=0.75)
            _draw_disc(0.12, 0.35, 0.95, radius=1.25, alpha=0.45)
        elif is_sel_p1:
            _draw_disc(0.90, 0.12, 0.12, radius=1.15, alpha=0.70)
        elif is_sel_p2:
            _draw_disc(0.12, 0.35, 0.95, radius=1.15, alpha=0.70)
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
        _hud_panel(cx-310, WIN_H//2-165, 620, 330, 0.0, 0.0, 0.0, 0.82)
        lines = [
            ("¡BIENVENIDO AL ARCADE 3D!", GLUT_BITMAP_HELVETICA_18, (0.95, 0.85, 0.20)),
            ("", None, None),
            ("--- Para jugar! ---", GLUT_BITMAP_HELVETICA_18, (0.70, 0.90, 0.70)),
            ("Paso 1:  J1 usa Flechas <- -> y ENTER para confirmar.", GLUT_BITMAP_HELVETICA_12, (1.00, 0.55, 0.55)),
            ("Paso 2:  J2 usa A / D y ESPACIO para confirmar.",       GLUT_BITMAP_HELVETICA_12, (0.55, 0.75, 1.00)),
            ("Paso 3:  Presiona ENTER para empezar Nivel 1 -> 2 -> 3.", GLUT_BITMAP_HELVETICA_12, (0.40, 0.95, 0.55)),
            ("", None, None),
            ("--- Exploracion---", GLUT_BITMAP_HELVETICA_18, (0.90, 0.75, 0.30)),
            ("Presiona F1 para explorar un personaje tu solo (no cuenta con niveles).", GLUT_BITMAP_HELVETICA_12, (0.88, 0.78, 0.55)),
            ("Usa ESC dentro del personaje para regresar aqui.", GLUT_BITMAP_HELVETICA_12, (0.75, 0.75, 0.75)),
        ]
        base_y = WIN_H//2 + 140
        for lbl, font, col in lines:
            if font:
                _txt(cx - 270, base_y, lbl, font, col)
            base_y -= 22
        _hud_panel(cx-220, WIN_H//2-172, 440, 32, 0.25, 0.25, 0.0, 0.85)
        _txt(cx - 205, WIN_H//2-160,
             ">>> Presiona CUALQUIER TECLA para empezar <<<",
             GLUT_BITMAP_HELVETICA_12, (1.0, 0.95, 0.40))

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
        _txt(cx-220, WIN_H//2-38,
             "Presiona  ENTER  para empezar a jugar  (Nivel 1 -> 2 -> 3)",
             GLUT_BITMAP_HELVETICA_12, (0.40, 0.95, 0.55))
        _txt(cx-195, WIN_H//2-60,
             "F1 : explorar tu personaje de forma individual",
             GLUT_BITMAP_HELVETICA_12, (0.60, 0.60, 0.65))
        _draw_lobby_dots(selected_p1, selected_p2, (0.90,0.10,0.10), (0.10,0.35,0.95))

    # ══════════════════════════════════════
    #  FASE 4 — Explorar individual
    # ══════════════════════════════════════
    elif _lobby_fase == 4:
        ch = CHARACTERS[selected_ind]
        _hud_panel(cx-220, WIN_H//2+50, 440, 50, 0.0, 0.0, 0.0, 0.75)
        _txt(cx-200, WIN_H//2+73,
             "MODO INDIVIDUAL — Exploracion de personajes",
             GLUT_BITMAP_HELVETICA_18, (0.90, 0.75, 0.30))
        _hud_panel(cx-180, WIN_H//2+20, 360, 26, 0.0, 0.0, 0.0, 0.65)
        _txt(cx-165, WIN_H//2+28,
             ch["label"] + "  —  Autor: " + ch["author"],
             GLUT_BITMAP_HELVETICA_12, (0.90, 0.90, 0.90))
        _draw_lobby_dots(selected_ind, -1, (0.90,0.90,0.90), None)

    # ══════════════════════════════════════
    #  FASES 5/6 — Animacion de confirmacion
    # ══════════════════════════════════════
    elif _lobby_fase == '1b':
        ch1 = CHARACTERS[selected_p1]
        _hud_panel(cx-270, WIN_H//2-50, 540, 100, 0.0, 0.0, 0.0, 0.88)
        _txt(cx-250, WIN_H//2+30,
             "J1: Confirmas a " + ch1["label"] + "?",
             GLUT_BITMAP_HELVETICA_18, (1.0, 0.55, 0.55))
        _txt(cx-180, WIN_H//2+5,
             "S = Si, jugar con este personaje",
             GLUT_BITMAP_HELVETICA_12, (0.40, 1.0, 0.40))
        _txt(cx-155, WIN_H//2-15,
             "N = No, elegir otro personaje",
             GLUT_BITMAP_HELVETICA_12, (1.0, 0.60, 0.60))
        _draw_lobby_dots(selected_p1, -1, (0.90,0.10,0.10), None)

    elif _lobby_fase == '2b':
        ch2 = CHARACTERS[selected_p2]
        _hud_panel(cx-270, WIN_H//2-50, 540, 100, 0.0, 0.0, 0.0, 0.88)
        _txt(cx-250, WIN_H//2+30,
             "J2: Confirmas a " + ch2["label"] + "?",
             GLUT_BITMAP_HELVETICA_18, (0.55, 0.75, 1.0))
        _txt(cx-180, WIN_H//2+5,
             "S = Si, listos para jugar!",
             GLUT_BITMAP_HELVETICA_12, (0.40, 1.0, 0.40))
        _txt(cx-155, WIN_H//2-15,
             "N = No, elegir otro personaje",
             GLUT_BITMAP_HELVETICA_12, (0.70, 0.85, 1.0))
        _draw_lobby_dots(selected_p1, selected_p2, (0.90,0.10,0.10), (0.10,0.35,0.95))

    # ── Barra de controles inferior ───────────────────────────
    _hud_panel(0, 0, WIN_W, 38, 0.0, 0.0, 0.0, 0.60)
    if _lobby_fase == 0:
        hint = "Cualquier tecla : empezar    F1 : explorar personaje individual    ESC : salir"
    elif _lobby_fase == 1:
        hint = "Flechas : navegar    ENTER : confirmar personaje de J1    ESC : salir"
    elif _lobby_fase == 2:
        hint = "A/D : navegar    ESPACIO : confirmar personaje de J2    ESC : volver"
    elif _lobby_fase == 4:
        hint = "Flechas : navegar personaje    ENTER : explorar este    ESC : volver a instrucciones"
    elif _lobby_fase == '1b':
        hint = "S : confirmar personaje de J1    N : volver a elegir"
    elif _lobby_fase == '2b':
        hint = "S : confirmar personaje de J2    N : volver a elegir    ENTER : jugar!"
    else:
        hint = "ENTER : jugar    1/2 : cambiar personaje    F1 : explorar individual    ESC : salir"
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
    lobby_audio.stop_lobby()   # parar música del lobby al entrar individual
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


# ── Expresion feliz por personaje al confirmar seleccion ─────

def _set_happy_expression(idx):
    """Activa la expresión feliz del personaje seleccionado."""
    try:
        # 0=FallGuy  1=AmongUs  2=Beru  3=Gato  4=MegaCaballero  5=Totoro
        if idx == 0:
            from fallguy.actions import state as _st
            _st.expression = "wink"
        elif idx == 1:
            from AmongUsFinal.actions import state as _st
            _st.expression = "surprised"
        elif idx == 2:
            from beru.actions import update as _upd
            _upd.set_expression('admire')
        elif idx == 3:
            from gato_3d.actions import state as _st
            _st.current_expression = "felicidad"
        elif idx == 4:
            from MegaCaballero.actions import state as _st
            _st.expression = 3
        elif idx == 5:
            from totoro.actions import state as _st
            _st.expression = "surprised"
    except Exception as e:
        print(f"[happy expr] {e}")


def _reset_all_expressions():
    """Resetea la expresión de todos los personajes a neutral."""
    try:
        from fallguy.actions import state as _s0;      _s0.expression = "neutral"
    except Exception: pass
    try:
        from AmongUsFinal.actions import state as _s1; _s1.expression = "neutral"
    except Exception: pass
    try:
        from beru.actions import state as _s2;         _s2.expression = "neutral"; _s2.expression_timer = 0
    except Exception: pass
    try:
        from gato_3d.actions import state as _s3;      _s3.current_expression = "neutral"
    except Exception: pass
    try:
        from MegaCaballero.actions import state as _s4; _s4.expression = 0
    except Exception: pass
    try:
        from totoro.actions import state as _st;       _st.expression = "neutral"
    except Exception: pass


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

    # Parar lobby y arrancar música del nivel
    lobby_audio.stop_lobby()
    lobby_audio.play_nivel(num)
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


def _draw_confirm_exit():
    """Superpone el dialogo de confirmacion de salida sobre el nivel."""
    from OpenGL.GL  import (glMatrixMode,glPushMatrix,glLoadIdentity,
                             glDisable,glEnable,GL_LIGHTING,GL_DEPTH_TEST,
                             glColor4f,glBegin,glEnd,glVertex2f,GL_QUADS,
                             glColor3f,glRasterPos2f,GL_BLEND,GL_SRC_ALPHA,
                             GL_ONE_MINUS_SRC_ALPHA,glBlendFunc)
    from OpenGL.GLU  import gluOrtho2D
    from OpenGL.GLUT import (glutGet,GLUT_WINDOW_WIDTH,GLUT_WINDOW_HEIGHT,
                              GLUT_BITMAP_HELVETICA_18,GLUT_BITMAP_HELVETICA_12,
                              glutBitmapCharacter)
    w=glutGet(GLUT_WINDOW_WIDTH); h=glutGet(GLUT_WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0,w,0,h)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST)
    cx=w//2; cy=h//2
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0,0,0,0.80)
    glBegin(GL_QUADS)
    glVertex2f(cx-260,cy-90); glVertex2f(cx+260,cy-90)
    glVertex2f(cx+260,cy+90); glVertex2f(cx-260,cy+90)
    glEnd(); glDisable(GL_BLEND)
    def txt(x,y,s,font,col):
        glColor3f(*col); glRasterPos2f(x,y)
        for c in s: glutBitmapCharacter(font,ord(c))
    txt(cx-190,cy+55,"Salir al lobby?",GLUT_BITMAP_HELVETICA_18,(0.95,0.85,0.20))
    txt(cx-230,cy+20,"Los puntajes acumulados se perderan.",
        GLUT_BITMAP_HELVETICA_12,(0.88,0.70,0.70))
    txt(cx-195,cy-10,"ENTER / S : confirmar salida",
        GLUT_BITMAP_HELVETICA_12,(1.00,0.55,0.55))
    txt(cx-165,cy-35,"Cualquier otra tecla : continuar",
        GLUT_BITMAP_HELVETICA_12,(0.55,0.90,0.55))
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()


# ── Variables y funciones del sistema de ganador ─────────────
_winner_active   = False
_winner_spin     = 0.0
_winner_player   = 1
_winner_char_idx = 0

def _show_winner(player, char_idx):
    global _winner_active, _winner_spin, _winner_player, _winner_char_idx
    _winner_active   = True
    _winner_spin     = 0.0
    _winner_player   = player
    _winner_char_idx = char_idx
    _set_happy_expression(char_idx)
    lobby_audio.stop_nivel()
    lobby_audio.play_aplausos()

def _hide_winner():
    global _winner_active
    _winner_active = False
    _reset_all_expressions()
    lobby_audio.stop_aplausos()
    lobby_audio.play_lobby()

def _draw_winner_overlay():
    w = glutGet(GLUT_WINDOW_WIDTH); h = glutGet(GLUT_WINDOW_HEIGHT)
    glClearColor(0.04, 0.02, 0.10, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluPerspective(45.0, w/max(h,1), 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    gluLookAt(0, 3, 8, 0, 1, 0, 0, 1, 0)
    glEnable(GL_LIGHTING); glEnable(GL_DEPTH_TEST)
    # Iluminacion del winner: dos luces brillantes para evitar opacidad
    glEnable(GL_LIGHT0); glEnable(GL_LIGHT1)
    glLightfv(GL_LIGHT0, GL_POSITION, [3.0, 8.0, 6.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.35, 0.35, 0.35, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.00, 1.00, 1.00, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.00, 1.00, 1.00, 1.0])
    glLightfv(GL_LIGHT1, GL_POSITION, [-3.0, 5.0, 4.0, 1.0])
    glLightfv(GL_LIGHT1, GL_AMBIENT,  [0.0,  0.0,  0.0,  1.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE,  [0.45, 0.45, 0.55, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.0,  0.0,  0.0,  1.0])
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT, GL_SPECULAR,  [0.60, 0.60, 0.60, 1.0])
    glMaterialf (GL_FRONT, GL_SHININESS, 64.0)
    fns = [_fg.draw_fallguy_full, _au.draw_amongus_full, _beru.draw,
           _cat.draw_cat, _mk.draw_megaknight_full, _tot.draw_totoro_full]
    sc_list  = [0.55, 0.55, 0.55, 0.55, 0.55, 0.13]
    off_list = [0.0,  0.0,  0.0,  0.0,  0.55, 0.0 ]
    idx = _winner_char_idx
    sc  = sc_list[idx]; yoff = off_list[idx]
    glPushMatrix()
    glRotatef(_winner_spin, 0, 1, 0)
    glScalef(sc, sc, sc)
    glTranslatef(0.0, yoff/sc if sc else 0, 0.0)
    try: fns[idx]()
    except Exception: pass
    glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST)
    def txt(x,y,s,font,col):
        glColor3f(*col); glRasterPos2f(x,y)
        for c in s: glutBitmapCharacter(font,ord(c))
    def panel(x,y,pw,ph,r,g,b,a=0.82):
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(r,g,b,a)
        glBegin(GL_QUADS)
        glVertex2f(x,y); glVertex2f(x+pw,y)
        glVertex2f(x+pw,y+ph); glVertex2f(x,y+ph)
        glEnd(); glDisable(GL_BLEND)
    cx = w//2
    panel(cx-290,h-100,580,90,0,0,0,0.88)
    wcol=(1.0,0.35,0.35) if _winner_player==1 else (0.35,0.60,1.0)
    txt(cx-245,h-38,f"FELICIDADES JUGADOR {_winner_player}!",
        GLUT_BITMAP_HELVETICA_18,wcol)
    cr,cg,cb = CHARACTERS[_winner_char_idx]["color"]
    txt(cx-205,h-62,f"Personaje: {CHARACTERS[_winner_char_idx]['label']}",
        GLUT_BITMAP_HELVETICA_12,(cr,cg,cb))
    from niveles import state as _ns
    if _ns.score_p1 > _ns.score_p2:
        fin="Puntaje final  J1:"+str(_ns.score_p1)+"  J2:"+str(_ns.score_p2)+"  Ganador: J1"
        fc=(1.0,0.55,0.55)
    elif _ns.score_p2 > _ns.score_p1:
        fin="Puntaje final  J1:"+str(_ns.score_p1)+"  J2:"+str(_ns.score_p2)+"  Ganador: J2"
        fc=(0.55,0.75,1.0)
    else:
        fin="Puntaje final  J1:"+str(_ns.score_p1)+"  J2:"+str(_ns.score_p2)+"  Empate!"
        fc=(0.95,0.85,0.20)
    txt(cx-270,h-82,fin,GLUT_BITMAP_HELVETICA_12,fc)
    panel(cx-210,18,420,32,0,0,0,0.78)
    txt(cx-195,26,"Presiona cualquier tecla para volver al lobby",
        GLUT_BITMAP_HELVETICA_12,(0.65,0.65,0.65))
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()


def display_maestro():
    global estado_nivel
    if _winner_active:
        _draw_winner_overlay()
        glutSwapBuffers()
        return
    if estado_nivel > 0:
        mod = MODULOS_NIVELES[estado_nivel]
        draw_p1, draw_p2 = _get_draw_fns()
        mod.display_sin_swap(draw_p1, draw_p2)
        if _confirmando_salida:
            _draw_confirm_exit()
        glutSwapBuffers()
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
    global _lob_target, _confirmando_salida

    # ── Winner: cualquier tecla vuelve al lobby ───────────────
    if _winner_active:
        _hide_winner()
        estado_nivel = 0
        arcade_init()
        glutPostRedisplay()
        return
    # ── ESC: siempre tiene prioridad maxima ───────────────────
    if key == b'\x1b':
        if _confirmando_salida:
            # ESC cancela el dialogo de salida
            _confirmando_salida = False
            glutPostRedisplay()
            return
        if estado_nivel > 0:
            _confirmando_salida = True
            glutPostRedisplay()
            return
        if estado_juego == -1:
            if _lobby_fase == 0:
                sys.exit(0)
            elif _lobby_fase in (1, 4):
                _lobby_fase = 0
            elif _lobby_fase == '1b':
                _lobby_fase = 1
            elif _lobby_fase == 2:
                _lobby_fase = 1
            elif _lobby_fase == '2b':
                _lobby_fase = 2
            glutPostRedisplay()
            return
        # en modo personaje individual -> parar audio y volver al lobby
        try:
            mod = MODULOS_PERSONAJES[estado_juego]
            if hasattr(mod, 'stop_audio'):
                mod.stop_audio()
        except Exception:
            pass
        _reset_all_expressions()
        estado_juego = -1
        lobby_audio.play_lobby()   # restaurar música del lobby
        arcade_init()
        glutPostRedisplay()
        return

    # ── Dialogo de confirmacion activo: solo S/ENTER aceptan ─
    if _confirmando_salida:
        if key in (b's', b'S', b'y', b'Y', b'\r', b'\n'):
            from niveles import state as ns
            ns.score_p1=0; ns.score_p2=0
            ns.nivel_score_p1=0; ns.nivel_score_p2=0
            _confirmando_salida = False
            estado_nivel = 0
            lobby_audio.stop_nivel()
            lobby_audio.play_lobby()
            arcade_init()
        else:
            _confirmando_salida = False
        glutPostRedisplay()
        return

    # ── Dentro de un nivel: delegar al nivel (sin ENTER libre) ─
    if estado_nivel > 0:
        # ENTER no debe llegar al nivel (evita salidas accidentales)
        if key not in (b'\r', b'\n'):
            MODULOS_NIVELES[estado_nivel].keyboard(key, x, y)
        return

    # ── Lobby ─────────────────────────────────────────────────
    if estado_juego == -1:
        # Bloquear input durante animacion de seleccion
        if _lobby_fase == 0:
            _lobby_fase = 1
            glutPostRedisplay()
            return

        elif _lobby_fase == 1:
            # J1 navega con flechas (special_maestro), ENTER pide confirmacion
            if key in (b'\r', b'\n'):
                _lobby_fase = '1b'
                _lob_target = selected_p1 * SPACING
                _lob_offset = _lob_target
            glutPostRedisplay()
            return

        elif _lobby_fase == '1b':
            # J1 confirma con S o rechaza con N
            if key in (b's', b'S'):
                _set_happy_expression(selected_p1)
                # Pasar a J2: centrar carrusel en selected_p2
                _lobby_fase = 2
                _lob_target = selected_p2 * SPACING
                _lob_offset = _lob_target
            elif key in (b'n', b'N'):
                _lobby_fase = 1
            glutPostRedisplay()
            return

        elif _lobby_fase == 2:
            # J2 navega con A/D, ESPACIO pide confirmacion
            if key == b' ':
                _lobby_fase = '2b'
                _lob_target = selected_p2 * SPACING
                _lob_offset = _lob_target
            elif key in (b'a', b'A'):
                new = selected_p2 - 1
                if new >= 0:
                    selected_p2 = new; _lob_target = selected_p2 * SPACING
            elif key in (b'd', b'D'):
                new = selected_p2 + 1
                if new < N:
                    selected_p2 = new; _lob_target = selected_p2 * SPACING
            glutPostRedisplay()
            return

        elif _lobby_fase == '2b':
            # J2 confirma con S o rechaza con N
            if key in (b's', b'S'):
                _set_happy_expression(selected_p2)
                from niveles import state as ns
                ns.score_p1=0; ns.score_p2=0
                _activate_nivel(1)
            elif key in (b'n', b'N'):
                _lobby_fase = 2
            glutPostRedisplay()
            return

        elif _lobby_fase == 4:
            if key in (b'\r', b'\n'):
                _set_happy_expression(selected_ind)
                _activate_character(selected_ind)
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
    global selected_p1, selected_ind, _lob_target, _lobby_fase, estado_nivel
    try:
        if _winner_active:
            _hide_winner()
            estado_nivel = 0
            arcade_init()
            glutPostRedisplay()
            return
        if estado_nivel > 0:
            MODULOS_NIVELES[estado_nivel].special_keys(key, x, y)
            return
        if estado_juego == -1:
            if _lobby_fase == 1:
                if key == GLUT_KEY_LEFT:
                    new = selected_p1 - 1
                    if new >= 0:
                        selected_p1 = new; _lob_target = selected_p1 * SPACING
                elif key == GLUT_KEY_RIGHT:
                    new = selected_p1 + 1
                    if new < N:
                        selected_p1 = new; _lob_target = selected_p1 * SPACING
                glutPostRedisplay()
            elif _lobby_fase == 4:
                if key == GLUT_KEY_LEFT:
                    new = selected_ind - 1
                    if new >= 0:
                        selected_ind = new; _lob_target = selected_ind * SPACING
                elif key == GLUT_KEY_RIGHT:
                    new = selected_ind + 1
                    if new < N:
                        selected_ind = new; _lob_target = selected_ind * SPACING
                glutPostRedisplay()
            elif _lobby_fase in (0, 3):
                if key == GLUT_KEY_F1:
                    _lobby_fase = 4
                    _lob_target = selected_ind * SPACING
                    glutPostRedisplay()
            # En fases 0,2,3 las flechas NO hacen nada (evitar crashes)
        else:
            if hasattr(MODULOS_PERSONAJES[estado_juego], 'special_keys'):
                MODULOS_PERSONAJES[estado_juego].special_keys(key, x, y)
    except Exception as e:
        print(f"[special_maestro] {e}")


def special_up_maestro(key, x, y):
    try:
        if estado_nivel > 0:
            mod = MODULOS_NIVELES[estado_nivel]
            if hasattr(mod, 'special_keys_up'):
                mod.special_keys_up(key, x, y)
    except Exception as e:
        print(f"[special_up] {e}")


def mouse_maestro(button, state_btn, x, y):
    global _mouse_down, _mouse_last_x, _drag_accum
    try:
        if estado_nivel > 0:
            return
        # Bloquear mouse durante animaciones de seleccion y winner
        if _winner_active:
            return
        if estado_juego == -1:
            if button == GLUT_LEFT_BUTTON:
                _mouse_down   = (state_btn == GLUT_DOWN)
                _mouse_last_x = x
                _drag_accum   = 0
            elif button == 3 and state_btn == GLUT_DOWN:
                # Scroll: solo navegar en fases donde tiene sentido
                if _lobby_fase in (1, 4):
                    _navigate(-1)
            elif button == 4 and state_btn == GLUT_DOWN:
                if _lobby_fase in (1, 4):
                    _navigate(1)
        else:
            if hasattr(MODULOS_PERSONAJES[estado_juego], 'mouse'):
                MODULOS_PERSONAJES[estado_juego].mouse(button, state_btn, x, y)
    except Exception as e:
        print(f"[mouse_maestro] {e}")


def motion_maestro(x, y):
    global _mouse_last_x, _drag_accum
    try:
        if estado_nivel > 0:
            return
        # Bloquear drag durante animaciones y fases no navegables
        if _winner_active:
            return
        if estado_juego == -1:
            if _mouse_down and _lobby_fase in (1, 4):
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
                # Actualizar posicion pero sin navegar
                _mouse_last_x = x
        else:
            if hasattr(MODULOS_PERSONAJES[estado_juego], 'motion'):
                MODULOS_PERSONAJES[estado_juego].motion(x, y)
    except Exception as e:
        print(f"[motion_maestro] {e}")


def timer_maestro(value):
    global estado_nivel, _winner_spin, _lobby_fase, _lob_target, _lob_offset
    if _winner_active:
        _winner_spin = (_winner_spin + 1.8) % 360
        glutPostRedisplay()
        glutTimerFunc(16, timer_maestro, 0)
        return
    if estado_nivel > 0:
        MODULOS_NIVELES[estado_nivel].update(value)
        # Transicion automatica al siguiente nivel cuando resultado_timer llega a 0
        from niveles import state as ns
        if ns.mostrar_resultado and ns.resultado_timer == 0:
            siguiente = estado_nivel + 1
            if siguiente <= 3:
                # Avanzar al siguiente nivel directamente
                estado_nivel = siguiente
                mod = MODULOS_NIVELES[siguiente]
                if not _nivel_initialized[siguiente]:
                    try: mod.init()
                    except Exception as e: print(f"[timer] init nivel {siguiente}: {e}")
                    _nivel_initialized[siguiente] = True
                else:
                    try: mod.reset()
                    except Exception as e: print(f"[timer] reset nivel {siguiente}: {e}")
                lobby_audio.stop_nivel()
                lobby_audio.play_nivel(siguiente)
                ns.mostrar_resultado = False
            else:
                # Nivel 3 terminado: mostrar pantalla de ganador final
                ganador_idx = (nivel_state.personaje_idx
                               if ns.nivel_ganador == 1
                               else nivel_state.personaje_idx_p2)
                _reset_all_expressions()
                _show_winner(ns.nivel_ganador, ganador_idx)
                ns.mostrar_resultado = False
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
    lobby_audio.init()
    lobby_audio.play_lobby()
    lobby_audio.init()
    lobby_audio.play_lobby()
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