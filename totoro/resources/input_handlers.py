from OpenGL.GLUT import *
from totoro.actions import state, camara
from totoro.resources import sound_manager


def mouse(button, state_btn, x, y):
    if button == 3 and state_btn == GLUT_DOWN:
        state.zoom -= 1.0
        if state.zoom < 5:
            state.zoom = 5
        glutPostRedisplay()
        return

    elif button == 4 and state_btn == GLUT_DOWN:
        state.zoom += 1.0
        if state.zoom > 60:
            state.zoom = 60
        glutPostRedisplay()
        return

    if button == GLUT_LEFT_BUTTON:
        state.mouse_down = (state_btn == GLUT_DOWN)

    state.last_mouse_x = x
    state.last_mouse_y = y

    camara.mouse(button, state_btn, x, y)
    glutPostRedisplay()


def motion(x, y):
    if not state.mouse_down:
        return

    dx = x - state.last_mouse_x
    dy = y - state.last_mouse_y

    state.rotate_y += dx * 0.3
    state.rotate_x += dy * 0.3

    state.last_mouse_x = x
    state.last_mouse_y = y

    camara.motion(x, y)
    glutPostRedisplay()


def special_keys(key, x, y):
    camara.handle_special_keys(key, x, y)
    glutPostRedisplay()


def keyboard(key, x, y):
    b = key

    if b == b'y':
        state.expression = "happy"
        sound_manager.play_sound("happy")

    elif b == b'a':
        state.expression = "sad"
        sound_manager.play_sound("sad")

    elif b == b'd':
        state.expression = "surprised"
        sound_manager.play_sound("surprised")

    elif b == b'n':
        state.expression = "neutral"

    elif b == b'm':
        state.expression = "angry"
        sound_manager.play_sound("angry")

    elif b == b'w':
        state.walking = not state.walking
        if state.walking:
            sound_manager.start_walk()
        else:
            sound_manager.stop_walk()

    elif b == b'j':
        state.reaction_type = "jump"
        state.reaction_timer = 0
        sound_manager.play_sound("jump")

    elif b == b'k':
        state.reaction_type = "spin"
        state.reaction_timer = 0
        sound_manager.play_sound("spin")

    elif b == b's':
        state.reaction_type = "shake"
        state.reaction_timer = 0
        sound_manager.play_sound("shake")

    elif b == b'h':
        state.reaction_type = "arms_up"
        state.reaction_timer = 0

    elif b == b'l':
        state.reaction_type = "legs_move"
        state.reaction_timer = 0

    elif b == b'1':
        state.current_scene = 1

    elif b == b'2':
        state.current_scene = 2

    elif b == b'3':
        state.current_scene = 3

    elif b == b'4':
        state.current_scene = 4
 

    elif b == b'i':
        state.show_instructions = not state.show_instructions

    elif b == b'b':
        state.show_about = not state.show_about

    elif b == b'o':
        sound_manager.toggle_music()

    elif b == b'r':
        state.char_x = 0.0
        state.char_z = -18.5
        state.rotate_x = 0.0
        state.rotate_y = 0.0
        state.expression = "neutral"
        state.walking = False
        state.current_scene = 1
        sound_manager.stop_walk()

    elif b == b'\x1b':
        sound_manager.stop_walk()
        sound_manager.stop_music()
        glutLeaveMainLoop()

    glutPostRedisplay()