# resources/input_handlers.py
from OpenGL.GLUT import *
from MegaCaballero.actions import state
from MegaCaballero.actions import camera
from MegaCaballero.utilerias.sonidos import audio_manager
import sys
from MegaCaballero.utilerias.escenarios import escenarios

def mouse(button, state_btn, x, y): 
    # --- SCROLL: ZOOM DE LA CÁMARA ---
    if button == 3 and state_btn == GLUT_DOWN: # Scroll Arriba
        state.zoom -= 2.0
        if state.zoom < 10.0: state.zoom = 10.0
        glutPostRedisplay()
    elif button == 4 and state_btn == GLUT_DOWN: # Scroll Abajo
        state.zoom += 2.0
        if state.zoom > 90.0: state.zoom = 90.0
        glutPostRedisplay()

    # CLICK NORMAL
    if button == GLUT_LEFT_BUTTON:
        state.mouse_down = (state_btn == GLUT_DOWN)
        state.last_mouse_x = x
        state.last_mouse_y = y
        camera.mouse(button, state_btn, x, y)
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
    glutPostRedisplay()

# --- EVENTOS DEL TECLADO (Traslacion)
def special_keys(key, x, y):
    velocidad = 0.2 # Qué tan rápido camina por el mapa

    # --- MOVIMIENTO DEL PERSONAJE ---
    if key == GLUT_KEY_UP:
        state.fox_z -= velocidad  # Camina hacia el fondo
        state.is_walking = True
    elif key == GLUT_KEY_DOWN:
        state.fox_z += velocidad  # Camina hacia el frente
        state.is_walking = True
    elif key == GLUT_KEY_LEFT:
        state.fox_x -= velocidad  # Camina hacia la izquierda
        state.is_walking = True
    elif key == GLUT_KEY_RIGHT:
        state.fox_x += velocidad  # Camina hacia la derecha
        state.is_walking = True

    # --- CAMBIO DE ESCENARIOS (F1 a F7) ---
    elif key == GLUT_KEY_F1: 
        state.current_escenario = 1 
        audio_manager.play_scenario_music(1)
    elif key == GLUT_KEY_F2: 
        state.current_escenario = 2 
        audio_manager.play_scenario_music(2)
    elif key == GLUT_KEY_F3: 
        state.current_escenario = 3 
        audio_manager.play_scenario_music(3)
    elif key == GLUT_KEY_F4: 
        state.current_escenario = 4 
        audio_manager.play_scenario_music(4)
    elif key == GLUT_KEY_F5: 
        state.current_escenario = 5 
        audio_manager.play_scenario_music(5)
    elif key == GLUT_KEY_F6: 
        state.current_escenario = 6 
        audio_manager.play_scenario_music(6)
    elif key == GLUT_KEY_F7: 
        state.current_escenario = 7 
        audio_manager.play_scenario_music(7)
    
    glutPostRedisplay()

# --- DETENER ANIMACIÓN AL SOLTAR LA FLECHA ---
def special_keys_up(key, x, y):
    if key in (GLUT_KEY_UP, GLUT_KEY_DOWN, GLUT_KEY_LEFT, GLUT_KEY_RIGHT):
        state.is_walking = False

# --- TECLAS NORMALES (LETRAS Y NÚMEROS) ---
def keyboard(key, x, y):
    b = key.lower() 
    
    if b == b'i': state.show_instructions = not state.show_instructions
    elif b == b'c': state.show_about = not state.show_about
    elif b == b'r':  # RESET DE CÁMARA Y POSICIÓN
        camera.reset_camera()
        state.fox_x=0.0
        state.fox_z = 0.0
        state.rotate_y = 0.0
        state.rotate_x = 0.0
        state.zoom = 45.0
        
    # CONTROL MAESTRO DE SONIDO (Tecla M)
    elif b == b'm':
       audio_manager.replay_scenario_music()
      
    # --- EXPRESIONES (1 AL 8) ---
    elif b == b'1': 
        state.expression = 1  
        audio_manager.play_sound(audio_manager.exp_sad)
    elif b == b'2': 
        state.expression = 2  
        audio_manager.play_sound(audio_manager.exp_angry)
    elif b == b'3': 
        state.expression = 3  
        audio_manager.play_sound(audio_manager.exp_happy)
    elif b == b'4': 
        state.expression = 4  
        audio_manager.play_sound(audio_manager.exp_embarrased)
    elif b == b'5': 
        state.expression = 5  
        audio_manager.play_sound(audio_manager.exp_surprised)
    elif b == b'6': 
        state.expression = 6  
        audio_manager.play_sound(audio_manager.exp_doubt)
    elif b == b'7': 
        state.expression = 7  
        audio_manager.play_sound(audio_manager.exp_angry2)
    elif b == b'8': 
        state.expression = 0  
    
    # --- MOVIMIENTOS Y REACCIONES (A - J) ---
    elif b == b'a': # Caminar (Manual Toggle)
        state.is_walking = not state.is_walking
        if state.is_walking:
            audio_manager.play_sound(audio_manager.sound_walk, loop=True) 
        else:
            audio_manager.stop_sound(audio_manager.sound_walk) 

    elif b == b's': # Saltar (Trigger)
        if not state.is_jumping: 
            state.is_jumping = True
            state.jump_velocity = 0.25
            audio_manager.play_sound(audio_manager.sound_jump)
        
    elif b == b'd': # Saludar / Hi (Toggle)
        state.is_waving = not state.is_waving
        if state.is_waving:
            audio_manager.play_sound(audio_manager.sound_hi, loop=True)
        else:
            audio_manager.stop_sound(audio_manager.sound_hi)
            
    elif b == b'f': # Celebración (Trigger)
        if not state.is_celebrating: 
            state.is_celebrating = True
            state.celebrate_cycles = 0
            audio_manager.play_sound(audio_manager.sound_celebration) 
        
    elif b == b'g': # Girar / Spin (Trigger)
        if not state.is_spinning:
            state.is_spinning = True
            audio_manager.play_sound(audio_manager.sound_spin)

    elif b == b'h': # Agachar / Bend (Trigger)
        if not state.is_crouching:
            state.is_crouching = True
            audio_manager.play_sound(audio_manager.sound_bend)

    elif b == b'j': # Mega Jump (Trigger)
        if not state.is_smashing:
            state.is_smashing = True
            state.smash_phase = 0
            audio_manager.play_sound(audio_manager.sound_megajump)

    elif key == b'\x1b': # ESC
        glutLeaveMainLoop()
        
    glutPostRedisplay()