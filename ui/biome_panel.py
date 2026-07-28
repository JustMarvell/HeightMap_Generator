from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QDoubleSpinBox,
    QLineEdit, QPushButton, QLabel, QCheckBox, QScrollArea, QColorDialog
)
from PySide6.QtGui import QColor, QPainter
from PySide6.QtCore import Signal
from core.biomes import Biome


class BiomeStrip(QWidget):
    """Gradient bar showing all enabled biomes at their actual height position."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(28)
        self._biomes: list[Biome] = []

    def set_biomes(self, biomes: list[Biome]):
        self._biomes = [b for b in biomes if b.enabled]
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(35, 35, 35))
        w, h = self.width(), self.height()
        for biome in sorted(self._biomes, key=lambda b: b.min_height):
            x0 = int(biome.min_height * w)
            x1 = int(biome.max_height * w)
            painter.fillRect(x0, 0, max(x1 - x0, 1), h, QColor(*biome.color))
        painter.end()


class BiomeRow(QFrame):
    changed = Signal()
    remove_requested = Signal(object)

    def __init__(self, biome: Biome):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self._color = QColor(*biome.color)
        self._expanded = True

        self.toggle_btn = QPushButton("▾")
        self.toggle_btn.setFixedWidth(20)
        self.toggle_btn.clicked.connect(self._toggle)

        self.color_btn = QPushButton()
        self.color_btn.setFixedWidth(28)
        self._refresh_swatch()
        self.color_btn.clicked.connect(self.pick_color)

        self.name_edit = QLineEdit(biome.name)
        self.range_label = QLabel()
        self.enabled_box = QCheckBox()
        self.enabled_box.setChecked(biome.enabled)

        remove_btn = QPushButton("×")
        remove_btn.setFixedWidth(24)
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))

        header = QHBoxLayout()
        for w in (self.toggle_btn, self.color_btn):
            header.addWidget(w)
        header.addWidget(self.name_edit, 1)
        header.addWidget(self.range_label)
        header.addWidget(self.enabled_box)
        header.addWidget(remove_btn)

        self.min_height = QDoubleSpinBox()
        self.min_height.setRange(0.0, 1.0)
        self.min_height.setSingleStep(0.01)
        self.min_height.setValue(biome.min_height)

        self.max_height = QDoubleSpinBox()
        self.max_height.setRange(0.0, 1.0)
        self.max_height.setSingleStep(0.01)
        self.max_height.setValue(biome.max_height)

        details = QHBoxLayout()
        details.addWidget(QLabel("Min"))
        details.addWidget(self.min_height)
        details.addWidget(QLabel("Max"))
        details.addWidget(self.max_height)
        self.details_widget = QWidget()
        self.details_widget.setLayout(details)

        layout = QVBoxLayout()
        layout.addLayout(header)
        layout.addWidget(self.details_widget)
        self.setLayout(layout)

        self.name_edit.textChanged.connect(lambda _: self.changed.emit())
        self.enabled_box.stateChanged.connect(lambda _: self.changed.emit())
        self.min_height.valueChanged.connect(self._on_range_changed)
        self.max_height.valueChanged.connect(self._on_range_changed)

        self._update_range_label()

    def _toggle(self):
        self._expanded = not self._expanded
        self.details_widget.setVisible(self._expanded)
        self.toggle_btn.setText("▾" if self._expanded else "▸")

    def _on_range_changed(self, _value):
        self._update_range_label()
        self.changed.emit()

    def _update_range_label(self):
        self.range_label.setText(f"{self.min_height.value():.2f}–{self.max_height.value():.2f}")

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
        self.biome_widgets: list[BiomeRow] = []

        self.strip = BiomeStrip()

        self.rows_container = QVBoxLayout()
        scroll_content = QWidget()
        scroll_content.setLayout(self.rows_container)
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
        outer.addWidget(self.strip)
        outer.addWidget(scroll)
        outer.addLayout(buttons_row)
        self.setLayout(outer)

    def add_biome(self, biome: Biome):
        row = BiomeRow(biome)
        row.changed.connect(self._on_changed)
        row.remove_requested.connect(self.remove_biome)
        self.biome_widgets.append(row)
        self._on_changed()

    def remove_biome(self, row: BiomeRow):
        if len(self.biome_widgets) <= 1:
            return  # keep at least one biome
        self.biome_widgets.remove(row)
        self.rows_container.removeWidget(row)
        row.deleteLater()
        self._on_changed()

    def _on_changed(self):
        self._resort()
        self.strip.set_biomes(self.get_biomes())
        self.biomes_changed.emit()

    def _resort(self):
        self.biome_widgets.sort(key=lambda w: w.min_height.value())
        for w in self.biome_widgets:
            self.rows_container.removeWidget(w)
        for w in self.biome_widgets:
            self.rows_container.addWidget(w)

    def set_biomes(self, biomes: list[Biome]):
        for w in self.biome_widgets:
            self.rows_container.removeWidget(w)
            w.deleteLater()
        self.biome_widgets.clear()
        for biome in biomes:
            self.add_biome(biome)

    def get_biomes(self) -> list[Biome]:
        return [w.to_biome() for w in self.biome_widgets]