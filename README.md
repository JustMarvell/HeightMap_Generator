# HeightMap_Generator

A desktop GUI app for procedurally generating 2D map textures — islands, archipelagos, terrains, and mountain ranges — with live preview of both the colored (biome) map and the raw heightmap, plus export to image files.

## Overview

HeightMap_Generator lets you build a heightmap from configurable noise layers, apply a sea level threshold, and paint the result with customizable biomes based on height (and optionally other factors like moisture, if added later). Both the colored map and the grayscale heightmap update in a live preview panel, and each can be exported independently as a texture.

## Features

- **Window-based GUI** (not a terminal app) — real-time preview of colored map and heightmap side by side
- **Map types** (toggleable/switchable): Island, Archipelago, Terrain, Mountain Range, etc.
- **Noise system**:
  - Seed control (manual or random)
  - Add / remove / reorder multiple noise layers
  - Per-layer customization (noise type, frequency, amplitude, octaves, persistence, lacunarity, blend mode)
- **Sea level** control (adjustable threshold that defines land vs. water)
- **Biome system**:
  - Create/add custom biomes with assigned colors
  - Choose which biomes are included/excluded from generation
  - Configure biome height ranges / assignment rules
  - Biome blending controls (smooth transitions between biome bands)
- **Export**:
  - Download colored map texture (PNG)
  - Download heightmap texture (PNG, grayscale)

## Tech Stack

| Component | Choice |
|---|---|
| Language | Python 3.12 |
| GUI Framework | PySide6 (Qt for Python) |
| Numerical / heightmap math | numpy |
| Noise generation | opensimplex (or `noise` library) |
| Image building / export | Pillow (PIL) |
| Environment | venv + requirements.txt |

> Framework rationale: PySide6 was chosen over Tkinter (too limited for real-time image/canvas-heavy UIs) and over PyQt6 (GPL-licensed; PySide6 is LGPL and more permissive).

## Project Structure (proposed)

```
HeightMap_Generator/
├── venv/                   # virtual environment (not committed)
├── requirements.txt
├── README.md
├── main.py                 # app entry point
├── core/
│   ├── noise_layers.py     # noise layer generation & stacking
│   ├── heightmap.py        # heightmap build/combine logic
│   ├── biomes.py           # biome definitions, assignment, blending
│   └── map_types.py        # island/archipelago/terrain/mountain presets
├── ui/
│   ├── main_window.py      # main window layout
│   ├── preview_panel.py    # colored map + heightmap preview widgets
│   ├── noise_panel.py      # noise layer controls
│   └── biome_panel.py      # biome editor controls
└── export/
    └── exporter.py         # PNG export for map/heightmap
```

## Setup Instructions

1. **Clone/create the project folder**
   ```bash
   mkdir HeightMap_Generator && cd HeightMap_Generator
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   python main.py
   ```

## requirements.txt (initial)

```
PySide6
numpy
opensimplex
Pillow
```

> Add any new package used during development to `requirements.txt` (e.g. via `pip freeze > requirements.txt` or manually).

## Expected Result

A running desktop window where the user can:
1. Pick a map type and adjust generation parameters (seed, noise layers, sea level).
2. See the heightmap and colored biome map update live in preview panels.
3. Add/edit biomes and control how they blend across height bands.
4. Click a button to export the colored texture and/or the heightmap texture as PNG files.

## Status

🚧 Planning stage — architecture and feature set defined, implementation not yet started.

## Notes

- Target device: Linux Zorin OS, Ryzen 5 6600H, 16GB RAM, Radeon 660M — no heavy GPU compute assumed; generation should rely on CPU-bound numpy operations, keep to reasonable map resolutions for real-time preview responsiveness.