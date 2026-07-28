# HeightMap_Generator

A desktop GUI app for procedurally generating 2D map textures — islands, archipelagos, terrains, and mountain ranges — with live preview of both the colored (biome) map and the raw heightmap, plus export to image files.

## Overview

HeightMap_Generator builds a heightmap from configurable noise layers, applies a sea level threshold, and paints the result with customizable biomes based on height. Both the colored map and the grayscale heightmap update in a live preview panel, and each can be exported independently as a PNG.

## Features

- **Window-based GUI** (PySide6) — live preview of colored map and heightmap side by side
- **Map types**: Terrain, Island, Archipelago, Mountain Range — selectable via dropdown, each loading its own default noise layers (Island/Archipelago also apply a radial falloff mask so land tapers into water toward the edges)
- **Noise system**:
  - Seed control (manual or random)
  - Add / remove / reorder noise layers, editable live in the UI
  - Per-layer: frequency, amplitude, octaves, persistence, lacunarity, blend mode (add/multiply/subtract/max/min)
  - Currently uses OpenSimplex only (no per-layer noise-type switch yet)
- **Sea level**: adjustable threshold, used to seed the default biome bands via "Reset to Defaults"
- **Biome system**:
  - Add/remove custom biomes with name, color (color picker), and height range (min/max)
  - Enable/disable individual biomes without deleting them
  - "Blend Biomes" toggle — smooth gradient transitions between bands instead of hard cutoffs
  - "Reset to Defaults" regenerates the default 7-biome set (water/sand/grass/forest/mountain/snow) from the current sea level
- **Auto-update**: optional toggle that regenerates the heightmap automatically (debounced) as noise layer parameters or seed change, instead of requiring a manual click
- **Export**:
  - Export colored biome map as PNG
  - Export grayscale heightmap as PNG

## Tech Stack

| Component | Choice |
|---|---|
| Language | Python 3.12 |
| GUI Framework | PySide6 (Qt for Python) |
| Numerical / heightmap math | numpy |
| Noise generation | opensimplex |
| Image building / export | Pillow (PIL) |
| Environment | venv + requirements.txt |

## Project Structure

```
HeightMap_Generator/
├── venv/                   # virtual environment (not committed)
├── requirements.txt
├── README.md
├── main.py                 # app entry point + main window, worker thread, previews
├── core/
│   ├── noise_layers.py     # NoiseLayer definition, noise generation, blend modes
│   ├── heightmap.py        # heightmap build/normalize, radial falloff mask
│   ├── biomes.py           # Biome definition, default presets, hard/blended colorization
│   └── map_types.py        # Terrain/Island/Archipelago/Mountain Range presets
├── ui/
│   ├── noise_panel.py      # editable noise layer list (add/remove/reorder/params)
│   └── biome_panel.py      # editable biome list (add/remove/color/range/enable)
└── export/
    └── exporter.py         # PNG export for colored map and heightmap
```

> `ui/main_window.py` and `ui/preview_panel.py` from the original proposed structure haven't been split out yet — that logic currently lives in `main.py`.

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

## requirements.txt

```
PySide6
numpy
opensimplex
Pillow
```

## Current Behavior

A running desktop window where the user can:
1. Pick a map type from the dropdown to load its default noise layers.
2. Edit noise layers (add/remove/reorder/tweak params) and regenerate manually, or enable Auto-update to regenerate automatically after a short pause in editing.
3. Edit biomes (add/remove/recolor/resize/enable/disable) and toggle blending — recolors instantly without regenerating the heightmap.
4. Export the colored map and/or heightmap as PNG files via file dialogs.

## Status

✅ Core feature set from the original plan is implemented and working: noise layers, sea level, biome system, map type presets, PNG export, and an auto-update toggle.

🚧 Remaining/open items:
- **Performance**: noise generation (`core/noise_layers.py`) uses `np.vectorize` over `opensimplex`'s per-pixel API, which is correct but slow — noticeable at higher octave counts or resolutions above the current 256×256 default. A batch/array-based noise call would be faster.
- **Known issue — Auto-update overlap**: rapid parameter changes (e.g. fast spinbox scrolling) while Auto-update is on can still occasionally overlap generation requests despite the pending-regeneration guard, causing instability. Current workaround: the auto-update debounce delay in `main.py` (`AUTO_UPDATE_DELAY_MS`) has been raised to reduce how often this triggers. Root cause (thread lifecycle under rapid re-entry) not yet fully resolved.
- Per-layer noise type selection (only OpenSimplex is implemented; `noise` library or others not yet wired in)
- No moisture/multi-factor biome assignment (biomes are height-only)
- `ui/main_window.py` / `ui/preview_panel.py` split from `main.py` not yet done

## Notes

- Target device: Linux Zorin OS, Ryzen 5 6600H, 16GB RAM, Radeon 660M — no heavy GPU compute assumed; generation relies on CPU-bound numpy operations.
- Current default preview resolution is 256×256 (`MAP_SIZE` in `main.py`).