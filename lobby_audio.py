# lobby_audio.py
# Gestiona la música de fondo del lobby y de los niveles.
import os, pygame

_ok           = False
_lobby_snd    = None
_lobby_ch     = None
_nivel_ch     = None

_SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'niveles', 'sounds')

def init():
    global _ok, _lobby_snd, _lobby_ch, _nivel_ch
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        pygame.mixer.set_num_channels(32)
        _lobby_snd = pygame.mixer.Sound(os.path.join(_SOUNDS_DIR, 'lobby_music.wav'))
        _lobby_snd.set_volume(0.35)
        _lobby_ch = pygame.mixer.Channel(30)
        _nivel_ch = pygame.mixer.Channel(29)
        _ok = True
    except Exception as e:
        print(f"[lobby_audio] {e}")

def play_lobby():
    if _ok and _lobby_ch and not _lobby_ch.get_busy():
        try: _lobby_ch.play(_lobby_snd, loops=-1)
        except Exception: pass

def stop_lobby():
    if _ok and _lobby_ch:
        try: _lobby_ch.stop()
        except Exception: pass

_NIVEL_FILES = {1: 'nivel1_music.wav', 2: 'nivel2_music.wav'}

def play_nivel(num):
    if not _ok or num not in _NIVEL_FILES:
        return
    try:
        snd = pygame.mixer.Sound(os.path.join(_SOUNDS_DIR, _NIVEL_FILES[num]))
        snd.set_volume(0.30)
        _nivel_ch.play(snd, loops=-1)
    except Exception as e:
        print(f"[lobby_audio.play_nivel] {e}")

def stop_nivel():
    if _ok and _nivel_ch:
        try: _nivel_ch.stop()
        except Exception: pass

_aplausos_ch  = None
_aplausos_snd = None

def play_aplausos():
    global _aplausos_ch, _aplausos_snd
    try:
        _aplausos_snd = pygame.mixer.Sound(os.path.join(_SOUNDS_DIR, 'aplausos.wav'))
        _aplausos_snd.set_volume(0.70)
        _aplausos_ch = pygame.mixer.Channel(28)
        _aplausos_ch.play(_aplausos_snd, loops=-1)
    except Exception as e:
        print(f"[lobby_audio.aplausos] {e}")

def stop_aplausos():
    try:
        if _aplausos_ch: _aplausos_ch.stop()
    except Exception: pass
