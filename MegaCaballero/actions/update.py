# MegaCaballero/actions/update.py
# CORRECCIÓN: Se separó la lógica pura (_logic) del re-registro del timer.
from OpenGL.GLUT import *
from MegaCaballero.actions import state
from MegaCaballero.utilerias.sonidos import audio_manager
import math

def _logic():
    """Lógica pura, sin re-registrar el timer (usada por el arcade)."""

    # 1. CAMINAR
    if state.is_walking:
        state.walk_angle += 2.0 * state.walk_dir
        if state.walk_angle > 30.0 or state.walk_angle < -30.0:
            state.walk_dir *= -1
    else:
        if state.walk_angle > 0: state.walk_angle -= 1.0
        elif state.walk_angle < 0: state.walk_angle += 1.0

    # 2. SALTAR
    if state.is_jumping:
        state.jump_y += state.jump_velocity
        state.jump_velocity -= 0.015
        if state.jump_y <= 0.0:
            state.jump_y = 0.0
            state.is_jumping = False

    # 3. SALUDAR (Hi)
    if state.is_waving:
        state.wave_angle += 4.0 * state.wave_dir
        if state.wave_angle > 40.0 or state.wave_angle < -20.0:
            state.wave_dir *= -1

    # 4. CELEBRACIÓN
    if state.is_celebrating:
        state.celebrate_angle += 4.0 * state.celebrate_dir
        if state.celebrate_angle > 60.0:
            state.celebrate_dir = -1
        elif state.celebrate_angle <= 0.0:
            state.celebrate_angle = 0.0
            state.celebrate_dir = 1
            state.celebrate_cycles += 1
            if state.celebrate_cycles >= 2:
                state.is_celebrating = False
                state.celebrate_cycles = 0
    else:
        if state.celebrate_angle > 0:
            state.celebrate_angle -= 4.0
            if state.celebrate_angle < 0: state.celebrate_angle = 0.0

    # 5. GIRAR (Spin)
    if state.is_spinning:
        state.spin_angle += 10.0
        if state.spin_angle >= 360.0:
            state.spin_angle = 0.0
            state.is_spinning = False

    # 6. AGACHARSE (Bend)
    if state.is_crouching:
        state.crouch_y += 0.02 * state.crouch_dir
        if state.crouch_y < -0.4:
            state.crouch_dir = 1.0
        elif state.crouch_y >= 0.0 and state.crouch_dir == 1.0:
            state.crouch_y = 0.0
            state.crouch_dir = -1.0
            state.is_crouching = False

    # 7. MEGA JUMP (Smash)
    if state.is_smashing:
        if state.smash_phase == 0:
            state.smash_y += 0.05
            state.smash_arm_angle += 5.0
            if state.smash_y >= 1.5:
                state.smash_phase = 1
        elif state.smash_phase == 1:
            state.smash_y -= 0.15
            state.smash_arm_angle -= 15.0
            if state.smash_y <= 0.0:
                state.smash_y = 0.0
                state.smash_arm_angle = -45.0
                state.smash_phase = 2
        elif state.smash_phase == 2:
            state.smash_arm_angle += 2.0
            if state.smash_arm_angle >= 0.0:
                state.smash_arm_angle = 0.0
                state.is_smashing = False
                state.smash_phase = 0

    # Colisiones
    dist_chest   = math.sqrt((state.fox_x - 2.0)**2   + (state.fox_z - (-1.5))**2)
    dist_crystal = math.sqrt((state.fox_x - (-2.5))**2 + (state.fox_z - (-2.0))**2)
    dist_log     = math.sqrt((state.fox_x - (-2.5))**2 + (state.fox_z - 2.0)**2)

    umbral_normal = 1.6
    umbral_log    = 2.0

    if dist_chest < umbral_normal and state.last_collision != 'chest':
        state.last_collision = 'chest'
        state.expression = 3
        state.is_celebrating = True
        state.celebrate_cycles = 0
        audio_manager.play_sound(audio_manager.sound_celebration)
    elif dist_crystal < umbral_normal and state.last_collision != 'crystal':
        state.last_collision = 'crystal'
        state.expression = 7
        state.is_smashing = True
        state.smash_phase = 0
        audio_manager.play_sound(audio_manager.sound_megajump)
    elif dist_log < umbral_log and state.last_collision != 'log':
        state.last_collision = 'log'
        state.expression = 1
        state.is_crouching = True
        audio_manager.play_sound(audio_manager.exp_sad)
    elif dist_chest >= umbral_normal and dist_crystal >= umbral_normal and dist_log >= umbral_log:
        if state.last_collision is not None:
            state.last_collision = None
            state.expression = 0

def update(value):
    """Wrapper para modo standalone: lógica + re-registro del timer."""
    _logic()
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)
