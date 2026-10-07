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

    def init_ui(self):
        dock = QDockWidget("Ovládanie", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        
        control_panel = QWidget()
        layout = QVBoxLayout()

        # Tlačidlo pre načítanie modelu (zatiaľ placeholder)
        self.btn_load = QPushButton("Načítať model")
        layout.addWidget(self.btn_load)

        # Slider pre parameter (napr. vizuálna mierka gaussov)
        layout.addWidget(QLabel("Mierka Gaussov:"))
        self.slider_scale = QSlider(Qt.Orientation.Horizontal)
        self.slider_scale.setRange(1, 100)
        self.slider_scale.setValue(50)
        layout.addWidget(self.slider_scale)

        layout.addStretch()
        control_panel.setLayout(layout)
        
        dock.setWidget(control_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
