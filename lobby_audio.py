# ============================================================
# lobby_audio.py
# ------------------------------------------------------------
# GESTOR DE AUDIO DE FONDO
# Centraliza todo el audio ambiental del juego usando canales
# fijos de pygame.mixer para evitar superposicion de pistas.
#
# Canales asignados (fijos para no interferir con personajes):
#   Canal 28 -> aplausos (pantalla de ganador)
#   Canal 29 -> musica de nivel 1 o 2
#   Canal 30 -> musica del lobby
#
# Nivel 3 NO tiene musica de fondo porque el audio ES
# la mecanica de juego (identificar instrumentos).
#
# Pregunta tipica:
#   "?Por que canales fijos?"
#   Los personajes ya usan canales 0-27 para sus efectos de
#   sonido. Usar canales altos (28-30) evita conflictos.
#   pygame.mixer.set_num_channels(32) garantiza que existan.
# ============================================================
import os, pygame

_ok           = False   # True si pygame.mixer se inicializo correctamente
_lobby_snd    = None    # objeto Sound de la musica del lobby
_lobby_ch     = None    # canal 30
_nivel_ch     = None    # canal 29
_music_on     = True    # Toggle: True=activo, False=silenciado (tecla M)

_SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'niveles', 'sounds')


def init():
    """
    Inicializa pygame.mixer y precarga la musica del lobby.
    Se llama UNA sola vez antes del bucle GLUT (en main()).
    Si falla (sin audio, driver faltante) el juego sigue
    funcionando sin musica gracias al flag _ok=False.
    """
    global _ok, _lobby_snd, _lobby_ch, _nivel_ch
    try:
        if not pygame.mixer.get_init():
            # frequency=22050: calidad CD reducida (ahorra CPU)
            # size=-16: muestras de 16 bits con signo
            # channels=1: mono (los WAV sinteticos son mono)
            # buffer=512: latencia baja (~11ms)
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        pygame.mixer.set_num_channels(32)   # asegurar que existan canales 28-30
        _lobby_snd = pygame.mixer.Sound(os.path.join(_SOUNDS_DIR, 'lobby_music.wav'))
        _lobby_snd.set_volume(0.35)   # volumen bajo para no tapar los efectos
        _lobby_ch = pygame.mixer.Channel(30)
        _nivel_ch = pygame.mixer.Channel(29)
        _ok = True
    except Exception as e:
        print(f"[lobby_audio] {e}")


def play_lobby():
    """
    Reproduce la musica del lobby en loop infinito.
    Solo actua si: mixer ok + toggle activo + canal no ocupado.
    get_busy() evita reiniciar la pista si ya esta sonando.
    """
    if _ok and _music_on and _lobby_ch and not _lobby_ch.get_busy():
        try: _lobby_ch.play(_lobby_snd, loops=-1)
        except Exception: pass


def stop_lobby():
    """Para la musica del lobby inmediatamente."""
    if _ok and _lobby_ch:
        try: _lobby_ch.stop()
        except Exception: pass


# Mapa de archivos de musica por numero de nivel
# Nivel 3 NO aparece aqui intencionalmente
_NIVEL_FILES = {1: 'nivel1_music.wav', 2: 'nivel2_music.wav'}


def play_nivel(num):
    """
    Reproduce la musica ambiental del nivel en loop.
    Si num=3 o toggle=False, no hace nada.
    Cada llamada crea un nuevo objeto Sound para cargar
    el archivo correcto segun el nivel.
    """
    if not _ok or _music_on is False or num not in _NIVEL_FILES:
        return
    try:
        snd = pygame.mixer.Sound(os.path.join(_SOUNDS_DIR, _NIVEL_FILES[num]))
        snd.set_volume(0.30)
        _nivel_ch.play(snd, loops=-1)
    except Exception as e:
        print(f"[lobby_audio.play_nivel] {e}")


def stop_nivel():
    """Para la musica de nivel inmediatamente."""
    if _ok and _nivel_ch:
        try: _nivel_ch.stop()
        except Exception: pass


_aplausos_ch  = None
_aplausos_snd = None


def play_aplausos():
    """
    Reproduce aplausos en loop en el canal 28 al mostrar
    la pantalla de ganador al final del nivel 3.
    Se detiene con stop_aplausos() al presionar cualquier tecla.
    """
    global _aplausos_ch, _aplausos_snd
    try:
        _aplausos_snd = pygame.mixer.Sound(os.path.join(_SOUNDS_DIR, 'aplausos.wav'))
        _aplausos_snd.set_volume(0.70)
        _aplausos_ch = pygame.mixer.Channel(28)
        _aplausos_ch.play(_aplausos_snd, loops=-1)
    except Exception as e:
        print(f"[lobby_audio.aplausos] {e}")


def stop_aplausos():
    """Para los aplausos al salir de la pantalla de ganador."""
    try:
        if _aplausos_ch: _aplausos_ch.stop()
    except Exception: pass


def disable_for_nivel3():
    """Apaga la musica y la bloquea al entrar al nivel 3.
    Se llama desde main_arcade._activate_nivel(3)."""
    global _music_on
    stop_lobby()
    stop_nivel()
    _music_on = False   # bloquea reactivacion via tecla M


def toggle_music():
    """
    Alterna musica activa/silenciada con la tecla M.
    Solo afecta lobby y niveles 1/2. Nivel 3 nunca se toca.
    Devuelve el nuevo estado (True=ON, False=OFF) para
    mostrarlo en el toast visual de main_arcade.
    """
    global _music_on
    _music_on = not _music_on
    if _music_on:
        play_lobby()    # reanudar si estamos en el lobby
    else:
        stop_lobby()    # apagar si estamos en lobby o nivel 1/2
        stop_nivel()
    return _music_on


def is_music_on():
    """Devuelve True si la musica esta activa."""
    return _music_on
