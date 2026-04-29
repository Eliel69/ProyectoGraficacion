# ============================================================
#  ARCADE SELECTOR MAESTRO  —  Lobby 3D
#  Instrucciones de navegación:
#    Flechas ← →  o  arrastrar mouse  :  cambiar personaje
#    Scroll del mouse                 :  cambiar personaje
#    ENTER o teclas 1-6              :  entrar al juego
#    ESC (en juego)                  :  volver al lobby
#    ESC (en lobby)                  :  salir
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
    {"scale": 1.0,  "y_off": 0.0 },   # 4  MegaCaballero
    {"scale": 0.7,  "y_off": 0.0 },   # 5  Totoro
]

# ════════════════════════════════════════════════════════════
# ESTADO GLOBAL
# ════════════════════════════════════════════════════════════
WIN_W, WIN_H = 960, 620
selected     = 0
estado_juego = -1          # -1 = lobby,  0..5 = personaje activo
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
        is_sel   = (i == selected)
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
        if is_sel:
            cr, cg, cb = CHARACTERS[i]["color"]
            _draw_disc(cr, cg, cb, radius=1.15, alpha=0.65)
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
def _draw_lobby_hud():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix(); glLoadIdentity()
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    ch = CHARACTERS[selected]
    cr, cg, cb = ch["color"]

    # ── Encabezado ────────────────────────────────────────────
    _txt(WIN_W//2 - 205, WIN_H - 30,
         "ARCADE 3D  —  Graficacion 2026",
         GLUT_BITMAP_HELVETICA_18, (0.95, 0.85, 0.20))
    _txt(WIN_W//2 - 172, WIN_H - 52,
         "Instituto Tecnologico de Toluca  |  Equipo",
         GLUT_BITMAP_HELVETICA_12, (0.65, 0.75, 0.95))

    # ── Info del personaje seleccionado (arriba al centro) ────
    lbl_w = len(ch["label"]) * 10
    _txt(WIN_W//2 - lbl_w//2, WIN_H - 96,
         ch["label"],
         GLUT_BITMAP_HELVETICA_18, (cr, cg, cb))
    _txt(WIN_W//2 - 70, WIN_H - 120,
         f"Autor: {ch['author']}",
         GLUT_BITMAP_HELVETICA_12, (0.88, 0.88, 0.75))
    for idx, line in enumerate(ch["desc"]):
        _txt(WIN_W//2 - 95, WIN_H - 142 - idx * 18,
             line, GLUT_BITMAP_HELVETICA_12, (0.75, 0.88, 0.98))

    # ── Puntos de selección (indicadores) ────────────────────
    dot_spacing = 20
    dot_start_x = WIN_W//2 - (N - 1) * dot_spacing // 2
    glDisable(GL_LIGHTING)
    for i in range(N):
        r2, g2, b2 = CHARACTERS[i]["color"]
        if i == selected:
            glPointSize(11)
            glColor3f(r2, g2, b2)
        else:
            glPointSize(5)
            glColor3f(0.42, 0.40, 0.52)
        glBegin(GL_POINTS)
        glVertex2f(dot_start_x + i * dot_spacing, 54)
        glEnd()
    glPointSize(1.0)

    # ── Controles en la barra inferior ───────────────────────
    # Fondo semitransparente
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 0.0, 0.55)
    glBegin(GL_QUADS)
    glVertex2f(0, 0); glVertex2f(WIN_W, 0)
    glVertex2f(WIN_W, 38); glVertex2f(0, 38)
    glEnd()
    glDisable(GL_BLEND)

    _txt(18, 14,
         "Flechas / Arrastrar mouse : navegar      "
         "ENTER o 1-6 : jugar      ESC : salir",
         GLUT_BITMAP_HELVETICA_12, (0.78, 0.78, 0.78))

    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()


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


def _navigate(delta):
    """Mueve la selección delta posiciones (con límites, sin wrap)."""
    global selected, _lob_target
    new_sel = selected + delta
    if 0 <= new_sel < N:
        selected = new_sel
        _lob_target = selected * SPACING
        glutPostRedisplay()


def _navigate_to(idx):
    """Salta directamente a un índice de personaje."""
    global selected, _lob_target
    selected = max(0, min(N - 1, idx))
    _lob_target = selected * SPACING
    glutPostRedisplay()


# ════════════════════════════════════════════════════════════
# CALLBACKS GLUT
# ════════════════════════════════════════════════════════════
def display_maestro():
    if estado_juego == -1:
        _draw_lobby_3d()
        _draw_lobby_hud()
        glutSwapBuffers()
    else:
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        MODULOS_PERSONAJES[estado_juego].display()


def keyboard_maestro(key, x, y):
    global estado_juego

    if key == b'\x1b':
        if estado_juego == -1:
            sys.exit(0)
        else:
            estado_juego = -1
            arcade_init()        # Restaurar GL para el lobby
            glutPostRedisplay()
        return

    if estado_juego == -1:
        if key in (b'\r', b'\n'):
            _activate_character(selected)
        elif b'1' <= key <= b'6':
            _navigate_to(int(key) - ord('1'))
    else:
        MODULOS_PERSONAJES[estado_juego].keyboard(key, x, y)


def special_maestro(key, x, y):
    if estado_juego == -1:
        if key == GLUT_KEY_LEFT:
            _navigate(-1)
        elif key == GLUT_KEY_RIGHT:
            _navigate(1)
    else:
        if hasattr(MODULOS_PERSONAJES[estado_juego], 'special_keys'):
            MODULOS_PERSONAJES[estado_juego].special_keys(key, x, y)


def mouse_maestro(button, state_btn, x, y):
    global _mouse_down, _mouse_last_x, _drag_accum

    if estado_juego == -1:
        if button == GLUT_LEFT_BUTTON:
            _mouse_down  = (state_btn == GLUT_DOWN)
            _mouse_last_x = x
            _drag_accum  = 0
        elif button == 3 and state_btn == GLUT_DOWN:   # scroll arriba
            _navigate(-1)
        elif button == 4 and state_btn == GLUT_DOWN:   # scroll abajo
            _navigate(1)
    else:
        if hasattr(MODULOS_PERSONAJES[estado_juego], 'mouse'):
            MODULOS_PERSONAJES[estado_juego].mouse(button, state_btn, x, y)


def motion_maestro(x, y):
    global _mouse_last_x, _drag_accum

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
    if estado_juego != -1:
        if hasattr(MODULOS_PERSONAJES[estado_juego], 'update'):
            MODULOS_PERSONAJES[estado_juego].update(value)
    glutPostRedisplay()
    glutTimerFunc(16, timer_maestro, 0)


def reshape_maestro(w, h):
    global WIN_W, WIN_H
    WIN_W, WIN_H = w, max(h, 1)
    if estado_juego != -1:
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
    glutSpecialFunc(special_maestro)
    glutMouseFunc(mouse_maestro)
    glutMotionFunc(motion_maestro)
    glutReshapeFunc(reshape_maestro)
    glutTimerFunc(16, timer_maestro, 0)
    glutMainLoop()


if __name__ == "__main__":
    main()