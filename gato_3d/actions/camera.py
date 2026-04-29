# actions/camera.py
from OpenGL.GL import *
from OpenGL.GLU import *
import math
from gato_3d.actions import state

def setup_camera():
    glLoadIdentity()

    # Límites de pitch
    if state.cam_pitch >  89.0: state.cam_pitch =  89.0
    if state.cam_pitch < -10.0: state.cam_pitch = -10.0
    if state.cam_radius < 2.0:  state.cam_radius = 2.0
    if state.cam_radius > 20.0: state.cam_radius = 20.0

    yaw_rad   = math.radians(state.cam_yaw)
    pitch_rad = math.radians(state.cam_pitch)

    cam_x = state.char_x + state.cam_radius * math.cos(pitch_rad) * math.sin(yaw_rad)
    cam_y = state.char_y + state.cam_target_y + state.cam_radius * math.sin(pitch_rad)
    cam_z = state.char_z + state.cam_radius * math.cos(pitch_rad) * math.cos(yaw_rad)

    gluLookAt(cam_x, cam_y, cam_z,
              state.char_x, state.char_y + state.cam_target_y, state.char_z,
              0, 1, 0)

def reset_camera():
    state.cam_radius   = 8.0
    state.cam_yaw      = 0.0
    state.cam_pitch    = 20.0
    state.cam_target_y = 0.0
