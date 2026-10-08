from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, QDockWidget
from PySide6.QtCore import Qt
from rendering.gl_widget import GLWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Gaussian Splatting Demo")
        self.resize(1024, 768)

        # Hlavný OpenGL widget pre renderovanie
        self.gl_widget = GLWidget(self)
        self.setCentralWidget(self.gl_widget)

        # Ovládací panel (DockWidget)
        self.init_ui()
        # Vytvorenie počiatočných náhodných gaussov
        self.gl_widget.model.create_synthetic_scene(100)

    def init_ui(self):
        dock = QDockWidget("Ovládanie", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        control_panel = QWidget()
        layout = QVBoxLayout()

        # Tlačidlá pre generovanie a vyčistenie
        self.btn_generate = QPushButton("Vygenerovať náhodné (100)")
        self.btn_generate.clicked.connect(self._on_generate)
        layout.addWidget(self.btn_generate)

        self.btn_clear = QPushButton("Vyčistiť scénu")
        self.btn_clear.clicked.connect(self._on_clear)
        layout.addWidget(self.btn_clear)

        # Slider pre parameter (vizuálna mierka gaussov)
        layout.addWidget(QLabel("Mierka Gaussov:"))
        self.slider_scale = QSlider(Qt.Orientation.Horizontal)
        self.slider_scale.setRange(1, 200)
        self.slider_scale.setValue(100)
        self.slider_scale.valueChanged.connect(self._on_scale_changed)
        layout.addWidget(self.slider_scale)

        layout.addStretch()
        control_panel.setLayout(layout)

        dock.setWidget(control_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def _on_generate(self):
        self.gl_widget.model.create_synthetic_scene(100)
        self.gl_widget.update()

    def _on_clear(self):
        self.gl_widget.model.positions = None
        self.gl_widget.update()

    def _on_scale_changed(self, value):
        self.gl_widget.scale_multiplier = value / 100.0
        self.gl_widget.update()
