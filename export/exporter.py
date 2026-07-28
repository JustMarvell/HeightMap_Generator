from PIL import Image
import numpy as np


def save_grayscale(heightmap: np.ndarray, path: str):
    Image.fromarray((heightmap * 255).astype(np.uint8), mode="L").save(path)


def save_rgb(rgb: np.ndarray, path: str):
    Image.fromarray(rgb, mode="RGB").save(path)