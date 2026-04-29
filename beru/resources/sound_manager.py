# beru/resources/sound_manager.py
# CORRECCIÓN: 'import actions.state as state' → from beru.actions import state

import os
from beru.actions import state                        # CORREGIDO

try:
    import pygame
    pygame.mixer.init()
    _ok = True
except Exception:
    _ok = False

_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "Utilerias", "sonidos")

_FILES = {
    "beru_caminar"  : "beru_caminar.mp3",
    "beru_saltar"   : "beru_saltar.mp3",
    "beru_saludar"  : "beru_saludar.mp3",
    "beru_girar"    : "beru_girar.mp3",
    "beru_feliz"    : "beru_feliz.mp3",
    "beru_triste"   : "beru_triste.mp3",
    "beru_enojado"  : "beru_enojado.mp3",
    "beru_miedo"    : "beru_miedo.mp3",
    "beru_sorpresa" : "beru_sorpresa.mp3",
    "sc0"           : "sc_dungeon.mp3",
    "sc1"           : "sc_hormigas.mp3",
    "sc2"           : "sc_sombras.mp3",
    "sc3"           : "sc_monarquia.mp3",
    "sc4"           : "sc_caos.mp3",
    "sc5"           : "sc_castillo.mp3",
    "sc6"           : "sc_puerta.mp3",
}

_cache = {}
_BG_CHANNEL_INDEX = 0
_bg_channel = None

if _ok:
    try:
        pygame.mixer.set_num_channels(16)
        _bg_channel = pygame.mixer.Channel(_BG_CHANNEL_INDEX)
    except Exception:
        _bg_channel = None

def _load(name):
    if name in _cache:
        return _cache[name]
    if not _ok:
        return None
    filename = _FILES.get(name, "")
    if not filename:
        _cache[name] = None
        return None
    path = os.path.join(_BASE, filename)
    if not os.path.isfile(path):
        _cache[name] = None
        return None
    try:
        snd = pygame.mixer.Sound(path)
        _cache[name] = snd
        return snd
    except Exception:
        _cache[name] = None
        return None

def play(name, loops=0):
    if not _ok or not state.fx_enabled:
        return
    snd = _load(name)
    if snd:
        snd.play(loops=loops)

def stop_fx():
    if not _ok:
        return
    try:
        total = pygame.mixer.get_num_channels()
        for i in range(total):
            if i == _BG_CHANNEL_INDEX:
                continue
            pygame.mixer.Channel(i).stop()
    except Exception:
        pass

def play_scenario(index):
    stop_scenario()
    if not _ok or not state.music_enabled:
        return
    snd = _load(f"sc{index}")
    if snd and _bg_channel is not None:
        _bg_channel.play(snd, loops=-1)
    elif snd:
        snd.play(loops=-1)

def stop_scenario():
    if not _ok:
        return
    try:
        if _bg_channel is not None:
            _bg_channel.stop()
    except Exception:
        pass

def toggle_music():
    state.music_enabled = not state.music_enabled
    if not state.music_enabled:
        stop_scenario()
    else:
        play_scenario(state.current_scenario)
    return state.music_enabled

def toggle_fx():
    state.fx_enabled = not state.fx_enabled
    if not state.fx_enabled:
        stop_fx()
    return state.fx_enabled

def stop_all():
    stop_scenario()
    stop_fx()
