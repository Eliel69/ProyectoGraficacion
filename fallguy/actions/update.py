# fallguy/actions/update.py
# CORRECCIÓN: Se separó la lógica pura (_logic) del re-registro del timer.
# - _logic()      → sólo actualiza el estado (sin glutTimerFunc)
# - update(value) → lógica + re-registro del timer (para modo standalone)
# El arcade llama a _logic() a través del puente en main.py, evitando el doble timer.

from OpenGL.GLUT import *
from fallguy.actions import state
from fallguy.resources import sounds

def enforce_scene_bounds():
    x_min, x_max = state.scene_bounds["x"]
    z_min, z_max = state.scene_bounds["z"]
    state.guy_x = max(x_min, min(x_max, state.guy_x))
    state.guy_z = max(z_min, min(z_max, state.guy_z))

def _logic():
    """Lógica pura de actualización, sin re-registrar el timer."""
    # Animación de caminar
    if state.walking:
        state.animation_angle += 0.10
        state.blink_timer     += 0.03
        state.step_timer      += 1
        if state.step_timer >= 18:
            sounds.play("step")
            state.step_timer = 0
        # Movimiento continuo con teclas
        if state.key_up:    state.guy_z -= state.guy_speed
        if state.key_down:  state.guy_z += state.guy_speed
        if state.key_left:  state.guy_x -= state.guy_speed
        if state.key_right: state.guy_x += state.guy_speed
    else:
        state.blink_timer += 0.015

    # Idle bob siempre activo
    state.idle_bob += 0.05

    # Timer de reacciones
    if state.reaction_type in ("jump", "spin"):
        state.reaction_timer += 1
        if state.reaction_timer >= state.reaction_duration:
            state.reaction_type  = None
            state.reaction_timer = 0

    enforce_scene_bounds()

def update(value):
    """
    Wrapper para modo standalone: ejecuta la lógica y re-registra el timer.
    El arcade usa _logic() directamente a través del puente en main.py.
    """
    _logic()
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)
