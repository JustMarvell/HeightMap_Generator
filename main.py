import sys
import random
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QSpinBox, QHBoxLayout, QVBoxLayout
)
from PySide6.QtGui import QPixmap, QImage
from core.noise_layers import NoiseLayer
from core.heightmap import build_heightmap

MAP_SIZE = 256


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HeightMap Generator")

        self.preview = QLabel()
        self.preview.setFixedSize(MAP_SIZE, MAP_SIZE)

        self.seed_box = QSpinBox()
        self.seed_box.setRange(0, 999_999)
        self.seed_box.setValue(random.randint(0, 999_999))

        regen_btn = QPushButton("Regenerate")
        regen_btn.clicked.connect(self.regenerate)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Seed:"))
        controls.addWidget(self.seed_box)
        controls.addWidget(regen_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.preview)
        layout.addLayout(controls)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.regenerate()

    def regenerate(self):
        layers = [
            NoiseLayer(frequency=0.02, amplitude=1.0, octaves=5),
            NoiseLayer(frequency=0.08, amplitude=0.3, octaves=3, blend_mode="add"),
        ]
        heightmap = build_heightmap(layers, MAP_SIZE, MAP_SIZE, self.seed_box.value())
        self.preview.setPixmap(heightmap_to_pixmap(heightmap))

    def new_seed(self):
        self.seed_box.setValue(random.randint(0, 999_999))
        self.regenerate()


def heightmap_to_pixmap(heightmap: np.ndarray) -> QPixmap:
    gray = (heightmap * 255).astype(np.uint8)
    h, w = gray.shape
    image = QImage(gray.data, w, h, w, QImage.Format_Grayscale8)
    return QPixmap.fromImage(image.copy())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())