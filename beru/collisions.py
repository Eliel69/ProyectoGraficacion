# beru/collisions.py
# CORRECCIONES:
# 1. Eliminado sys.path.insert que rompía imports en modo arcade.
# 2. 'import actions.state as state'           → from beru.actions import state
# 3. 'from resources.sound_manager import play' → from beru.resources import sound_manager

from OpenGL.GL  import *
from OpenGL.GLU import *
from beru.actions import state                        # CORREGIDO

_PLAYER_RADIUS = 0.55
_HIT_DURATION  = 60

def draw_objects():
    for obj in state.collision_objects:
        glPushMatrix()
        glTranslatef(obj["x"], obj["y"], obj["z"])

        if obj["hit"]:
            glColor3f(1.0, 1.0, 0.4)
        else:
            glColor3f(*obj["color"])

        oid = obj["id"]

        if oid == 0:
            q = gluNewQuadric()
            glTranslatef(0.0, 0.8, 0.0)
            gluSphere(q, 0.5, 16, 16)
            gluDeleteQuadric(q)

        elif oid == 1:
            s = 0.45
            glBegin(GL_QUADS)
            glVertex3f(-s, 0,  s); glVertex3f( s, 0,  s)
            glVertex3f( s, s*2, s); glVertex3f(-s, s*2, s)

            glVertex3f( s, 0, -s); glVertex3f(-s, 0, -s)
            glVertex3f(-s, s*2,-s); glVertex3f( s, s*2,-s)

            glVertex3f(-s, 0, -s); glVertex3f(-s, 0,  s)
            glVertex3f(-s, s*2, s); glVertex3f(-s, s*2,-s)

            glVertex3f( s, 0,  s); glVertex3f( s, 0, -s)
            glVertex3f( s, s*2,-s); glVertex3f( s, s*2, s)

            glVertex3f(-s, s*2, s); glVertex3f( s, s*2, s)
            glVertex3f( s, s*2,-s); glVertex3f(-s, s*2,-s)

            glVertex3f(-s, 0, -s); glVertex3f( s, 0, -s)
            glVertex3f( s, 0,  s); glVertex3f(-s, 0,  s)
            glEnd()

        elif oid == 2:
            q = gluNewQuadric()
            gluCylinder(q, 0.45, 0.0, 1.2, 12, 4)
            gluDeleteQuadric(q)

        glPopMatrix()

def check():
    from beru.resources import sound_manager          # CORREGIDO

    import math
    for obj in state.collision_objects:
        if obj["hit"]:
            obj["hit_timer"] -= 1
            if obj["hit_timer"] <= 0:
                obj["hit"]       = False
                obj["hit_timer"] = 0
                if state.expression in ('fear', 'smile', 'angry'):
                    state.expression = 'neutral'
                if state.movement in ('jump', 'spin'):
                    state.movement = 'idle'
            continue

        dx   = state.pos_x - obj["x"]
        dz   = state.pos_z - obj["z"]
        dist = math.sqrt(dx*dx + dz*dz)

        if dist < (_PLAYER_RADIUS + obj["radius"]):
            obj["hit"]       = True
            obj["hit_timer"] = _HIT_DURATION
            sound_manager.play("beru_miedo")           # CORREGIDO

            oid = obj["id"]
            if oid == 0:
                state.expression = 'fear'
                if dist > 0.01:
                    state.pos_x += (dx / dist) * 0.8
                    state.pos_z += (dz / dist) * 0.8
            elif oid == 1:
                state.expression = 'smile'
                state.movement   = 'jump'
                state.jump_phase = 0.0
            elif oid == 2:
                state.expression = 'angry'
                state.movement   = 'spin'
