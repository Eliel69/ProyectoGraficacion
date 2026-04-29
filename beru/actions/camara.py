import math
from OpenGL.GL import *
from OpenGL.GLU import *
from beru.actions import state    

_PITCH_MIN = -80.0
_PITCH_MAX = 80.0
_DIST_MIN  = 2.5
_DIST_MAX  = 20.0

def apply():
    glLoadIdentity()

    yaw_r   = math.radians(state.cam_yaw)
    pitch_r = math.radians(state.cam_pitch)

    # cámara normal/orbital
    if state.cam_mode == 'normal':
        target_x = state.pos_x + state.cam_pan_x
        target_y = state.cam_pan_y
        target_z = state.pos_z

        eye_x = target_x + state.cam_distance * math.sin(yaw_r) * math.cos(pitch_r)
        eye_y = target_y + state.cam_distance * math.sin(pitch_r)
        eye_z = target_z + state.cam_distance * math.cos(yaw_r) * math.cos(pitch_r)

        gluLookAt(
            eye_x, eye_y, eye_z,
            target_x, target_y, target_z,
            0.0, 1.0, 0.0
        )
        return
 
    follow_r = math.radians(state.rotation_y)

    target_x = state.pos_x
    target_y = 0.95 + state.pos_y
    target_z = state.pos_z

    back_dist = max(3.8, min(state.cam_distance, 6.5))
    side_off  = 0.0
    up_off    = 1.9

    eye_x = target_x - math.sin(follow_r) * back_dist + side_off
    eye_z = target_z - math.cos(follow_r) * back_dist
    eye_y = target_y + up_off

    gluLookAt(
        eye_x, eye_y, eye_z,
        target_x, target_y, target_z,
        0.0, 1.0, 0.0
    )

def move_up(step=3.0):
    state.cam_pitch = min(_PITCH_MAX, state.cam_pitch + step)
    state.cam_mode = 'normal'

def move_down(step=3.0):
    state.cam_pitch = max(_PITCH_MIN, state.cam_pitch - step)
    state.cam_mode = 'normal'

def move_left(step=5.0):
    state.cam_yaw += step
    state.cam_mode = 'normal'

def move_right(step=5.0):
    state.cam_yaw -= step
    state.cam_mode = 'normal'

def zoom_in(step=0.5):
    state.cam_distance = max(_DIST_MIN, state.cam_distance - step)

def zoom_out(step=0.5):
    state.cam_distance = min(_DIST_MAX, state.cam_distance + step)

def reset():
    state.cam_yaw      = 0.0
    state.cam_pitch    = 15.0
    state.cam_distance = 6.0
    state.cam_pan_x    = 0.0
    state.cam_pan_y    = 0.8
    state.cam_mode     = 'normal'

def pan_up(step=0.2):
    state.cam_pan_y += step
    state.cam_mode = 'normal'

def pan_down(step=0.2):
    state.cam_pan_y -= step
    state.cam_mode = 'normal'

def follow_on():
    state.cam_mode = 'follow'

def follow_off():
    state.cam_mode = 'normal'

def toggle_follow():
    if state.cam_mode == 'follow':
        state.cam_mode = 'normal'
        return False
    state.cam_mode = 'follow'
    return True