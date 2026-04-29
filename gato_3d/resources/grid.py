# resources/grid.py
from OpenGL.GL import *
from gato_3d.actions import state

_GRID_COLORS = {
    1: (0.20, 0.65, 0.20),
    2: (0.45, 0.80, 0.45),
    3: (0.35, 0.60, 0.35),
    4: (0.40, 0.28, 0.16),
    5: (0.85, 0.75, 0.50),
    6: (0.08, 0.12, 0.08),
    7: (0.06, 0.06, 0.18),
}

def draw_grid():
    sc = state.current_scene
    r, g, b = _GRID_COLORS.get(sc, (0.3, 0.3, 0.3))
    glColor3f(r * 0.8, g * 0.8, b * 0.8)
    glLineWidth(1)
    glBegin(GL_LINES)
    for i in range(-10, 11):
        glVertex3f(i, -1.20,  10); glVertex3f(i, -1.20, -10)
        glVertex3f(-10, -1.20, i); glVertex3f( 10, -1.20, i)
    glEnd()
