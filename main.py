import sys
import random
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QSpinBox, QDoubleSpinBox, QHBoxLayout, QVBoxLayout
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QObject, QThread, Signal
from core.noise_layers import NoiseLayer
from core.heightmap import build_heightmap
from core.biomes import build_biomes, colorize

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

        self.colored_preview = QLabel()
        self.colored_preview.setFixedSize(MAP_SIZE, MAP_SIZE)

        self.preview = QLabel()
        self.preview.setFixedSize(MAP_SIZE, MAP_SIZE)

        self.last_heightmap = None

        self.seed_box = QSpinBox()
        self.seed_box.setRange(0, 999_999)
        self.seed_box.setValue(random.randint(0, 999_999))

        self.sea_level_box = QDoubleSpinBox()
        self.sea_level_box.setRange(0.0, 1.0)
        self.sea_level_box.setSingleStep(0.05)
        self.sea_level_box.setValue(0.4)
        self.sea_level_box.valueChanged.connect(self.update_colored_preview)

        self.regen_btn = QPushButton("Regenerate")
        self.regen_btn.clicked.connect(self.regenerate)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Seed:"))
        controls.addWidget(self.seed_box)
        controls.addWidget(QLabel("Sea Level:"))
        controls.addWidget(self.sea_level_box)
        controls.addWidget(self.regen_btn)

        previews = QHBoxLayout()
        previews.addWidget(self.colored_preview)
        previews.addWidget(self.preview)

        layout = QVBoxLayout()
        layout.addLayout(previews)
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
        self.last_heightmap = heightmap
        self.preview.setPixmap(heightmap_to_pixmap(heightmap))
        self.update_colored_preview()
        self.regen_btn.setEnabled(True)
        self.regen_btn.setText("Regenerate")

    def update_colored_preview(self):
        if self.last_heightmap is None:
            return
        biomes = build_biomes(self.sea_level_box.value())
        rgb = colorize(self.last_heightmap, biomes)
        self.colored_preview.setPixmap(rgb_to_pixmap(rgb))

    def new_seed(self):
        self.seed_box.setValue(random.randint(0, 999_999))
        self.regenerate()


def heightmap_to_pixmap(heightmap: np.ndarray) -> QPixmap:
    gray = (heightmap * 255).astype(np.uint8)
    h, w = gray.shape
    image = QImage(gray.data, w, h, w, QImage.Format_Grayscale8)
    return QPixmap.fromImage(image.copy())


def rgb_to_pixmap(rgb: np.ndarray) -> QPixmap:
    h, w, _ = rgb.shape
    image = QImage(rgb.data, w, h, w * 3, QImage.Format_RGB888)
    return QPixmap.fromImage(image.copy())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())