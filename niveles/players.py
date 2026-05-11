# niveles/players.py
# ─────────────────────────────────────────────────────────────
# Actualiza la posición y animación de ambos jugadores.
# Llamado cada frame desde el update() de cada nivel.
# ─────────────────────────────────────────────────────────────
import math
from niveles import state

# Límites del área de juego (igual para los tres niveles)
_BOUND = 14.0


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def update():
    """Mueve J1 y J2 según las teclas activas en state."""

    # ── Jugador 1 (WASD) ─────────────────────────────────────
    dx1, dz1 = 0.0, 0.0
    if state.k_w: dz1 -= 1.0
    if state.k_s: dz1 += 1.0
    if state.k_a: dx1 -= 1.0
    if state.k_d: dx1 += 1.0

    moving1 = (dx1 != 0.0 or dz1 != 0.0)
    if moving1:
        length = math.sqrt(dx1 * dx1 + dz1 * dz1)
        state.p1_x += (dx1 / length) * state.p1_speed
        state.p1_z += (dz1 / length) * state.p1_speed
        state.p1_x  = _clamp(state.p1_x, -_BOUND, _BOUND)
        state.p1_z  = _clamp(state.p1_z, -_BOUND, _BOUND)
        # Orientar el personaje en la dirección de movimiento
        state.p1_rot = math.degrees(math.atan2(dx1, -dz1))

    state.p1_walking = moving1
    if moving1:
        state.p1_anim += 0.25
    else:
        state.p1_anim *= 0.8   # suaviza la parada

    # ── Jugador 2 (Flechas) ───────────────────────────────────
    dx2, dz2 = 0.0, 0.0
    if state.k_up:    dz2 -= 1.0
    if state.k_down:  dz2 += 1.0
    if state.k_left:  dx2 -= 1.0
    if state.k_right: dx2 += 1.0

    moving2 = (dx2 != 0.0 or dz2 != 0.0)
    if moving2:
        length = math.sqrt(dx2 * dx2 + dz2 * dz2)
        state.p2_x += (dx2 / length) * state.p2_speed
        state.p2_z += (dz2 / length) * state.p2_speed
        state.p2_x  = _clamp(state.p2_x, -_BOUND, _BOUND)
        state.p2_z  = _clamp(state.p2_z, -_BOUND, _BOUND)
        state.p2_rot = math.degrees(math.atan2(dx2, -dz2))

    state.p2_walking = moving2
    if moving2:
        state.p2_anim += 0.25
    else:
        state.p2_anim *= 0.8


def draw_players(draw_p1_fn, draw_p2_fn):
    """
    Dibuja ambos jugadores en sus posiciones actuales.

    draw_p1_fn / draw_p2_fn : funciones sin argumentos que renderizan
    el modelo 3D centrado en el origen (p. ej. draw_amongus_full).
    El posicionado y la rotación se aplican aquí con glTranslate/Rotate.
    """
    from OpenGL.GL import (glPushMatrix, glPopMatrix,
                           glTranslatef, glRotatef)

    # Jugador 1
    glPushMatrix()
    glTranslatef(state.p1_x, 0.0, state.p1_z)
    glRotatef(state.p1_rot, 0, 1, 0)
    draw_p1_fn()
    glPopMatrix()

    # Jugador 2
    glPushMatrix()
    glTranslatef(state.p2_x, 0.0, state.p2_z)
    glRotatef(state.p2_rot, 0, 1, 0)
    draw_p2_fn()
    glPopMatrix()
