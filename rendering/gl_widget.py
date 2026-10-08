try:
    from PySide6.QtOpenGLWidgets import QOpenGLWidget
    from PySide6.QtCore import Qt
    HAS_PYSIDE6 = True
except (ImportError, Exception):
    QOpenGLWidget = object
    Qt = None
    HAS_PYSIDE6 = False

from rendering.camera import Camera
from rendering.renderer import Renderer
from core.gaussian_model import GaussianModel

class GLWidget(QOpenGLWidget):
    """
    Qt OpenGL widget pre zobrazenie 3D scény a Gaussoviek.
    Využíva OpenGL jadro Renderer a kameru Camera.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera = Camera()
        self.renderer = Renderer()
        self.model = GaussianModel()
        self.scale_multiplier = 1.0
        self.last_pos = None

    def initializeGL(self):
        self.renderer.init_gl(self.width(), self.height())

    def resizeGL(self, w, h):
        self.renderer.resize(w, h)

    def paintGL(self):
        self.renderer.clear()
        self.camera.apply()
        self.renderer.draw_grid_and_axes()
        self.renderer.draw_gaussians(self.model, self.scale_multiplier)

    def draw_gaussians(self, model=None, scale_multiplier=None):
        """Umožňuje priame vykreslenie alebo aktualizáciu zobrazenia Gaussoviek."""
        target_model = model if model is not None else self.model
        multiplier = scale_multiplier if scale_multiplier is not None else self.scale_multiplier
        self.renderer.draw_gaussians(target_model, multiplier)

    # Interakcia myšou
    def mousePressEvent(self, event):
        self.last_pos = event.position()

    def mouseMoveEvent(self, event):
        if self.last_pos is None:
            return

        dx = event.position().x() - self.last_pos.x()
        dy = event.position().y() - self.last_pos.y()

        if event.buttons() == Qt.MouseButton.LeftButton:
            self.camera.rotate(dx, dy)
            self.update()
        elif event.buttons() in (Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton):
            self.camera.pan(dx, dy)
            self.update()

        self.last_pos = event.position()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.camera.zoom(1 if delta > 0 else -1)
        self.update()
