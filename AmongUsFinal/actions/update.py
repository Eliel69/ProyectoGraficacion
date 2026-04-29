# AmongUsFinal/actions/update.py
# CORRECCIÓN: Se separó la lógica pura (_logic) del re-registro del timer.
from OpenGL.GLUT import *
from AmongUsFinal.actions import state
from AmongUsFinal.utilerias.sonidos import audio_manager

def _logic():
    """Lógica pura, sin re-registrar el timer (usada por el arcade)."""
    if state.walking:
        state.animation_angle += 0.2
    else:
        state.animation_angle = 0.0

    if state.shaking:
        state.shake_timer += 1.0
    else:
        state.shake_timer = 0.0

    if state.reaction_type:
        state.reaction_timer += 1
        if state.reaction_timer >= state.reaction_duration:
            state.reaction_type  = None
            state.reaction_timer = 0

    if state.key_up:    state.fox_z -= state.fox_speed
    if state.key_down:  state.fox_z += state.fox_speed
    if state.key_left:  state.fox_x -= state.fox_speed
    if state.key_right: state.fox_x += state.fox_speed

def update(value):
    """Wrapper para modo standalone: lógica + re-registro del timer."""
    _logic()
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)
