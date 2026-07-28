from dataclasses import dataclass
import numpy as np
from opensimplex import OpenSimplex


@dataclass
class NoiseLayer:
    frequency: float = 0.01
    amplitude: float = 1.0
    octaves: int = 4
    persistence: float = 0.5
    lacunarity: float = 2.0
    blend_mode: str = "add"  # add, multiply, subtract, max, min
    seed_offset: int = 0


def generate_layer(layer: NoiseLayer, width: int, height: int, seed: int) -> np.ndarray:
    gen = OpenSimplex(seed=seed + layer.seed_offset)
    out = np.zeros((height, width), dtype=np.float64)

    freq, amp, max_amp = layer.frequency, 1.0, 0.0
    for _ in range(layer.octaves):
        xs = np.arange(width) * freq
        ys = np.arange(height) * freq
        noise2d = np.vectorize(lambda y, x: gen.noise2(x, y))
        out += amp * noise2d(ys[:, None], xs[None, :])
        max_amp += amp
        amp *= layer.persistence
        freq *= layer.lacunarity

    out /= max_amp  # normalize to [-1, 1]
    return out * layer.amplitude


def blend(base: np.ndarray, addition: np.ndarray, mode: str) -> np.ndarray:
    if mode == "add":
        return base + addition
    if mode == "multiply":
        return base * addition
    if mode == "subtract":
        return base - addition
    if mode == "max":
        return np.maximum(base, addition)
    if mode == "min":
        return np.minimum(base, addition)
    raise ValueError(f"Unknown blend mode: {mode}")