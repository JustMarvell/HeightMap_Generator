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


def colorize(heightmap: np.ndarray, biomes: list[Biome]) -> np.ndarray:
    h, w = heightmap.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    for biome in biomes:
        mask = (heightmap >= biome.min_height) & (heightmap <= biome.max_height)
        rgb[mask] = biome.color
    return rgb