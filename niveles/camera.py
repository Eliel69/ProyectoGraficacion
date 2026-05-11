# niveles/camera.py
# ─────────────────────────────────────────────────────────────
# Cámara compartida para todos los niveles.
# Sigue el punto medio entre los dos jugadores y se aleja
# automáticamente cuando se separan.
# ─────────────────────────────────────────────────────────────
import math
from OpenGL.GL  import *
from OpenGL.GLU import *
from niveles    import state

# Parámetros ajustables
_BASE_HEIGHT  = 12.0   # altura base cuando los jugadores están juntos
_BASE_BACK    = 8.0    # retroceso base de la cámara detrás del centro
_SPREAD_FACTOR = 0.6   # cuánto se aleja la cámara según la separación
_FOV          = 50.0


def apply(win_w, win_h):
    """
    Llama a este método justo antes de dibujar la escena 3D del nivel.
    Calcula el punto medio entre ambos jugadores y posiciona la cámara
    por encima y detrás, mirando hacia ese centro.
    """
    # ── Centro entre los dos jugadores ───────────────────────
    mid_x = (state.p1_x + state.p2_x) / 2.0
    mid_z = (state.p1_z + state.p2_z) / 2.0

    # ── Distancia de separación → zoom out dinámico ──────────
    dx   = state.p2_x - state.p1_x
    dz   = state.p2_z - state.p1_z
    dist = math.sqrt(dx * dx + dz * dz)

    height = _BASE_HEIGHT  + dist * _SPREAD_FACTOR
    back   = _BASE_BACK    + dist * _SPREAD_FACTOR * 0.5

    # ── Configurar proyección ─────────────────────────────────
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = win_w / max(win_h, 1)
    gluPerspective(_FOV, aspect, 0.1, 200.0)

    # ── Aplicar vista ─────────────────────────────────────────
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    eye_x = mid_x
    eye_y = height
    eye_z = mid_z + back

    gluLookAt(
        eye_x, eye_y, eye_z,    # ojo: encima y detrás del centro
        mid_x, 0.0,   mid_z,    # objetivo: el centro a nivel del suelo
        0.0,   1.0,   0.0       # arriba
    )
