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
- **Workshop data = one cropped, SpatialData/Sopa-ready Zarr** (decided 2026-11-13). Participants never touch raw Xenium output: they open one Zarr with `spatialdata.read_zarr` and can pass it straight to Sopa (`sopa.make_image_patches`, `sopa.segmentation.instanseg`, `sopa.aggregate`). Built from the chosen crop, it holds:
  - **Images:** `morphology_focus` (35 channels, +100 offset removed from the protein channels, pyramidal) and the aligned H&E (pyramidal).
  - **Points:** `transcripts`, with `feature_name` as the gene column.
  - **Shapes:** 10x's `cell_boundaries` and `nucleus_boundaries` (for the session 6 comparison), plus the pathology annotations.
  - **Tables (decided 2026-11-13):** two tables over the same cells, both linked to `cell_boundaries` with the same cell IDs.
    - `table` holds genes only (transcript counts). The 111 control and codeword features are dropped, but the per-cell control counts stay as `obs` columns.
    - `protein` holds the 27 protein intensities.
    - Names stay natural (`CD4` in both), so the 9 gene/protein clashes don't matter. Each table gets its own normalisation: counts and intensities must not be normalised together.
  - **Coordinates:** a µm coordinate system alongside spatialdata-io's pixel `global` one.
- **Day 1 works on the same crop, exported for QuPath** (decided 2026-11-13). The same notebook run writes, alongside the Zarr:
  - the cropped 35-channel IF image as a pyramidal OME-TIFF, offset-corrected so values match Day 2;
  - the cropped H&E;
  - 10x's pathology annotations as GeoJSON, and optionally 10x's cell boundaries;
  - possibly a ready-made QuPath project.
  - **Crop-local coordinates (decided 2026-11-13, option A).** The Zarr and the OME-TIFFs both start at the crop corner (0, 0) in µm and pixels, so Day 1 GeoJSON loads into the Zarr in session 5 without shifting. Nobody needs to apply an offset during the workshop.
    - The full-slide offset (x 1487.5 µm, y 0) is recorded for traceability only: in the Zarr's metadata, and in the OME-TIFFs as `Plane PositionX/PositionY`.
    - QuPath is believed to ignore OME stage positions and always start at (0, 0). Not yet verified, but it doesn't matter under option A.
    - Rejected, option B: keep slide coordinates in the Zarr and apply a translation when loading Day 1 GeoJSON.
  - **H&E resampled for Day 1 (decided 2026-11-13).** The exported H&E OME-TIFF is resampled into the IF image's frame and pixel size (0.2125 µm), so annotations move between H&E, IF and Day 2 unchanged. The Zarr keeps the original (cropped) H&E plus its affine transform, which shows SpatialData's way of handling registration in session 5.
- **The preparation notebook builds everything from 10x's raw files** (decided 2026-11-13): the Day 2 Zarr and the Day 1 OME-TIFFs/GeoJSON, in one run, so attendees can reproduce the workshop data after the course.
  - **It should work on other Xenium datasets too.** No values specific to this dataset are hard-coded:
    - URLs, file names and the crop box are parameters.
    - Pixel size and XOA version come from `experiment.xenium`.
    - Protein channels are found by matching image channel names to the table's Protein Expression features. The +100 offset is applied only for XOA ≥ 4.
    - The H&E, alignment and annotations are optional; skip those steps when absent.
    - Protein steps are skipped for RNA-only runs.
    - Image reading follows whatever XOA version spatialdata-io supports.
- **A walkthrough notebook for preparing the full dataset** (decided 2026-11-13), for anyone who wants to work on the whole slide after the workshop. It covers download, reading, offset correction, unique feature names, alignment, cropping (optional) and writing the Zarr.
  - **Decided 2026-11-13: this notebook is the single source of truth.** There is no separate `prepare_data.py` to drift from it. It is parameterised by a crop box: `None` for the full slide, the chosen box for the workshop bundle. The maintainer builds the Zenodo bundle by executing it headless on the HPC (`jupyter nbconvert --to notebook --execute`). `Scripts/` then keeps only small helpers, or none.
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
- **Crop:** chosen 2026-11-13, x 1487.5–2987.5 µm, y 0–1500 µm, about 16,000 cells (details under Open questions). The 36 GB bundle is downloaded on the HPC; participants only download the Zenodo crop.

## Target layout
```
README.md            workshop page (overview, registration, instructors, preparation, programme, venue, slides, FAQ)
Pages/               Installation-Instructions.md, Data.md, Day1/ (session guides), Day2/
qupath/              Day 1 classifiers + class lists (the project itself ships in the data download)
notebooks/           05_data_model_and_loading … 08_spatial_and_next_steps
                     extra/prepare_xenium_dataset.ipynb (post-workshop: download + prepare the full slide; also builds the bundle)
solutions/           completed notebooks with outputs
Scripts/             check_install.py, inspect_xenium.py (maintainer-only)
assets/
pixi.toml
```

`assets/` still holds two CellSurvey output figures. They can be replaced once the workshop data produces its own.

## Large and private files
- `qupath_content/` (the original QuPath course) is **gitignored**. Copy only classifiers and class lists from it into `qupath/`.
- Never commit the 80 MB slide deck (slides live on Google Drive) or the QuPath project `data/` folders (~450 MB). The `.qpproj` files store absolute paths from the author's machine, and the projects will be rebuilt on the RCC data.
- Workshop data never goes in git. Participants download the Zenodo bundle; the preparation notebook builds it (and the full-slide version) from 10x's files. Commit that notebook **without outputs**, since its outputs would include large images.

## Order of work
0. **Upstream first**: **done on `feature/instanseg`** in upstream CellSurvey (2026-11-10). Merge to upstream `main` is pending final tests. Adds `--segmenter instanseg`, requires `sopa>=2.3.0`, separates TensorFlow/Stardist and PyTorch/InstanSeg into separate pixi environments, and converts spatial distances to µm.
1. **Teardown** (done): remove the CellSurvey files, write a README skeleton, slim down `AGENTS.md`/`CLAUDE.md`.
2. **Environment** (done, see Status): new `pixi.toml`/`pixi.lock`, `Scripts/check_install.py`, a matching `requirements.txt`, and `Pages/Installation-Instructions.md` (QuPath + extensions, pixi, `check-full`, troubleshooting including the certificate errors). `pixi.lock` is format v7, so participants need pixi ≥ 0.68. **Still to do:** run `pixi run check-full` on macOS, and fill in the organisers' contact details and the data link on the installation page.
3. **Data**: build the cropped SpatialData/Sopa-ready Zarr and the Day 1 QuPath files (see Decisions), via the preparation notebook (or `prepare_data.py`). The licence and file list are confirmed (see Dataset).
   - QuPath loading is confirmed and the crop is chosen (candidate 1; see Open questions).
   - `notebooks/extra/prepare_xenium_dataset.ipynb` was written on 2026-11-13. Run it headless with `XENIUM_RAW_DIR`, `XENIUM_OUTPUT_DIR`, `XENIUM_DOWNLOAD=0/1`, `XENIUM_CROP=full|x0,y0,x1,y1` and `XENIUM_VALIDATE`/`XENIUM_ZIP`. Relative folders count from the repo root, because nbconvert runs kernels in `notebooks/extra/`.
     - Every step after reading has been checked on a small synthetic Xenium-like dataset: protein offset, H&E resampling, annotation transform, table links, OME-TIFF pyramids and Plane positions, and the zips.
     - The InstanSeg path of the Sopa check also runs.
     - The full run on the real data, on the HPC, is in progress.
   - **Gotchas found:**
     - Cropped copies of spatialdata-io GeoDataFrames and DataFrames keep the old transforms in `.attrs`, so clear them before `ShapesModel`/`PointsModel.parse` with new transforms.
     - `sopa.aggregate` writes to `table` by default, which would overwrite 10x's gene table. In session 6 pass `key_added` and `image_key="morphology_focus"`.
   - Then write the preparation notebook. Develop it against the crop and run it headless on the HPC to build the Zenodo bundle. Check that the Zarr round-trips through `spatialdata.read_zarr` and a small `sopa.make_image_patches` + `sopa.segmentation.instanseg` run.
   - `Scripts/inspect_xenium.py --data-dir <dir> [--with-he]` is a maintainer-only script, written 2026-11-13. It downloads `outs.zip` and the small files, resuming if interrupted, then extracts them. It reports what `experiment.xenium` and the panels contain, and reads each `morphology_focus/` file directly with tifffile (shape, dtype, value percentiles, so the +100 offset is visible). It then runs test 1 with `spatialdata_io.xenium` and writes `inspection_report.json`.
   - Ran successfully on the HPC on 2026-11-13. The data and `inspection_report.json` are in `/nemo/stp/lm/working/barryd/hpc/projects/stps/lm/spatial-bio-training/10x_xenium_data` (`Z:\working\...` from Windows). Findings are under Open questions.
4. **Day 2 notebooks**: 06 first (riskiest), then 05, 07, 08.
5. **Day 1**: port the QuPath exercises to the RCC data and write the `Pages/Day1/` guides (QuPath GUI work, led by the instructors).

## Open questions
- **Test 1 PASSED on the HPC (2026-11-13).** `spatialdata_io.xenium(outs, gex_only=False, cells_labels=False, nucleus_labels=False, aligned_images=False)` read the bundle in 82 s.
  - `morphology_focus` is a 5-level pyramid, 35 × 27328 × 54002 px (uint16), with proper channel names: DAPI, ATP1A1/CD45/E-Cadherin, 18S, alphaSMA/Vimentin, the four colour backgrounds, CD4, CD20, CD8A, CD3E, CD138, HLA-DR, CD11c, CD68, CD16, GranzymeB, CD163, PD-1, VISTA, PD-L1, LAG-3, CD45RA, PCNA, CD45RO, Ki-67, Beta-catenin, CD31, PTEN, PanCK, Vimentin, alphaSMA, CD45 and E-Cadherin. **No bioio fallback is needed.**
  - It also produced `cell_boundaries` (465,534) and `nucleus_boundaries` (471,228). The table is 465,534 cells × 543 features: 405 gene, 27 protein, plus control and codeword features.
  - The `global` coordinate system is in **pixels**. Points and shapes are stored in µm, with a `Scale(1/0.2125)` transform. Notebooks that work in µm need to set that up explicitly.
  - With labels skipped, spatialdata warns that the table annotates `cell_labels`, which isn't present. `prepare_data.py` should re-point the table at `cell_boundaries` (its region and instance key).
- **Protein and gene names clash.** Some protein features share names with genes (e.g. CD4), so the table's `var_names` aren't unique. Name-based indexing fails (`InvalidIndexError`). `prepare_data.py` must make them unique, e.g. a `_protein` suffix, or split protein into its own table. Notebooks can then index by name.
  - The 9 clashes are CD163, CD3E, CD4, CD45RA, CD45RO, CD68, CD8A, PCNA and PTEN.
- **Transcript count is fine.** The SpatialData printout claims 847,626,296 (11 × the parquet rows, matching its 11 partitions), but the exact count is 77,056,936, the same as `transcripts.parquet`. Ignore the printout. Filtering `transcripts.parquet` to the crop with pyarrow is still the efficient way for `prepare_data.py` to build the points.
- **The +100 offset is only on the 27 protein channels** (`ch0008`–`ch0034`, median about 99–119 at the coarsest level).
  - DAPI, 18S, the three combined segmentation-stain channels (`ch0001`–`ch0003`) and the four colour backgrounds have no offset.
  - Every channel has 0 outside the imaged region, so subtract as `clip(x - 100, 0)` on protein channels only.
  - The cell table's protein values are already offset-free and unscaled: min 0, median 0, max 1055.5 with `gex_only=False`.
- **H&E:** `xenium_aligned_image` returns a single unpyramided 3 × 60680 × 24096 RGB array in one 4.4 GB chunk (spatialdata warns). `prepare_data.py` should pass `image_models_kwargs` with `chunks` and `scale_factors`.
  - `he_imagealignment.csv` maps H&E pixels to Xenium pixels: a 90° rotation and ×1.2896 scale, so an H&E pixel is about 0.274 µm. Translation is (−11896, 28914).
- **`annotation.geojson` coordinates are in H&E pixels.** Its 9 polygons are Tumor ×3, Necrosis, Immune infiltration ×2, Hemorrhage, Adipose tissue and Blood vessels.
  - 5 of the 9 have only a `name` and no `classification`, and one "Immune infiltration" is classified "Immune cells". `prepare_data.py` should set each classification from its name for QuPath.
  - **Transform them with `he_imagealignment.csv` before use** (shapely `affine_transform` with `[a, b, d, e, xoff, yoff]` from rows 1–2). Untransformed, they appear rotated 90° in QuPath (confirmed by the maintainer, 2026-11-13).
  - The transform was checked against cell density: Immune infiltration about 12,100 cells/mm², Tumor about 6,800, Adipose about 560, whole image about 7,000.
  - **Blood vessels and Hemorrhage lie entirely outside the Xenium region**, because the H&E covers more tissue than Xenium imaged. Adipose is only 0.75 mm² inside it. Within the Xenium image, only Tumor ×3, Immune infiltration ×2, Necrosis and part of Adipose are usable. Use CD31 to show vessels instead.
- QuPath 0.7 loads all 35 `morphology_focus` channels when `ch0000_dapi.ome.tif` is opened (confirmed by the maintainer, 2026-11-13). Test 2 is passed for loading; responsiveness on the crop is still to check.
- **Crop candidates** (2026-11-13) are 1.5 × 1.5 mm = 7059 px windows, ranked by how evenly they mix Tumor, Immune infiltration and unannotated tissue. Coordinates are Xenium pixels (multiply by 0.2125 for µm):
  - **Candidate 1:** x 7000–14059, y 0–7059. Tumour 55%, immune 24%, unannotated 21%, 16,047 cells. The most balanced.
  - **Candidate 2:** x 0–7059, y 0–7059, the top-left corner. Tumour 32%, immune 51%, unannotated 18%, 19,934 cells.
  - Both lie along the top edge, where the first Immune infiltration region borders the main Tumor region.
  - `annotations_xenium_px_with_crop_candidates.geojson` (in the HPC data folder) holds the transformed annotations, clipped to the image, plus the candidate boxes, for checking in QuPath. Its third box (11000–18059) has only 3% immune and can be ignored.
  - **Right-hand three-region candidates** (Tumor + Immune infiltration + Adipose, at the top-right edge; the maintainer wants three annotated regions in the crop):
    - A 1.5 mm square can't balance them: the best is 8% tumour, 78% immune, 7% adipose.
    - **Candidate 3**, 1.5 × 2.5 mm (portrait): x 46501–53559, y 500–12264 px. Tumour 18%, immune 57%, adipose 16%, 34,042 cells. The best balance.
    - **Candidate 4**, 1.5 × 2.0 mm: x 46501–53559, y 2000–11411 px. Tumour 13%, immune 68%, adipose 12%, 29,830 cells.
    - Both are in the QuPath candidates file.
  - **CHOSEN (2026-11-13): candidate 1.** Workshop crop = **x 1487.5–2987.5 µm, y 0–1500 µm** (1.5 × 1.5 mm). In Xenium pixels at 0.2125 µm/px that is x 7000–14059, y 0–7059.
    - It contains about 16,000 cells: tumour 55%, immune infiltration 24% and 21% unannotated tissue (no necrosis or adipose).
    - It sits on the image's top edge, where the first Immune infiltration region borders the main Tumor region.
    - Candidates 3 and 4 (three annotated regions) were rejected: immune-dominated and about twice the cells.
    - Crop in µm in the preparation notebook, and derive pixel bounds from `pixel_size` in `experiment.xenium`.
- **QuPath GeoJSON import requirements** (found 2026-11-13). The first candidates file failed in QuPath 0.7 with `Unable to parse PathClass`. When exporting GeoJSON for QuPath:
  - give every `classification` both `name` and `color` (an RGB list), with one colour per class name;
  - keep only Polygon/MultiPolygon geometries, since clipping can produce a GeometryCollection.
- `protein_panel.json` lists 28 targets under `payload.panel.targets`, against `num_targets: 27`. The gene panel's `payload.targets` has 465 entries.
- **Original test question:** does `spatialdata_io.xenium` (0.7.1) read all 35 per-channel protein images from XOA 4.0's `morphology_focus/`? Its documentation doesn't say, but its source has an explicit XOA v4 path. That path takes channel names from the OME-XML in `ch0000_dapi.ome.tif` and loads the `chNNNN_*.ome.tif` files as one multichannel image, so it will probably pass. `Scripts/inspect_xenium.py` checks it on the real files.
  - **Always pass `gex_only=False`.** The default (`True`) drops the Protein Expression features from the cell table. With `False`, spatialdata-io keeps them and undoes 10x's fixed-point scaling of protein values in `cell_feature_matrix.h5`. That is separate from the +100 offset in the images.
  - **If it doesn't, keep `spatialdata_io.xenium` for everything except the images, and read the images with bioio.** spatialdata-io also reads the transcripts (points), cell and nucleus boundaries (shapes) and the cell-by-feature table, puts them in one µm coordinate system, and loads the H&E with `xenium_aligned_image`. Reimplementing that would be more work than the image step.
  - How: call `spatialdata_io.xenium(..., morphology_focus=False, morphology_mip=False)`. Then read the 35 `morphology_focus/` files with bioio (or plain `tifffile`), stack them with channel names taken from the file names, and add them with `Image2DModel.parse`. Give it a 0.2125 µm/px scale transform (check the bundle's `experiment.xenium`) so it lines up with the µm-space elements, plus multiscale levels for a pyramid. bioio and bioio-ome-tiff would need adding to `pixi.toml` and `requirements.txt`.
  - This only affects `prepare_data.py`: participants open the cropped SpatialData Zarr checkpoints with `spatialdata.read_zarr`, not raw Xenium output. Building the image layer by hand could even be shown in session 5, since it makes SpatialData elements and transforms explicit.
  - The +100 protein offset needs handling with either reader.
- **Test:** does QuPath 0.7 load all 35 channels from `ch0000_dapi.ome.tif`, and stay responsive on the crop?
- Transcripts on Day 1: decide whether to adopt the Day 2-only recommendation in Dataset.
- Compute platform; cohort size and dates.
- Source and sharing terms of the original liver `.vsi` and `LungImg1.ome.tif` course images.
