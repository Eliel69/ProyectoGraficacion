from OpenGL.GL import *
from OpenGL.GLUT import *
from totoro.actions import state
import math


def draw_ellipsoid(cx, cy, cz, sx, sy, sz, r, g, b, slices=30, stacks=30):
    glPushMatrix()
    glTranslatef(cx, cy, cz)
    glScalef(sx, sy, sz)
    glColor3f(r, g, b)
    glutSolidSphere(1.0, slices, stacks)
    glPopMatrix()


def draw_totoro_full():
    glPushMatrix()

    glTranslatef(state.shake_offset, state.jump_offset, 0.0)
    glRotatef(state.spin_angle, 0, 1, 0)

    draw_body()
    draw_belly()
    draw_ears()
    draw_arms()
    draw_legs()
    draw_eyes()
    draw_nose()
    draw_whiskers()
    draw_mouth()
    draw_belly_marks()

    glPopMatrix()


def draw_body():
    draw_ellipsoid(0.0, 0.0, 0.0, 4.0, 5.0, 3.0, 0.49, 0.51, 0.53)


def draw_belly():
    draw_ellipsoid(0.0, -0.5, 1.2, 2.8, 3.5, 2.0, 0.93, 0.91, 0.77)


def draw_ears():
    draw_ellipsoid(-1.2, 4.8, 0.0, 0.5, 1.5, 0.4, 0.49, 0.51, 0.53)
    draw_ellipsoid(1.2, 4.8, 0.0, 0.5, 1.5, 0.4, 0.49, 0.51, 0.53)


def draw_arms():
    glPushMatrix()
    glTranslatef(-3.8, 0.0, 0.0)
    glRotatef(state.arm_angle, 1, 0, 0)
    draw_ellipsoid(0.0, 0.0, 0.0, 0.6, 1.5, 0.6, 0.49, 0.51, 0.53)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(3.8, 0.0, 0.0)
    glRotatef(-state.arm_angle, 1, 0, 0)
    draw_ellipsoid(0.0, 0.0, 0.0, 0.6, 1.5, 0.6, 0.49, 0.51, 0.53)
    glPopMatrix()


def draw_legs():
    glPushMatrix()
    glTranslatef(-1.5, -4.5, 0.5)
    glRotatef(state.leg_angle, 1, 0, 0)
    draw_ellipsoid(0.0, 0.0, 0.0, 0.8, 0.6, 0.8, 0.49, 0.51, 0.53)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(1.5, -4.5, 0.5)
    glRotatef(-state.leg_angle, 1, 0, 0)
    draw_ellipsoid(0.0, 0.0, 0.0, 0.8, 0.6, 0.8, 0.49, 0.51, 0.53)
    glPopMatrix()


def draw_eyes():
    if state.expression == "happy":
        draw_happy_eyes()
    elif state.expression == "sad":
        draw_sad_eyes()
    elif state.expression == "surprised":
        draw_surprised_eyes()
    elif state.expression == "angry":
        draw_angry_eyes()
    else:
        draw_neutral_eyes()


def draw_neutral_eyes():
    draw_ellipsoid(-1.0, 2.2, 2.6, 0.4, 0.4, 0.2, 1.0, 1.0, 1.0)
    draw_ellipsoid(1.0, 2.2, 2.6, 0.4, 0.4, 0.2, 1.0, 1.0, 1.0)
    draw_ellipsoid(-1.0, 2.2, 2.8, 0.15, 0.15, 0.1, 0.0, 0.0, 0.0)
    draw_ellipsoid(1.0, 2.2, 2.8, 0.15, 0.15, 0.1, 0.0, 0.0, 0.0)


def draw_happy_eyes():
    glDisable(GL_LIGHTING)
    glColor3f(0, 0, 0)
    glLineWidth(3)
    glBegin(GL_LINES)
    glVertex3f(-1.4, 2.2, 2.8)
    glVertex3f(-0.6, 2.0, 2.8)

    glVertex3f(0.6, 2.0, 2.8)
    glVertex3f(1.4, 2.2, 2.8)
    glEnd()
    glEnable(GL_LIGHTING)


def draw_sad_eyes():
    glDisable(GL_LIGHTING)
    glColor3f(0, 0, 0)
    glLineWidth(3)
    glBegin(GL_LINES)
    glVertex3f(-1.4, 2.0, 2.8)
    glVertex3f(-0.6, 2.2, 2.8)

    glVertex3f(0.6, 2.2, 2.8)
    glVertex3f(1.4, 2.0, 2.8)
    glEnd()
    glEnable(GL_LIGHTING)


def draw_surprised_eyes():
    draw_ellipsoid(-1.0, 2.2, 2.6, 0.5, 0.6, 0.2, 1.0, 1.0, 1.0)
    draw_ellipsoid(1.0, 2.2, 2.6, 0.5, 0.6, 0.2, 1.0, 1.0, 1.0)
    draw_ellipsoid(-1.0, 2.2, 2.8, 0.18, 0.25, 0.1, 0.0, 0.0, 0.0)
    draw_ellipsoid(1.0, 2.2, 2.8, 0.18, 0.25, 0.1, 0.0, 0.0, 0.0)


def draw_angry_eyes():
    draw_neutral_eyes()
    glDisable(GL_LIGHTING)
    glColor3f(0, 0, 0)
    glLineWidth(2)
    glBegin(GL_LINES)
    glVertex3f(-1.4, 2.7, 2.8)
    glVertex3f(-0.7, 2.4, 2.8)

    glVertex3f(0.7, 2.4, 2.8)
    glVertex3f(1.4, 2.7, 2.8)
    glEnd()
    glEnable(GL_LIGHTING)


def draw_nose():
    draw_ellipsoid(0.0, 2.0, 2.9, 0.25, 0.15, 0.15, 0.15, 0.15, 0.15)


def draw_whiskers():
    glDisable(GL_LIGHTING)
    glLineWidth(2.5)
    glColor3f(0.1, 0.1, 0.1)
    glBegin(GL_LINES)
    for i in [-0.3, 0.0, 0.3]:
        glVertex3f(-0.5, 1.8 + i, 2.8)
        glVertex3f(-2.5, 2.0 + (i * 2), 2.5)

    for i in [-0.3, 0.0, 0.3]:
        glVertex3f(0.5, 1.8 + i, 2.8)
        glVertex3f(2.5, 2.0 + (i * 2), 2.5)
    glEnd()
    glEnable(GL_LIGHTING)


def draw_mouth():
    glDisable(GL_LIGHTING)
    glColor3f(0.1, 0.1, 0.1)
    glLineWidth(3)

    glBegin(GL_LINES)

    if state.expression == "happy":
        glVertex3f(-0.8, 1.2, 2.9)
        glVertex3f(0.0, 0.9, 2.9)
        glVertex3f(0.0, 0.9, 2.9)
        glVertex3f(0.8, 1.2, 2.9)

    elif state.expression == "sad":
        glVertex3f(-0.8, 0.9, 2.9)
        glVertex3f(0.0, 1.2, 2.9)
        glVertex3f(0.0, 1.2, 2.9)
        glVertex3f(0.8, 0.9, 2.9)

    elif state.expression == "surprised":
        glEnd()
        glEnable(GL_LIGHTING)
        draw_ellipsoid(0.0, 1.0, 2.95, 0.25, 0.35, 0.1, 0.1, 0.1, 0.1)
        return

    elif state.expression == "angry":
        glVertex3f(-0.7, 0.95, 2.9)
        glVertex3f(0.7, 0.95, 2.9)

    else:
        glVertex3f(-0.6, 1.0, 2.9)
        glVertex3f(0.6, 1.0, 2.9)

    glEnd()
    glEnable(GL_LIGHTING)


def draw_belly_marks():
    glDisable(GL_LIGHTING)
    glColor3f(0.6, 0.6, 0.6)
    glLineWidth(3)
    glBegin(GL_LINES)

    glVertex3f(-1.2, -0.2, 3.0)
    glVertex3f(-0.6, 0.3, 3.0)

    glVertex3f(0.0, -0.4, 3.0)
    glVertex3f(0.0, 0.4, 3.0)

    glVertex3f(1.2, -0.2, 3.0)
    glVertex3f(0.6, 0.3, 3.0)

    glEnd()
    glEnable(GL_LIGHTING)