# ============================================================
# niveles/camera.py
# ------------------------------------------------------------
# CAMARA COMPARTIDA DINAMICA
# Resuelve el problema de mantener a DOS jugadores visibles
# en la misma pantalla sin usar pantalla dividida (split-screen).
#
# Algoritmo:
#   1. Calcula el PUNTO MEDIO entre los dos avatares.
#   2. Mide la DISTANCIA de separacion entre ellos.
#   3. A mayor distancia -> mayor altura y retroceso (zoom out).
#   4. Aplica gluLookAt apuntando siempre al punto medio.
#

import math
from OpenGL.GL  import *
from OpenGL.GLU import *
from niveles    import state

# Parametros de la camara (ajustados para el rango _BOUND=14)
_BASE_HEIGHT  = 12.0   # altura minima cuando los jugadores estan juntos
_BASE_BACK    = 8.0    # retroceso minimo de la camara
_SPREAD_FACTOR = 0.6   # cuanto sube la camara por cada unidad de separacion
_FOV          = 50.0   # campo de vision en grados (perspectiva humana ~50-60)


def apply(win_w, win_h):
    """
    Configura la proyeccion y la vista antes de dibujar la escena 3D.
    Debe llamarse al inicio de cada display(), ANTES de dibujar objetos.

    Parametros:
        win_w, win_h : dimensiones actuales de la ventana (para el aspect ratio)
    """
    # 1. Punto medio entre los dos jugadores
    mid_x = (state.p1_x + state.p2_x) / 2.0
    mid_z = (state.p1_z + state.p2_z) / 2.0

    # 2. Distancia euclidiana de separacion en el plano XZ
    dx   = state.p2_x - state.p1_x
    dz   = state.p2_z - state.p1_z
    dist = math.sqrt(dx * dx + dz * dz)

    # 3. Zoom dinamico: la camara se aleja proporcionalmente
    height = _BASE_HEIGHT  + dist * _SPREAD_FACTOR
    back   = _BASE_BACK    + dist * _SPREAD_FACTOR * 0.5

    # 4. Proyeccion perspectiva (simula ojo humano con FOV 50 grados)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = win_w / max(win_h, 1)   # evitar division por cero en resize
    gluPerspective(_FOV, aspect, 0.1, 200.0)
    # 0.1 = plano cercano (near), 200.0 = plano lejano (far)
    # Objetos fuera de [0.1, 200.0] se recortan (clipping)

    # 5. Vista: ojo encima y detras del punto medio, mirando hacia el
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
        mid_x, height, mid_z + back,  # posicion del ojo
        mid_x, 0.0,    mid_z,          # punto al que mira (centro del mapa)
        0.0,   1.0,    0.0             # vector "arriba" del mundo
    )
