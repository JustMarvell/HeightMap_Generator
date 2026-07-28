from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QDoubleSpinBox,
    QLineEdit, QPushButton, QLabel, QCheckBox, QScrollArea, QColorDialog
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal
from core.biomes import Biome


class BiomeWidget(QGroupBox):
    changed = Signal()

    def __init__(self, biome: Biome, on_remove):
        super().__init__()
        self._color = QColor(*biome.color)

        self.name_edit = QLineEdit(biome.name)
        self.enabled_box = QCheckBox("Enabled")
        self.enabled_box.setChecked(biome.enabled)

        self.color_btn = QPushButton()
        self.color_btn.setFixedWidth(50)
        self._refresh_swatch()
        self.color_btn.clicked.connect(self.pick_color)

        self.min_height = QDoubleSpinBox()
        self.min_height.setRange(0.0, 1.0)
        self.min_height.setSingleStep(0.01)
        self.min_height.setValue(biome.min_height)

        self.max_height = QDoubleSpinBox()
        self.max_height.setRange(0.0, 1.0)
        self.max_height.setSingleStep(0.01)
        self.max_height.setValue(biome.max_height)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: on_remove(self))

        top_row = QHBoxLayout()
        top_row.addWidget(self.name_edit)
        top_row.addWidget(self.color_btn)
        top_row.addWidget(self.enabled_box)

        range_row = QHBoxLayout()
        range_row.addWidget(QLabel("Min"))
        range_row.addWidget(self.min_height)
        range_row.addWidget(QLabel("Max"))
        range_row.addWidget(self.max_height)

        layout = QVBoxLayout()
        layout.addLayout(top_row)
        layout.addLayout(range_row)
        layout.addWidget(remove_btn)
        self.setLayout(layout)

        self.name_edit.textChanged.connect(lambda _: self.changed.emit())
        self.enabled_box.stateChanged.connect(lambda _: self.changed.emit())
        self.min_height.valueChanged.connect(lambda _: self.changed.emit())
        self.max_height.valueChanged.connect(lambda _: self.changed.emit())

    def pick_color(self):
        color = QColorDialog.getColor(self._color, self, "Choose Biome Color")
        if color.isValid():
            self._color = color
            self._refresh_swatch()
            self.changed.emit()

    def _refresh_swatch(self):
        self.color_btn.setStyleSheet(f"background-color: {self._color.name()};")

    def to_biome(self) -> Biome:
        return Biome(
            name=self.name_edit.text() or "Biome",
            color=(self._color.red(), self._color.green(), self._color.blue()),
            min_height=self.min_height.value(),
            max_height=self.max_height.value(),
            enabled=self.enabled_box.isChecked(),
        )


class BiomePanel(QWidget):
    biomes_changed = Signal()
    reset_requested = Signal()

    def __init__(self):
        super().__init__()
        self.biome_widgets: list[BiomeWidget] = []

        self.biomes_container = QVBoxLayout()
        scroll_content = QWidget()
        scroll_content.setLayout(self.biomes_container)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_content)

        add_btn = QPushButton("Add Biome")
        add_btn.clicked.connect(lambda: self.add_biome(Biome("New Biome", (128, 128, 128), 0.0, 1.0)))

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_requested.emit)

        buttons_row = QHBoxLayout()
        buttons_row.addWidget(add_btn)
        buttons_row.addWidget(reset_btn)

        outer = QVBoxLayout()
        outer.addWidget(QLabel("Biomes"))
        outer.addWidget(scroll)
        outer.addLayout(buttons_row)
        self.setLayout(outer)

    def add_biome(self, biome: Biome):
        widget = BiomeWidget(biome, self.remove_biome)
        widget.changed.connect(self.biomes_changed.emit)
        self.biome_widgets.append(widget)
        self.biomes_container.addWidget(widget)
        self.biomes_changed.emit()

    def remove_biome(self, widget: BiomeWidget):
        if len(self.biome_widgets) <= 1:
            return  # keep at least one biome
        self.biome_widgets.remove(widget)
        self.biomes_container.removeWidget(widget)
        widget.deleteLater()
        self.biomes_changed.emit()

    def set_biomes(self, biomes: list[Biome]):
        for widget in self.biome_widgets:
            self.biomes_container.removeWidget(widget)
            widget.deleteLater()
        self.biome_widgets.clear()
        for biome in biomes:
            self.add_biome(biome)

    def get_biomes(self) -> list[Biome]:
        return [w.to_biome() for w in self.biome_widgets]