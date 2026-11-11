# AGENTS.md

This repo holds the material for a **two-day workshop on spatial biology/omics analysis** run by the Crick: Day 1 in QuPath, Day 2 in Python. It is modelled on [introduction-to-image-analysis](https://github.com/FrancisCrickInstitute/introduction-to-image-analysis). The full plan, with rationale, is in the shared doc [Spatial Biology Workshop Plan](https://claude.ai/artifact/CnmDq3CUzc3fMptRAinEtY).

The repo began as a fork of the [CellSurvey](https://github.com/FrancisCrickInstitute/CellSurvey) pipeline. That code was removed in the teardown step (step 1), and its history stays in git. For CellSurvey's architecture, gotchas and its survey of related tools (PANORAMIC, CELESTA, Novae, segger, Spotiflow, etc.), read **upstream `AGENTS.md`**. That survey is the source material for session 8, "evaluating new tools".

## Status

**2026-11-11: steps 1 (teardown) and 2 (environment) done and merged into `main`.** No notebooks or data scripts exist yet.

The workshop environment is `pixi.toml` + `pixi.lock`, locked for linux-64, win-64 and osx-arm64. It uses Python 3.12, `sopa[instanseg]` 2.3, PyTorch, `spatialdata` 0.8, scanpy, squidpy, SegTraQ, napari (PyQt6) and JupyterLab, with no TensorFlow. Tasks:
- `pixi run check` runs `Scripts/check_install.py`: imports, versions, compute device, Qt.
- `pixi run check-full` also downloads the InstanSeg model and segments a synthetic image.
- `pixi run lab` starts JupyterLab.

`requirements.txt` mirrors the PyPI deps for pip users, so keep it in step with `pixi.toml`. `pixi run check-full` passes on win-64 (CPU) and on linux-64 (CUDA, NVIDIA A100 on the Crick HPC, 2026-11-11), including the InstanSeg model download. osx-arm64 is locked but untested. On the HPC, pixi warns that its cache is on a network filesystem and redirects it to `/tmp`. This is harmless. On networks or VPNs that intercept HTTPS, pixi and the InstanSeg model download can fail with certificate errors (`UnknownIssuer` / `CERTIFICATE_VERIFY_FAILED`). `Pages/Installation-Instructions.md` covers this.

## Working in this repo
- **This is a training-workshop repo, not a software package.** There is no build, no tests and no CI. Day 2 material will be Jupyter notebooks, and nothing here is meant to be imported.
- **Don't restore the CellSurvey code.** Point to upstream [CellSurvey](https://github.com/FrancisCrickInstitute/CellSurvey) instead. An `upstream` git remote (SSH; HTTPS fails certificate checks on the maintainer's machine) may be configured for fetching it.
- **Keep participant-facing text and the plan in step.** The programme in `README.md` mirrors the table below.
- **The maintainer stages and commits.** Leave changes unstaged.

## Decisions made
- **Keep this repo and its history.** No new repo.
- **One dataset across both days.** The preferred dataset is the 10x **Xenium Protein FFPE human renal cell carcinoma** (RCC) section: transcripts, a 27-plex protein panel and post-Xenium H&E, all on the same section. Desk research on 2026-11-11 found it suitable (see Dataset below), pending two hands-on tests. The fallback is BioImage Archive **S-BIAD1093** (Xenium + COMET IF, but no H&E). A cropped region is published on Zenodo as the workshop download.
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

## Dataset: 10x Xenium Protein FFPE human RCC (researched 2026-11-11)
[Dataset page](https://www.10xgenomics.com/datasets/xenium-protein-ffpe-human-renal-carcinoma). The page title is "Xenium In Situ Gene and Protein Expression data for FFPE Human Renal Cell Carcinoma". It was analysed with Xenium Onboard Analysis (XOA) v4.0 and last replaced on 2025-09-25. Don't confuse it with the separate 10x ccRCC protein dataset (`xenium-protein-ffpe-human-renal-ccrcc`), which hasn't been checked.

- **Licence: CC BY 4.0**, stated on the page. Redistributing a crop on Zenodo is fine with attribution (follow 10x's citation guidelines).
- **Sample:** FFPE RCC, stage III (T3a N1 MX), from Discovery Life Sciences. It has 465,534 cells over 66 mm² (about 7,000 cells/mm²) and a median of 70 transcripts per cell.
- **RNA:** the 377-gene Xenium Human Multi-Tissue and Cancer panel plus 28 custom genes.
- **Protein:** the 27-plex Cell Typing & Functional State Marker Set. Each marker is a separate OME-TIFF in `morphology_focus/` (35 files including DAPI, the segmentation stains and background channels).
  - Immune cells: CD3E, CD4, CD8A, CD20, CD138, HLA-DR, CD11c, CD68, CD16, Granzyme B, CD163.
  - Immune checkpoints: PD-1, PD-L1, VISTA, LAG-3.
  - Proliferation and differentiation: Ki-67, PCNA, CD45RA, CD45RO.
  - Tumour: PanCK, β-catenin, PTEN, CD31.
  - Segmentation stains, also as separate channels: CD45, E-cadherin, Vimentin, αSMA.
  - This is enough for the Day 1 IF exercise (T-cell subsets, macrophages, PD-1/PD-L1, tumour vs stroma).
- **XOA 4.0 adds a fixed +100 offset to protein pixel values** instead of allowing negative values after background subtraction. Account for it when measuring intensities.
- **Downloads.** All are on `cf.10xgenomics.com/samples/xenium/4.0.0/Xenium_V1_Human_Kidney_FFPE_Protein_updated/`, named `Xenium_V1_Human_Kidney_FFPE_Protein_updated_<suffix>`. Sizes were checked on 2026-11-11.
  - `outs.zip` (**36.1 GB**) is the full bundle and the one `prepare_data.py` needs. It contains `morphology_focus/`, `morphology.ome.tif`, `transcripts.parquet`, `cells.parquet`, `cell_boundaries.parquet`, `nucleus_boundaries.parquet`, `cell_feature_matrix.h5`, `protein_panel.json`, `gene_panel.json`, `experiment.xenium` and the zarr.zip files.
  - `xe_outs.zip` (19.3 GB) is the Xenium Explorer subset. It has no parquet files, so it isn't enough for Day 2.
  - `he_image.ome.tif` (3.7 GB) is the post-Xenium H&E. `he_imagealignment.csv` is a 3×3 affine from the H&E into Xenium coordinates (roughly a 90° rotation plus scaling).
  - `annotation.geojson` holds pathology annotations, **already in QuPath format and aligned to the H&E**. It has 9 regions: Tumor ×3, Immune infiltration ×2, Necrosis, Blood vessels, Hemorrhage and Adipose tissue. It is a reference for Day 1 session 2 and a guide for choosing the crop.
  - The page also offers a supplemental `cell_groups.csv` (10x's cell groupings), a possible comparison for session 7.
- **Fetching with curl:** use an explicit byte range (`-r start-end`). The CDN ignored a suffix range (`-r -N`) on `outs.zip` and started sending the whole 36 GB. The 10x dataset pages rate-limit automated fetches (HTTP 429), and they load with browser-like request headers.
- **QuPath and Xenium:**
  - Images: 10x documents that opening `morphology_focus/ch0000_dapi.ome.tif` in QuPath loads every channel in that folder.
  - Cell boundaries: there is no built-in importer. `prepare_data.py` should convert the cropped `cell_boundaries.parquet` to QuPath GeoJSON (µm → pixels).
  - Transcripts: there is no supported route, only community scripts and an open request on [uw-loci/qupath-extension-cell-analysis-tools#25](https://github.com/uw-loci/qupath-extension-cell-analysis-tools/issues/25). Large GeoJSON files strain QuPath's importer.
  - **Recommendation (not yet decided):** transcripts on Day 2 only, with at most a small points GeoJSON as a Day 1 demonstration.
- **Crop size:** at about 7,000 cells/mm², a 1.5 × 1.5 mm crop gives roughly 16,000 cells. Choose it from the H&E plus the pathology annotations, so it includes tumour, immune infiltration and stroma. The 36 GB bundle should be downloaded on the HPC; participants only download the Zenodo crop.

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
1. **Teardown** (done): remove the CellSurvey files, write a README skeleton, slim down `AGENTS.md`/`CLAUDE.md`.
2. **Environment** (done, see Status): new `pixi.toml`/`pixi.lock`, `Scripts/check_install.py`, a matching `requirements.txt`, and `Pages/Installation-Instructions.md` (QuPath + extensions, pixi, `check-full`, troubleshooting including the certificate errors). `pixi.lock` is format v7, so participants need pixi ≥ 0.68. **Still to do:** run `pixi run check-full` on macOS, and fill in the organisers' contact details and the data link on the installation page.
3. **Data**: `Scripts/prepare_data.py`. The licence and file list are confirmed (see Dataset). Next: download the full bundle on the HPC, run the two hands-on tests (see Open questions), then choose the crop.
4. **Day 2 notebooks**: 06 first (riskiest), then 05, 07, 08.
5. **Day 1**: port the QuPath exercises to the RCC data and write the `Pages/Day1/` guides (QuPath GUI work, led by the instructors).

## Open questions
- **Test:** does `spatialdata_io.xenium` (0.7.1) read all 35 per-channel protein images from XOA 4.0's `morphology_focus/`? Its documentation doesn't say.
  - **If it doesn't, keep `spatialdata_io.xenium` for everything except the images, and read the images with bioio.** spatialdata-io also reads the transcripts (points), cell and nucleus boundaries (shapes) and the cell-by-feature table, puts them in one µm coordinate system, and loads the H&E with `xenium_aligned_image`. Reimplementing that would be more work than the image step.
  - How: call `spatialdata_io.xenium(..., morphology_focus=False, morphology_mip=False)`. Then read the 35 `morphology_focus/` files with bioio (or plain `tifffile`), stack them with channel names taken from the file names, and add them with `Image2DModel.parse`. Give it a 0.2125 µm/px scale transform (check the bundle's `experiment.xenium`) so it lines up with the µm-space elements, plus multiscale levels for a pyramid. bioio and bioio-ome-tiff would need adding to `pixi.toml` and `requirements.txt`.
  - This only affects `prepare_data.py`: participants open the cropped SpatialData Zarr checkpoints with `spatialdata.read_zarr`, not raw Xenium output. Building the image layer by hand could even be shown in session 5, since it makes SpatialData elements and transforms explicit.
  - The +100 protein offset needs handling with either reader.
- **Test:** does QuPath 0.7 load all 35 channels from `ch0000_dapi.ome.tif`, and stay responsive on the crop?
- Transcripts on Day 1: decide whether to adopt the Day 2-only recommendation in Dataset.
- Crop region (size suggested in Dataset); compute platform; cohort size and dates.
- Source and sharing terms of the original liver `.vsi` and `LungImg1.ome.tif` course images.
