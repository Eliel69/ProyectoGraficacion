# beru/actions/update.py
# CORRECCIONES: Todos los imports rotos corregidos a rutas de paquete completo.
# - 'import actions.state as state'           → from beru.actions import state
# - 'from resources.sound_manager import play' → from beru.resources import sound_manager

import math
from beru.actions import state                      # CORREGIDO

_MOVE_SPEED    = 0.055
_ROT_SPEED     = 4.0
_JUMP_SPEED    = 0.12
_SPIN_SPEED    = 10.0
_GREET_SPEED   = 12.0
_ARM_SPEED     = 3.0
_EXPR_DURATION = 120

def tick():
    _update_expression()
    _update_movement()
    _update_hud()

def _update_expression():
    if state.expression_timer > 0:
        state.expression_timer -= 1
        if state.expression_timer == 0:
            state.expression = 'neutral'

def set_expression(name):
    from beru.resources import sound_manager          # CORREGIDO

    state.expression = name
    state.expression_timer = _EXPR_DURATION

    sound_map = {
        'smile' : 'beru_feliz',
        'sad'   : 'beru_triste',
        'angry' : 'beru_enojado',
        'fear'  : 'beru_miedo',
        'doubt' : 'beru_sorpresa',
        'admire': 'beru_sorpresa',
        'wink'  : 'beru_feliz',
    }
    snd = sound_map.get(name)
    if snd:
        sound_manager.play(snd)

def _update_movement():
    moving = False

    if state.move_left:
        state.rotation_y += _ROT_SPEED
        moving = True

    if state.move_right:
        state.rotation_y -= _ROT_SPEED
        moving = True

    rad = math.radians(state.rotation_y)

    if state.move_forward:
        state.pos_x += math.sin(rad) * _MOVE_SPEED
        state.pos_z += math.cos(rad) * _MOVE_SPEED
        moving = True

    if state.move_backward:
        state.pos_x -= math.sin(rad) * _MOVE_SPEED
        state.pos_z -= math.cos(rad) * _MOVE_SPEED
        moving = True

    if state.movement not in ('jump', 'greet', 'spin', 'arms_up', 'arms_down'):
        state.movement = 'walk' if moving else 'idle'

    if state.movement == 'walk':
        state.walk_cycle += 8.0
        state.pos_y  = math.sin(math.radians(state.walk_cycle)) * 0.025
        state.scale  = 1.0
        state.arm_angle = math.sin(math.radians(state.walk_cycle)) * 8.0

    elif state.movement == 'idle':
        state.pos_y = 0.0
        state.scale = 1.0
        state.arm_angle *= 0.80
        if abs(state.arm_angle) < 0.2:
            state.arm_angle = 0.0

    elif state.movement == 'jump':
        state.jump_phase += _JUMP_SPEED
        state.pos_y = max(0.0, math.sin(state.jump_phase) * 1.2)
        if state.jump_phase >= math.pi:
            state.pos_y = 0.0
            state.jump_phase = 0.0
            state.movement = 'idle'

    elif state.movement == 'greet':
        state.greet_phase += _GREET_SPEED
        state.arm_angle = 28.0 + 18.0 * math.sin(math.radians(state.greet_phase))
        if state.move_timer > 0:
            state.move_timer -= 1
        else:
            state.arm_angle  = 0.0
            state.greet_phase = 0.0
            state.movement   = 'idle'

    elif state.movement == 'spin':
        state.spin_angle  += _SPIN_SPEED
        state.rotation_y  += _SPIN_SPEED
        if state.move_timer > 0:
            state.move_timer -= 1
        else:
            state.spin_angle = 0.0
            state.movement   = 'idle'

    elif state.movement == 'arms_up':
        state.arm_angle += _ARM_SPEED
        if state.arm_angle >= 40.0:
            state.movement = 'idle'

    elif state.movement == 'arms_down':
        state.arm_angle -= _ARM_SPEED
        if state.arm_angle <= 0.0:
            state.arm_angle = 0.0
            state.movement  = 'idle'

def set_movement(name, duration=60):
    from beru.resources import sound_manager          # CORREGIDO

    state.movement   = name
    state.move_timer = duration

    sound_map = {
        'jump'     : 'beru_saltar',
        'greet'    : 'beru_saludar',
        'spin'     : 'beru_girar',
        'arms_up'  : None,
        'arms_down': None,
    }
    snd = sound_map.get(name)
    if snd:
        sound_manager.play(snd)

def _update_hud():
    if getattr(state, 'hud_timer', 0) > 0:
        state.hud_timer -= 1
        if state.hud_timer == 0:
            state.hud_msg = ""

def set_hud(msg, duration=90):
    state.hud_msg   = msg
    state.hud_timer = duration
