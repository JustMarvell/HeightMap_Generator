import sys
import random
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QSpinBox, QHBoxLayout, QVBoxLayout
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QObject, QThread, Signal
from core.noise_layers import NoiseLayer
from core.heightmap import build_heightmap

MAP_SIZE = 256


class HeightmapWorker(QObject):
    finished = Signal(np.ndarray)

    def __init__(self, layers, size, seed):
        super().__init__()
        self.layers = layers
        self.size = size
        self.seed = seed

    def run(self):
        heightmap = build_heightmap(self.layers, self.size, self.size, self.seed)
        self.finished.emit(heightmap)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HeightMap Generator")

        self.preview = QLabel()
        self.preview.setFixedSize(MAP_SIZE, MAP_SIZE)

        self.seed_box = QSpinBox()
        self.seed_box.setRange(0, 999_999)
        self.seed_box.setValue(random.randint(0, 999_999))

        self.regen_btn = QPushButton("Regenerate")
        self.regen_btn.clicked.connect(self.regenerate)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Seed:"))
        controls.addWidget(self.seed_box)
        controls.addWidget(self.regen_btn)

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
        self.regen_btn.setEnabled(False)
        self.regen_btn.setText("Generating...")

        self.thread = QThread()
        self.worker = HeightmapWorker(layers, MAP_SIZE, self.seed_box.value())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_heightmap_ready)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_heightmap_ready(self, heightmap: np.ndarray):
        self.preview.setPixmap(heightmap_to_pixmap(heightmap))
        self.regen_btn.setEnabled(True)
        self.regen_btn.setText("Regenerate")

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