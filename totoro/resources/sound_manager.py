import os
import pygame

try:
    pygame.mixer.init()
except Exception as e:
    print("Error al iniciar mixer:", e)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUND_DIR = os.path.join(BASE_DIR, "Utilerias", "sonidos")

sounds = {}
music_loaded = False
walk_channel = None
music_enabled = True


def load_sounds():
    global sounds, music_loaded

    sound_files = {
        "jump": "salto.mp3",
        "walk": "caminar.mp3",
        "happy": "feliz.mp3",
        "sad": "triste.mp3",
        "surprised": "sorpresa.mp3",
        "spin": "giro.mp3",
        "shake": "temblor.mp3",
        "angry": "enojado.mp3"
    }

    for key, filename in sound_files.items():
        path = os.path.join(SOUND_DIR, filename)
        if os.path.exists(path):
            try:
                sounds[key] = pygame.mixer.Sound(path)
                print(f"Cargado: {filename}")
            except Exception as e:
                print(f"Error cargando {filename}: {e}")
        else:
            print(f"No se encontró el archivo: {path}")

    music_path = os.path.join(SOUND_DIR, "fondo_bosque.mp3")
    if os.path.exists(music_path):
        try:
            pygame.mixer.music.load(music_path)
            music_loaded = True
            print("Música de fondo cargada")
        except Exception as e:
            print(f"Error cargando música de fondo: {e}")
    else:
        print(f"No se encontró la música de fondo: {music_path}")


def play_sound(name):
    if name in sounds:
        sounds[name].play()


def start_walk():
    global walk_channel
    if "walk" in sounds and walk_channel is None:
        walk_channel = sounds["walk"].play(-1)


def stop_walk():
    global walk_channel
    if walk_channel is not None:
        walk_channel.stop()
        walk_channel = None


def play_music():
    if music_enabled and music_loaded and not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)


def stop_music():
    pygame.mixer.music.stop()


def toggle_music():
    global music_enabled
    music_enabled = not music_enabled

    if music_enabled:
        play_music()
        print("Música de bosque activada")
    else:
        stop_music()
        print("Música de bosque desactivada")