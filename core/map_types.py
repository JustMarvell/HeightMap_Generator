from core.noise_layers import NoiseLayer

MAP_TYPES = {
    "Terrain": {
        "layers": [
            NoiseLayer(frequency=0.015, amplitude=1.0, octaves=6, persistence=0.5),
            NoiseLayer(frequency=0.06, amplitude=0.25, octaves=3, blend_mode="add"),
        ],
        "use_falloff": False,
    },
    "Island": {
        "layers": [
            NoiseLayer(frequency=0.02, amplitude=1.0, octaves=5, persistence=0.5),
            NoiseLayer(frequency=0.08, amplitude=0.2, octaves=3, blend_mode="add"),
        ],
        "use_falloff": True,
        "falloff_strength": 1.4,
    },
    "Archipelago": {
        "layers": [
            NoiseLayer(frequency=0.035, amplitude=1.0, octaves=5, persistence=0.55),
            NoiseLayer(frequency=0.1, amplitude=0.3, octaves=3, blend_mode="add"),
        ],
        "use_falloff": True,
        "falloff_strength": 0.8,
    },
    "Mountain Range": {
        "layers": [
            NoiseLayer(frequency=0.01, amplitude=1.0, octaves=6, persistence=0.6, lacunarity=2.2),
            NoiseLayer(frequency=0.05, amplitude=0.4, octaves=4, blend_mode="add"),
        ],
        "use_falloff": False,
    },
}