# utilerias/audio_manager.py
import pygame
import os
# Variables globales para almacenar los sonidos

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
sound_main = None
sound_walk = None
sound_jump = None
sound_hi = None
sound_celebration = None
sound_spin = None
sound_bend = None
sound_megajump = None

exp_sad = None
exp_angry = None
exp_happy = None
exp_embarrased = None
exp_surprised = None
exp_doubt = None
exp_angry2 = None

bg_music = {}           # Diccionario para guardar las 7 canciones
current_bg_music = None # Para saber qué canción está sonando ahorita

def obtener_ruta(subcarpeta, archivo):
    """Arma la ruta dinámica uniendo el directorio actual -> subcarpeta -> archivo"""
    return os.path.join(DIRECTORIO_ACTUAL, subcarpeta, archivo)

def init_audio():
    global bg_music, current_bg_music
    global sound_main, sound_walk, sound_jump, sound_hi, sound_celebration, sound_spin, sound_bend, sound_megajump
    global exp_sad, exp_angry, exp_happy, exp_embarrased, exp_surprised, exp_doubt, exp_angry2
    
    pygame.mixer.init()

    # 1. CARGAMOS LAS CANCIONES DE LOS ESCENARIOS
    bg_music[1] = pygame.mixer.Sound(obtener_ruta("escenariosounds", "entrenamiento.mp3"))
    bg_music[2] = pygame.mixer.Sound(obtener_ruta("escenariosounds", "foso.mp3"))
    bg_music[3] = pygame.mixer.Sound(obtener_ruta("escenariosounds", "valle.mp3"))
    bg_music[4] = pygame.mixer.Sound(obtener_ruta("escenariosounds", "taller.mp3"))
    bg_music[5] = pygame.mixer.Sound(obtener_ruta("escenariosounds", "hielo.mp3"))
    bg_music[6] = pygame.mixer.Sound(obtener_ruta("escenariosounds", "pekka.mp3"))
    bg_music[7] = pygame.mixer.Sound(obtener_ruta("escenariosounds", "legendaria.mp3"))

    # 2. CARGAMOS LOS SONIDOS DE MOVIMIENTOS
    sound_walk = pygame.mixer.Sound(obtener_ruta("movimientos", "walk.mp3"))
    sound_jump = pygame.mixer.Sound(obtener_ruta("movimientos", "jump.mp3"))
    sound_hi = pygame.mixer.Sound(obtener_ruta("movimientos", "hi.mp3"))
    sound_celebration = pygame.mixer.Sound(obtener_ruta("movimientos", "celebration.mp3"))
    sound_spin = pygame.mixer.Sound(obtener_ruta("movimientos", "spin.mp3"))
    sound_bend = pygame.mixer.Sound(obtener_ruta("movimientos", "bend.mp3"))
    sound_megajump = pygame.mixer.Sound(obtener_ruta("movimientos", "megajump.mp3"))

    # 3. CARGAMOS LOS SONIDOS DE EXPRESIONES
    exp_sad = pygame.mixer.Sound(obtener_ruta("expresiones", "sad.mp3"))
    exp_angry = pygame.mixer.Sound(obtener_ruta("expresiones", "angry.mp3"))
    exp_happy = pygame.mixer.Sound(obtener_ruta("expresiones", "happy.mp3"))
    exp_embarrased = pygame.mixer.Sound(obtener_ruta("expresiones", "embarrased.mp3"))
    exp_surprised = pygame.mixer.Sound(obtener_ruta("expresiones", "surprised.mp3"))
    exp_doubt = pygame.mixer.Sound(obtener_ruta("expresiones", "doubt.mp3"))
    exp_angry2 = pygame.mixer.Sound(obtener_ruta("expresiones", "angry2.mp3"))

    # 4. Iniciar la música de fondo del primer escenario
    play_scenario_music(1)

def play_scenario_music(scenario_id):
    """Cambia el escenario y reproduce su sonido de presentación una sola vez"""
    global current_bg_music
    
    # Si hay un sonido de fondo sonando, lo detenemos
    if current_bg_music:
        current_bg_music.stop()
        
    # Actualizamos al nuevo sonido y lo reproducimos UNA SOLA VEZ
    if scenario_id in bg_music:
        current_bg_music = bg_music[scenario_id]
        current_bg_music.play()

def replay_scenario_music():
    """Vuelve a reproducir el sonido del escenario actual (Se activa con la tecla M)"""
    if current_bg_music:
        current_bg_music.stop() 
        current_bg_music.play()

def play_sound(snd, loop=False):
    """Reproduce efectos de sonido siempre, independientemente de la música de fondo"""
    if snd:
        if loop:
            snd.play(loops=-1)
        else:
            snd.play()

def stop_sound(snd):
    """Detiene un sonido específico (útil para walk y shake)"""
    if snd:
        snd.stop()