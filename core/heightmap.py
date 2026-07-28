import numpy as np
from core.noise_layers import NoiseLayer, generate_layer, blend


def build_heightmap(layers: list[NoiseLayer], width: int, height: int, seed: int) -> np.ndarray:
    result = np.zeros((height, width), dtype=np.float64)
    for layer in layers:
        result = blend(result, generate_layer(layer, width, height, seed), layer.blend_mode)
    return normalize(result)


def normalize(arr: np.ndarray) -> np.ndarray:
    lo, hi = arr.min(), arr.max()
    if hi - lo < 1e-9:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def apply_sea_level(heightmap: np.ndarray, sea_level: float) -> np.ndarray:
    """Returns a boolean land mask: True where above sea_level."""
    return heightmap >= sea_level