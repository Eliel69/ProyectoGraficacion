# resources/sounds.py  –  5 sonidos sinteticos con pygame
import math, array

_snd      = {}
_pg_ready = False

def _make_tone(freq, ms, vol=0.42, shape="sine"):
    try:
        import pygame.sndarray
        sr = 22050
        n  = int(sr * ms / 1000)
        buf = array.array('h')
        for i in range(n):
            t = i / sr
            if   shape == "chirp":  v = math.sin(2*math.pi*(freq + freq*i/n)*t)
            elif shape == "sq":     v = 1.0 if math.sin(2*math.pi*freq*t) >= 0 else -1.0
            else:                   v = math.sin(2*math.pi*freq*t)
            env = max(0, 1 - i/n)
            buf.append(int(v * env * vol * 32767))
        return pygame.sndarray.make_sound(buf)
    except Exception:
        return None

def init():
    global _pg_ready
    try:
        import pygame
        pygame.mixer.init(22050, -16, 1, 512)
        _pg_ready = True
        # 5 sonidos distintos
        _snd["jump"]  = _make_tone(520, 280, shape="chirp")  # salto: agudo ascendente
        _snd["step"]  = _make_tone(160,  80, shape="sq")     # paso: grave corto
        _snd["expr+"] = _make_tone(880, 120)                 # expresion positiva (guino)
        _snd["expr-"] = _make_tone(130, 350, shape="sq")     # expresion negativa (ira/miedo/tristeza)
        _snd["scene"] = _make_tone(440, 200)                 # cambio de escena
    except Exception:
        pass

def play(name):
    from fallguy.actions import state
    if not state.sound_enabled or not _pg_ready:
        return
    s = _snd.get(name)
    if s:
        try: s.play()
        except Exception: pass