from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
import numpy as np

class Renderer:
    """
    OpenGL vykresľovacie jadro.
    Stará sa o projekčné matice, mriežku, osi a neskôr vykresľovanie Gaussov.
    """
    def __init__(self):
        pass

    def init_gl(self, width, height):
        """Inicializácia OpenGL stavov."""
        glClearColor(0.12, 0.12, 0.14, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.resize(width, height)

    def resize(self, width, height):
        """Aktualizácia rozmerov okna a perspektívy."""
        if height == 0:
            height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / float(height), 0.1, 200.0)
        glMatrixMode(GL_MODELVIEW)

    def clear(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

    def draw_grid_and_axes(self, grid_size=5, step=1.0):
        """Vykreslí orientačnú 3D mriežku v rovine XZ a súradnicové osi."""
        # 1. Mriežka v rovine Y = 0
        glColor4f(0.25, 0.25, 0.28, 0.6)
        glBegin(GL_LINES)
        for i in np.arange(-grid_size, grid_size + 0.1, step):
            # Čiary pozdĺž X
            glVertex3f(-grid_size, 0.0, i)
            glVertex3f(grid_size, 0.0, i)
            # Čiary pozdĺž Z
            glVertex3f(i, 0.0, -grid_size)
            glVertex3f(i, 0.0, grid_size)
        glEnd()

        # 2. Hlavné osi
        glLineWidth(2.0)
        glBegin(GL_LINES)
        # X osa (Červená)
        glColor3f(0.9, 0.2, 0.2)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(2.0, 0.0, 0.0)

        # Y osa (Zelená) - smer hore
        glColor3f(0.2, 0.85, 0.2)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 2.0, 0.0)

        # Z osa (Modrá)
        glColor3f(0.2, 0.4, 0.95)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 2.0)
        glEnd()
        glLineWidth(1.0)
