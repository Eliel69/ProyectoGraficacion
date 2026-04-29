# totoro/actions/update.py
# CORRECCIÓN: Se separó la lógica pura (_logic) del re-registro del timer.
from OpenGL.GLUT import *
from totoro.actions import state
import math

def enforce_scene_bounds():
    x_min, x_max = state.scene_bounds["x"]
    z_min, z_max = state.scene_bounds["z"]
    state.char_x = max(x_min, min(x_max, state.char_x))
    state.char_z = max(z_min, min(z_max, state.char_z))

def _logic():
    """Lógica pura, sin re-registrar el timer (usada por el arcade)."""
    if state.walking:
        state.animation_angle += 0.2
        state.leg_angle  = math.sin(state.animation_angle) * 25
        state.arm_angle  = -math.sin(state.animation_angle) * 20
        state.blink_timer += 0.05
    else:
        state.leg_angle *= 0.9
        state.arm_angle *= 0.9

    if state.reaction_type:
        state.reaction_timer += 1

        if state.reaction_type == "jump":
            state.jump_offset = abs(math.sin(state.reaction_timer * 0.2)) * 2.0
        elif state.reaction_type == "spin":
            state.spin_angle += 15
        elif state.reaction_type == "shake":
            state.shake_offset = math.sin(state.reaction_timer * 0.8) * 0.5
        elif state.reaction_type == "arms_up":
            state.arm_angle = 60
        elif state.reaction_type == "legs_move":
            state.leg_angle = math.sin(state.reaction_timer * 0.5) * 35

        if state.reaction_timer >= state.reaction_duration:
            state.reaction_type  = None
            state.reaction_timer = 0
            state.jump_offset    = 0.0
            state.shake_offset   = 0.0
            state.spin_angle     = 0.0

    enforce_scene_bounds()

def update(value):
    """Wrapper para modo standalone: lógica + re-registro del timer."""
    _logic()
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)
