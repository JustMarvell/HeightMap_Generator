import sys
import random
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QSpinBox, QDoubleSpinBox, QComboBox, QHBoxLayout, QVBoxLayout,
    QFileDialog
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QObject, QThread, Signal
from core.heightmap import build_heightmap
from core.biomes import build_biomes, colorize
from core.map_types import MAP_TYPES
from ui.noise_panel import NoisePanel
from export.exporter import save_grayscale, save_rgb

MAP_SIZE = 256


class HeightmapWorker(QObject):
    finished = Signal(np.ndarray)

    def __init__(self, layers, size, seed, use_falloff, falloff_strength):
        super().__init__()
        self.layers = layers
        self.size = size
        self.seed = seed
        self.use_falloff = use_falloff
        self.falloff_strength = falloff_strength

    def run(self):
        heightmap = build_heightmap(
            self.layers, self.size, self.size, self.seed,
            use_falloff=self.use_falloff, falloff_strength=self.falloff_strength,
        )
        self.finished.emit(heightmap)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HeightMap Generator")

        self.last_heightmap = None
        self.last_rgb = None
        self.current_map_type = next(iter(MAP_TYPES))

        self.colored_preview = QLabel()
        self.colored_preview.setFixedSize(MAP_SIZE, MAP_SIZE)
        self.preview = QLabel()
        self.preview.setFixedSize(MAP_SIZE, MAP_SIZE)

        self.map_type_box = QComboBox()
        self.map_type_box.addItems(MAP_TYPES.keys())
        self.map_type_box.currentTextChanged.connect(self.load_map_type)

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

        export_colored_btn = QPushButton("Export Colored Map")
        export_colored_btn.clicked.connect(self.export_colored)
        export_height_btn = QPushButton("Export Heightmap")
        export_height_btn.clicked.connect(self.export_heightmap)

        top_controls = QHBoxLayout()
        top_controls.addWidget(QLabel("Map Type:"))
        top_controls.addWidget(self.map_type_box)
        top_controls.addWidget(QLabel("Seed:"))
        top_controls.addWidget(self.seed_box)
        top_controls.addWidget(QLabel("Sea Level:"))
        top_controls.addWidget(self.sea_level_box)
        top_controls.addWidget(self.regen_btn)

        export_controls = QHBoxLayout()
        export_controls.addWidget(export_colored_btn)
        export_controls.addWidget(export_height_btn)

        previews = QHBoxLayout()
        previews.addWidget(self.colored_preview)
        previews.addWidget(self.preview)

        left_panel = QVBoxLayout()
        left_panel.addLayout(top_controls)
        left_panel.addLayout(previews)
        left_panel.addLayout(export_controls)
        left_widget = QWidget()
        left_widget.setLayout(left_panel)

        self.noise_panel = NoisePanel()

        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.noise_panel)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.load_map_type(self.current_map_type, regenerate=False)
        self.regenerate()

    def load_map_type(self, name: str, regenerate: bool = True):
        self.current_map_type = name
        self.noise_panel.set_layers(MAP_TYPES[name]["layers"])
        if regenerate:
            self.regenerate()

    def regenerate(self):
        preset = MAP_TYPES[self.current_map_type]
        layers = self.noise_panel.get_layers()

        self.regen_btn.setEnabled(False)
        self.regen_btn.setText("Generating...")

        self.thread = QThread()
        self.worker = HeightmapWorker(
            layers, MAP_SIZE, self.seed_box.value(),
            preset.get("use_falloff", False), preset.get("falloff_strength", 1.0),
        )
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
        self.last_rgb = colorize(self.last_heightmap, biomes)
        self.colored_preview.setPixmap(rgb_to_pixmap(self.last_rgb))

    def export_colored(self):
        if self.last_rgb is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Colored Map", "colored_map.png", "PNG Files (*.png)")
        if path:
            save_rgb(self.last_rgb, path)

    def export_heightmap(self):
        if self.last_heightmap is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Heightmap", "heightmap.png", "PNG Files (*.png)")
        if path:
            save_grayscale(self.last_heightmap, path)


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