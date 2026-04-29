# utilerias/audio_manager.py
import pygame
import os

# 1. DETECTAR LA RUTA AUTOMÁTICA
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))

# 2. FUNCIÓN AYUDANTE MEJORADA
def obtener_ruta(*rutas):
    """Une dinámicamente las carpetas y archivos partiendo del directorio actual"""
    return os.path.join(DIRECTORIO_ACTUAL, *rutas)

# Variables globales para almacenar los sonidos
sound_main = None
sound_walk = None
sound_jump = None
sound_spin = None
sound_shake = None
sound_vent = None

exp_embarrassed = None
exp_surprised = None
exp_sad = None
exp_suspicious = None
exp_angry = None

# Bandera para el control maestro de sonido
sonido_activado = True 

def init_audio():
    global sound_main, sound_walk, sound_jump, sound_spin, sound_shake, sound_vent
    global exp_embarrassed, exp_surprised, exp_sad, exp_suspicious, exp_angry
    
    pygame.mixer.init()

    # --- Carga directa de sonidos con rutas relativas ---
    
    # Sonido principal (está directo en la carpeta actual)
    sound_main = pygame.mixer.Sound(obtener_ruta("soundmain.mp3"))
    
    # Movimientos (están dentro de la subcarpeta 'movimientos')
    sound_walk = pygame.mixer.Sound(obtener_ruta("movimientos", "walk.mp3"))
    sound_jump = pygame.mixer.Sound(obtener_ruta("movimientos", "jump.mp3"))
    sound_spin = pygame.mixer.Sound(obtener_ruta("movimientos", "spin.mp3"))
    sound_shake = pygame.mixer.Sound(obtener_ruta("movimientos", "shake.mp3"))
    sound_vent = pygame.mixer.Sound(obtener_ruta("movimientos", "vent.mp3"))

    # Expresiones (están dentro de la subcarpeta 'expresiones')
    exp_embarrassed = pygame.mixer.Sound(obtener_ruta("expresiones", "embarrased.mp3"))
    exp_surprised = pygame.mixer.Sound(obtener_ruta("expresiones", "surprised.mp3"))
    exp_sad = pygame.mixer.Sound(obtener_ruta("expresiones", "sad.mp3"))
    exp_suspicious = pygame.mixer.Sound(obtener_ruta("expresiones", "suspicious.mp3"))
    exp_angry = pygame.mixer.Sound(obtener_ruta("expresiones", "angry.mp3"))

    # Iniciar la música de fondo
    sonidoOn()


def sonidoOn():
    global sonido_activado
    sonido_activado = True
    if sound_main:
        sound_main.play(loops=-1) # Vuelve a reproducir solo la música principal

def sonidoOff():
    global sonido_activado
    sonido_activado = False
    if sound_main:
        sound_main.stop() # Detiene EXCLUSIVAMENTE la música principal

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