import numpy as np
from core.noise_layers import NoiseLayer, generate_layer, blend


def build_heightmap(
    layers: list[NoiseLayer], width: int, height: int, seed: int,
    use_falloff: bool = False, falloff_strength: float = 1.0,
) -> np.ndarray:
    result = np.zeros((height, width), dtype=np.float64)
    for layer in layers:
        result = blend(result, generate_layer(layer, width, height, seed), layer.blend_mode)
    result = normalize(result)
    if use_falloff:
        mask = generate_falloff_mask(width, height, falloff_strength)
        result = np.clip(result - mask, 0.0, 1.0)
        result = normalize(result)
    return result


def generate_falloff_mask(width: int, height: int, strength: float = 1.0) -> np.ndarray:
    """Radial gradient, 0 at center rising toward 1 at the edges — pulls land down into water."""
    y, x = np.indices((height, width))
    cx, cy = width / 2, height / 2
    dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    max_dist = np.sqrt(cx ** 2 + cy ** 2)
    return np.clip((dist / max_dist) ** 2 * strength, 0.0, 1.0)


def normalize(arr: np.ndarray) -> np.ndarray:
    lo, hi = arr.min(), arr.max()
    if hi - lo < 1e-9:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def apply_sea_level(heightmap: np.ndarray, sea_level: float) -> np.ndarray:
    """Returns a boolean land mask: True where above sea_level."""
    return heightmap >= sea_level