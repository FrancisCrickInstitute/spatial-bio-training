# AGENTS.md

This repo holds the material for a **two-day workshop on spatial biology/omics analysis** run by the Crick: Day 1 in QuPath, Day 2 in Python. It is modelled on [introduction-to-image-analysis](https://github.com/FrancisCrickInstitute/introduction-to-image-analysis). The full plan, with rationale, is in the shared doc [Spatial Biology Workshop Plan](https://claude.ai/artifact/CnmDq3CUzc3fMptRAinEtY).

The repo began as a fork of the [CellSurvey](https://github.com/FrancisCrickInstitute/CellSurvey) pipeline. That code was removed in the teardown step (step 1), and its history stays in git. For CellSurvey's architecture, gotchas and its survey of related tools (PANORAMIC, CELESTA, Novae, segger, Spotiflow, etc.), read **upstream `AGENTS.md`**. That survey is the source material for session 8, "evaluating new tools".

## Status

**2026-11-10: step 1 (teardown) in progress on branch `restructure/teardown`.** No notebooks, data scripts or new environment exist yet. `pixi.toml` and `requirements.txt` are still CellSurvey's (Stardist/TensorFlow) until step 2 rewrites them, so don't treat them as the workshop environment.

## Decisions made
- **Keep this repo and its history.** No new repo.
- **One dataset across both days.** The preferred dataset is the 10x **Xenium Protein FFPE human renal cell carcinoma** section: transcripts, a 27-plex protein panel and post-Xenium H&E, all on the same section. The fallback is BioImage Archive **S-BIAD1093** (Xenium + COMET IF, but no H&E). A cropped region is published on Zenodo as the workshop download.
- **Day 1 = the existing one-day Introduction to QuPath course** (Sara Salgueiro Torres, CALM STP, QuPath v0.7; source material in `qupath_content/`), ported to the workshop dataset. **No Groovy scripting**: Python is the only scripting language taught. Session 4 becomes spatial analysis (density maps, distances, Delaunay) plus export for Day 2.
- **InstanSeg on both days**: QuPath's InstanSeg extension on Day 1, and `sopa.segmentation.instanseg` (Sopa ≥ 2.3, `sopa[instanseg]`) on Day 2, using the same `fluorescence_nuclei_and_cells` model. Pass `pixel_size`, or it may return no cells. The workshop environment needs **no TensorFlow**.
- **Notebooks only for Day 2.** Session 8 points to upstream CellSurvey as the "notebooks → pipeline" example.
- **Distances in µm**, matching upstream CellSurvey (which converted its spatial parameters to µm on `feature/instanseg`).
- **No bring-your-own-data session.** Applications capture participants' projects and goals. The workshop teaches tool choice and how to ask the right questions, not analysis of attendees' own data.
- **Compute is still open.** The design assumes precomputed checkpoints (one SpatialData Zarr per notebook in the download), so most of Day 2 runs on modest hardware. Live segmentation runs on one small tile only.

## Programme (4 sessions/day, 09:30–17:00)
| Day 1 (QuPath) | Day 2 (Python) |
|---|---|
| 1. Images + spatial-biology primer | 5. Notebooks, SpatialData/AnnData, loading Xenium + H&E + Day 1 GeoJSON |
| 2. H&E workflow (tissue, regions, cells) | 6. Segmentation (InstanSeg via Sopa) + QC (SegTraQ, vs Xenium segmentation) + aggregation |
| 3. Multiplex IF workflow (InstanSeg, classifiers, phenotypes) | 7. Cell types (scanpy; compare with Day 1 phenotypes; RNA vs protein) |
| 4. Spatial analysis + export | 8. Spatial stats/niches (squidpy, Delaunay + Louvain), back to QuPath, evaluating new tools |

The participant-facing version of this programme is in `README.md`. Keep the two in step.

## Target layout
```
README.md            workshop page (overview, registration, instructors, preparation, programme, venue, slides, FAQ)
Pages/               Installation-Instructions.md, Data.md, Day1/ (session guides), Day2/
qupath/              Day 1 classifiers + class lists (the project itself ships in the data download)
notebooks/           05_data_model_and_loading … 08_spatial_and_next_steps
solutions/           completed notebooks with outputs
Scripts/             prepare_data.py (download, crop, checkpoints), check_install.py
assets/
pixi.toml
```

`assets/` still holds two CellSurvey output figures. They can be replaced once the workshop data produces its own.

## Large and private files
- `qupath_content/` (the original QuPath course) is **gitignored**. Copy only classifiers and class lists from it into `qupath/`.
- Never commit the 80 MB slide deck (slides live on Google Drive) or the QuPath project `data/` folders (~450 MB). The `.qpproj` files store absolute paths from the author's machine, and the projects will be rebuilt on the RCC data.
- Workshop data never goes in git. It is downloaded by `Scripts/prepare_data.py` or from the Zenodo bundle.

## Order of work
0. **Upstream first**: **done on `feature/instanseg`** in upstream CellSurvey (2026-11-10). Merge to upstream `main` is pending final tests. Adds `--segmenter instanseg`, requires `sopa>=2.3.0`, separates TensorFlow/Stardist and PyTorch/InstanSeg into separate pixi environments, and converts spatial distances to µm.
1. **Teardown** (in progress): remove the CellSurvey files, write a README skeleton, slim down `AGENTS.md`/`CLAUDE.md`.
2. **Environment**: new `pixi.toml` (`sopa[instanseg]`, `spatialdata-io`, `squidpy`, `napari-spatialdata`, `jupyterlab`, SegTraQ; no TensorFlow) and `Scripts/check_install.py`, solved and tested on win-64 and linux-64. Replace `requirements.txt` to match (or drop it if Binder isn't used).
3. **Data**: `Scripts/prepare_data.py`. Blocked on confirming the RCC licence and choosing the crop.
4. **Day 2 notebooks**: 06 first (riskiest), then 05, 07, 08.
5. **Day 1**: port the QuPath exercises to the RCC data and write the `Pages/Day1/` guides (QuPath GUI work, led by the instructors).

## Open questions
- Confirm the RCC dataset's licence (expected CC BY 4.0), file list, and that its protein panel can carry the Day 1 IF exercise (e.g. CD45, PD-1).
- Can QuPath import Xenium transcripts and cell boundaries cleanly? This decides whether transcripts appear on Day 1.
- Crop region and size; compute platform; cohort size and dates.
- Source and sharing terms of the original liver `.vsi` and `LungImg1.ome.tif` course images.
