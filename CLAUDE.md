# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

The canonical, detailed project guide is `AGENTS.md` (architecture, every pipeline stage, CLI flags, gotchas, and planned work). It is imported here so it stays the single source of truth — update `AGENTS.md`, not this file, when project facts change.

@AGENTS.md

## Quick orientation

- **The repo is about to become a two-day training workshop.** Read "Current direction" at the top of `AGENTS.md` before any structural change. Until its teardown step runs, the CellSurvey code below is still live.

- **What it is**: CellSurvey — OME-TIFF → Sopa/SpatialData Zarr → Stardist nuclei → watershed whole-cell expansion → per-cell aggregation → k-means + Delaunay/Louvain communities → QuPath GeoJSON + plots.
- **Entry points**: `run.py` (shim: sets `TF_USE_LEGACY_KERAS=1`, preloads libstdc++, calls `cellsurvey.cli.main()`), and `python -m cellsurvey.stability` (read-only parameter sweeps over an existing `*_seg.zarr`).
- **Package modules** (`cellsurvey/`): `cli.py` (orchestration), `segmentation.py` (pixel size + nucleus→cell watershed expansion), `blob_detection.py`, `network_analysis.py`, `stability.py`, `export.py`, `utils.py`.

## Commands

```bash
pixi install                                                   # env (linux-64 GPU, win-64 CPU-only)
pixi run python run.py -i <in.ome.tiff> -o <out_prefix> -p <plot_dir>
pixi run python run.py -i <in.ome.tiff> -o <out_prefix> -p <plot_dir> --resume-from <out_prefix>.zarr   # reuse checkpoints
pixi run python -m cellsurvey.stability --zarr <out_prefix>_seg.zarr --mode communities --resolutions 0.1,0.05 --max-edge-distances 500,1000
pixi run python -m cellsurvey.stability --zarr <out_prefix>_seg.zarr --mode clusters --n-clusters 5,8,10
```

There are no tests, no linter config, no CI, and no pixi tasks defined. Verify changes by running the pipeline on a sample image (on Windows this runs Stardist on CPU and is slow).
