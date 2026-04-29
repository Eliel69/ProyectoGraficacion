# gato_3d/resources/sounds.py
# CORRECCIÓN: 'from actions import state' → from gato_3d.actions import state

import os

try:
    import pygame
    _pygame_available = True
except ImportError:
    _pygame_available = False

from gato_3d.actions import state                     # CORREGIDO

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_SOUNDS = {
    "caminar":       os.path.join(_BASE, "caminar.mp3"),
    "girar":         os.path.join(_BASE, "girar.mp3"),
    "saltar":        os.path.join(_BASE, "saltar.mp3"),
    "saludar":       os.path.join(_BASE, "saludar.mp3"),
    "agacharse":     os.path.join(_BASE, "agacharse.mp3"),
    "bailar":        os.path.join(_BASE, "bailar.mp3"),
    "brazos_arriba": os.path.join(_BASE, "brazos arriba.mp3"),
}

_SCENE_SOUNDS = {
    1: os.path.join(_BASE, "Fondo casa.mp3"),
    2: os.path.join(_BASE, "Fondo arcoiris.mp3"),
    3: os.path.join(_BASE, "Fondo Columpio.mp3"),
    4: os.path.join(_BASE, "Fondo habitacion.mp3"),
    5: os.path.join(_BASE, "Fondo playa.mp3"),
    6: os.path.join(_BASE, "Fondo bosque.mp3"),
    7: os.path.join(_BASE, "Fondo espacio.mp3"),
}

_scene_channel  = None
_motion_channel = None

def init():
    global _scene_channel, _motion_channel
    if not _pygame_available:
        return
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(16)
        _scene_channel  = pygame.mixer.Channel(15)
        _motion_channel = pygame.mixer.Channel(14)
    except Exception as e:
        print(f"[Sonido] No se pudo inicializar pygame.mixer: {e}")

def play(name):
    global _motion_channel
    if not _pygame_available or not state.sound_enabled:
        return
    path = _SOUNDS.get(name)
    if not path or not os.path.exists(path):
        return
    try:
        if _motion_channel is None:
            _motion_channel = pygame.mixer.Channel(14)
        snd = pygame.mixer.Sound(path)
        _motion_channel.stop()
        _motion_channel.play(snd)
    except Exception as e:
        print(f"[Sonido] Error reproduciendo '{name}': {e}")

def play_scene(scene_num):
    global _scene_channel
    if not _pygame_available or not state.sound_enabled:
        return
    path = _SCENE_SOUNDS.get(scene_num)
    if not path or not os.path.exists(path):
        print(f"[Sonido] Fondo no encontrado escena {scene_num}: {path}")
        return
    try:
        if _scene_channel is None:
            _scene_channel = pygame.mixer.Channel(15)
        snd = pygame.mixer.Sound(path)
        _scene_channel.stop()
        _scene_channel.play(snd, loops=-1)
    except Exception as e:
        print(f"[Sonido] Error fondo escena {scene_num}: {e}")

def stop_scene():
    global _scene_channel
    if _pygame_available and _scene_channel:
        try:
            _scene_channel.stop()
        except Exception:
            pass

def toggle_all():
    state.sound_enabled = not state.sound_enabled
    if not state.sound_enabled and _pygame_available:
        try:
            pygame.mixer.pause()
        except Exception:
            pass
    else:
        if _pygame_available:
            try:
                pygame.mixer.unpause()
            except Exception:
                pass
