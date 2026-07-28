from dataclasses import dataclass
import numpy as np

# (name, color, band_start, band_end) — band values are fractions of their region (water or land)
_WATER_BANDS = [
    ("Deep Water", (20, 60, 140), 0.0, 0.5),
    ("Shallow Water", (50, 110, 200), 0.5, 1.0),
]
_LAND_BANDS = [
    ("Sand", (230, 220, 170), 0.00, 0.08),
    ("Grass", (90, 160, 60), 0.08, 0.35),
    ("Forest", (40, 100, 40), 0.35, 0.65),
    ("Mountain", (120, 110, 100), 0.65, 0.85),
    ("Snow", (245, 245, 250), 0.85, 1.00),
]


@dataclass
class Biome:
    name: str
    color: tuple[int, int, int]
    min_height: float
    max_height: float
    enabled: bool = True


def build_biomes(sea_level: float) -> list[Biome]:
    biomes = [
        Biome(name, color, sea_level * lo, sea_level * hi)
        for name, color, lo, hi in _WATER_BANDS
    ]
    land_span = 1.0 - sea_level
    biomes += [
        Biome(name, color, sea_level + lo * land_span, sea_level + hi * land_span)
        for name, color, lo, hi in _LAND_BANDS
    ]
    return biomes


def colorize(heightmap: np.ndarray, biomes: list[Biome], blend: bool = False) -> np.ndarray:
    enabled = [b for b in biomes if b.enabled]
    h, w = heightmap.shape
    if not enabled:
        return np.zeros((h, w, 3), dtype=np.uint8)

    if not blend:
        rgb = np.zeros((h, w, 3), dtype=np.uint8)
        for biome in enabled:
            mask = (heightmap >= biome.min_height) & (heightmap <= biome.max_height)
            rgb[mask] = biome.color
        return rgb

    return _colorize_blended(heightmap, enabled)


def _colorize_blended(heightmap: np.ndarray, enabled: list[Biome]) -> np.ndarray:
    """Smooth gradient across biome bands using each band's midpoint as a color control point."""
    ordered = sorted(enabled, key=lambda b: b.min_height)
    control_x = [0.0] + [(b.min_height + b.max_height) / 2 for b in ordered] + [1.0]
    control_x[0] = min(control_x[0], control_x[1])  # keep strictly non-decreasing for np.interp
    control_x[-1] = max(control_x[-1], control_x[-2])

    flat = heightmap.ravel()
    channels = []
    for c in range(3):
        control_y = [ordered[0].color[c]] + [b.color[c] for b in ordered] + [ordered[-1].color[c]]
        channels.append(np.interp(flat, control_x, control_y))

    h, w = heightmap.shape
    return np.stack(channels, axis=-1).reshape(h, w, 3).astype(np.uint8)