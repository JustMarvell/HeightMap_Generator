from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QDoubleSpinBox,
    QSpinBox, QComboBox, QPushButton, QLabel, QScrollArea
)
from core.noise_layers import NoiseLayer

BLEND_MODES = ["add", "multiply", "subtract", "max", "min"]


class NoiseLayerWidget(QGroupBox):
    def __init__(self, layer: NoiseLayer, on_remove, on_move_up, on_move_down):
        super().__init__("Noise Layer")

        self.frequency = QDoubleSpinBox()
        self.frequency.setRange(0.001, 1.0)
        self.frequency.setSingleStep(0.005)
        self.frequency.setDecimals(3)
        self.frequency.setValue(layer.frequency)

        self.amplitude = QDoubleSpinBox()
        self.amplitude.setRange(0.0, 5.0)
        self.amplitude.setSingleStep(0.05)
        self.amplitude.setValue(layer.amplitude)

        self.octaves = QSpinBox()
        self.octaves.setRange(1, 10)
        self.octaves.setValue(layer.octaves)

        self.persistence = QDoubleSpinBox()
        self.persistence.setRange(0.0, 1.0)
        self.persistence.setSingleStep(0.05)
        self.persistence.setValue(layer.persistence)

        self.lacunarity = QDoubleSpinBox()
        self.lacunarity.setRange(1.0, 4.0)
        self.lacunarity.setSingleStep(0.1)
        self.lacunarity.setValue(layer.lacunarity)

        self.blend_mode = QComboBox()
        self.blend_mode.addItems(BLEND_MODES)
        self.blend_mode.setCurrentText(layer.blend_mode)

        form = QVBoxLayout()
        for label, widget in [
            ("Frequency", self.frequency), ("Amplitude", self.amplitude),
            ("Octaves", self.octaves), ("Persistence", self.persistence),
            ("Lacunarity", self.lacunarity), ("Blend Mode", self.blend_mode),
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(widget)
            form.addLayout(row)

        buttons = QHBoxLayout()
        up_btn, down_btn, remove_btn = QPushButton("↑"), QPushButton("↓"), QPushButton("Remove")
        up_btn.clicked.connect(lambda: on_move_up(self))
        down_btn.clicked.connect(lambda: on_move_down(self))
        remove_btn.clicked.connect(lambda: on_remove(self))
        buttons.addWidget(up_btn)
        buttons.addWidget(down_btn)
        buttons.addWidget(remove_btn)
        form.addLayout(buttons)

        self.setLayout(form)

    def to_layer(self) -> NoiseLayer:
        return NoiseLayer(
            frequency=self.frequency.value(),
            amplitude=self.amplitude.value(),
            octaves=self.octaves.value(),
            persistence=self.persistence.value(),
            lacunarity=self.lacunarity.value(),
            blend_mode=self.blend_mode.currentText(),
        )


class NoisePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layer_widgets: list[NoiseLayerWidget] = []

        self.layers_container = QVBoxLayout()
        scroll_content = QWidget()
        scroll_content.setLayout(self.layers_container)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_content)

        add_btn = QPushButton("Add Layer")
        add_btn.clicked.connect(lambda: self.add_layer(NoiseLayer()))

        outer = QVBoxLayout()
        outer.addWidget(QLabel("Noise Layers"))
        outer.addWidget(scroll)
        outer.addWidget(add_btn)
        self.setLayout(outer)

    def add_layer(self, layer: NoiseLayer):
        widget = NoiseLayerWidget(layer, self.remove_layer, self.move_up, self.move_down)
        self.layer_widgets.append(widget)
        self.layers_container.addWidget(widget)

    def remove_layer(self, widget: NoiseLayerWidget):
        if len(self.layer_widgets) <= 1:
            return  # keep at least one layer
        self.layer_widgets.remove(widget)
        self.layers_container.removeWidget(widget)
        widget.deleteLater()

    def move_up(self, widget: NoiseLayerWidget):
        idx = self.layer_widgets.index(widget)
        if idx > 0:
            self.layer_widgets[idx - 1], self.layer_widgets[idx] = self.layer_widgets[idx], self.layer_widgets[idx - 1]
            self._refresh_layout()

    def move_down(self, widget: NoiseLayerWidget):
        idx = self.layer_widgets.index(widget)
        if idx < len(self.layer_widgets) - 1:
            self.layer_widgets[idx + 1], self.layer_widgets[idx] = self.layer_widgets[idx], self.layer_widgets[idx + 1]
            self._refresh_layout()

    def _refresh_layout(self):
        for widget in self.layer_widgets:
            self.layers_container.removeWidget(widget)
        for widget in self.layer_widgets:
            self.layers_container.addWidget(widget)

    def set_layers(self, layers: list[NoiseLayer]):
        for widget in self.layer_widgets:
            self.layers_container.removeWidget(widget)
            widget.deleteLater()
        self.layer_widgets.clear()
        for layer in layers:
            self.add_layer(layer)

    def get_layers(self) -> list[NoiseLayer]:
        return [w.to_layer() for w in self.layer_widgets]