# ============================================================
# niveles/players.py
# ------------------------------------------------------------
# LOGICA DE MOVIMIENTO Y DIBUJO DE AVATARES
#
# Responsabilidades:
#   1. Leer banderas de teclado de state.py y mover p1/p2.
#   2. Normalizar el vector de movimiento (evita velocidad
#      doble en diagonal).
#   3. Calcular la rotacion del personaje con atan2.
#   4. Confinar a los jugadores dentro del perimetro _BOUND.
#   5. Dibujar disco de color + personaje escalado + bolita ID.
#
# Pregunta tipica:
#   "?Por que normalizan el vector de movimiento?"
#   Si el jugador presiona W+D (diagonal), dx=1 dz=1, la
#   magnitud del vector seria sqrt(2) ~ 1.41, haciendo que
#   la velocidad diagonal sea 41% mayor. Dividir por la
#   magnitud lo lleva de vuelta a 1.0.
# ============================================================
import math
from OpenGL.GL  import *
from OpenGL.GLU import *
from niveles    import state

# Limite del area de juego (mismo en los 3 niveles)
_BOUND = 14.0


def _clamp(v, lo, hi):
    """Restringe v al rango [lo, hi]. Evita que los avatares salgan del mapa."""
    return max(lo, min(hi, v))


def update():
    """
    Actualiza posicion y estado de animacion de ambos jugadores.
    Se llama una vez por frame desde update() de cada nivel.
    """
    # ── Jugador 1: WASD ───────────────────────────────────────
    dx1, dz1 = 0.0, 0.0
    if state.k_w: dz1 -= 1.0   # W = hacia adelante (Z negativo)
    if state.k_s: dz1 += 1.0   # S = hacia atras
    if state.k_a: dx1 -= 1.0   # A = izquierda
    if state.k_d: dx1 += 1.0   # D = derecha
    moving1 = (dx1 != 0.0 or dz1 != 0.0)
    if moving1:
        # Normalizacion: divide por magnitud para velocidad constante
        l = math.sqrt(dx1*dx1 + dz1*dz1)
        state.p1_x = _clamp(state.p1_x + (dx1/l)*state.p1_speed, -_BOUND, _BOUND)
        state.p1_z = _clamp(state.p1_z + (dz1/l)*state.p1_speed, -_BOUND, _BOUND)
        # atan2(dx, -dz) convierte el vector de movimiento a angulo de rotacion
        state.p1_rot = math.degrees(math.atan2(dx1, -dz1))
    # Safety: si no hay tecla activa, forzar parada (evita inercias de foco perdido)
    state.p1_walking = moving1 and (state.k_w or state.k_s or state.k_a or state.k_d)
    state.p1_anim = (state.p1_anim + 0.25) if state.p1_walking else state.p1_anim * 0.8

    # ── Jugador 2: Flechas ────────────────────────────────────
    dx2, dz2 = 0.0, 0.0
    if state.k_up:    dz2 -= 1.0
    if state.k_down:  dz2 += 1.0
    if state.k_left:  dx2 -= 1.0
    if state.k_right: dx2 += 1.0
    moving2 = (dx2 != 0.0 or dz2 != 0.0)
    if moving2:
        l = math.sqrt(dx2*dx2 + dz2*dz2)
        state.p2_x = _clamp(state.p2_x + (dx2/l)*state.p2_speed, -_BOUND, _BOUND)
        state.p2_z = _clamp(state.p2_z + (dz2/l)*state.p2_speed, -_BOUND, _BOUND)
        state.p2_rot = math.degrees(math.atan2(dx2, -dz2))
    state.p2_walking = moving2 and (state.k_up or state.k_down or state.k_left or state.k_right)
    state.p2_anim = (state.p2_anim + 0.25) if state.p2_walking else state.p2_anim * 0.8


# Escala y offset Y por personaje para que queden proporcionados en el nivel
# 0=FallGuy 1=AmongUs 2=Beru 3=Gato 4=MegaCaballero 5=Totoro
# Totoro (0.13) es tan pequeno porque su modelo usa radio 4-5 unidades mundo
_NIVEL_SCALE = [0.55, 0.55, 0.55, 0.55, 0.55, 0.13]
# MegaCaballero (0.55) tiene un offset Y porque internamente sus piernas
# estan en Y negativo, lo que lo hunde en el suelo
_NIVEL_Y_OFF = [0.0,  0.0,  0.0,  0.0,  0.55, 0.0 ]


def _draw_disc_under(r, g, b, radius=0.8, alpha=0.75):
    """
    Disco de color semitransparente en el suelo bajo el avatar.
    Identifica visualmente a cada jugador: ROJO=J1, AZUL=J2.
    Se dibuja con TRIANGLE_FAN desde el centro hacia el borde.
    """
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(r, g, b, alpha)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, 0.02, 0.0)   # centro (Y=0.02 para no z-fight con el suelo)
    for i in range(21):
        a = 2 * math.pi * i / 20
        glVertex3f(math.cos(a)*radius, 0.02, math.sin(a)*radius)
    glEnd()
    glDisable(GL_BLEND); glEnable(GL_LIGHTING)


def _draw_label_dot(r, g, b):
    """
    Pequeña esfera sobre la cabeza del avatar para identificarlo
    cuando los dos personajes son el mismo modelo 3D.
    """
    glDisable(GL_LIGHTING)
    glColor3f(r, g, b)
    q = gluNewQuadric()
    glPushMatrix()
    glTranslatef(0.0, 2.8, 0.0)
    gluSphere(q, 0.18, 10, 10)
    glPopMatrix()
    gluDeleteQuadric(q)
    glEnable(GL_LIGHTING)


def draw_players(draw_p1_fn, draw_p2_fn):
    """
    Dibuja ambos jugadores en sus posiciones actuales.

    draw_p1_fn / draw_p2_fn: funciones de dibujo del modelo 3D
    de cada personaje, obtenidas desde _get_draw_fns() en main_arcade.

    Flujo por jugador:
      1. Trasladar al origen del avatar (p_x, 0, p_z)
      2. Rotar hacia la direccion de movimiento
      3. Dibujar disco de color en el suelo
      4. Escalar y elevar el modelo 3D
      5. Dibujar bolita identificadora sobre la cabeza
    """
    idx1 = getattr(state, 'personaje_idx',    0)
    idx2 = getattr(state, 'personaje_idx_p2', 1)

    def _draw_one(px, pz, rot, fn, idx, disc_r, disc_g, disc_b):
        sc   = _NIVEL_SCALE[idx] if 0 <= idx < len(_NIVEL_SCALE) else 0.55
        yoff = _NIVEL_Y_OFF[idx] if 0 <= idx < len(_NIVEL_Y_OFF) else 0.0
        glPushMatrix()
        glTranslatef(px, 0.0, pz)
        glRotatef(rot, 0, 1, 0)
        _draw_disc_under(disc_r, disc_g, disc_b)
        glPushMatrix()
        glTranslatef(0.0, yoff, 0.0)
        glScalef(sc, sc, sc)
        fn()    # llamar la funcion de dibujo del personaje elegido
        glPopMatrix()
        _draw_label_dot(disc_r, disc_g, disc_b)
        glPopMatrix()

    _draw_one(state.p1_x, state.p1_z, state.p1_rot, draw_p1_fn, idx1, 0.90, 0.12, 0.12)  # ROJO J1
    _draw_one(state.p2_x, state.p2_z, state.p2_rot, draw_p2_fn, idx2, 0.15, 0.35, 0.95)  # AZUL J2
