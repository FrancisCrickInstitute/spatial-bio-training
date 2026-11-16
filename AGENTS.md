# AGENTS.md

This repo holds the material for a **two-day workshop on spatial biology/omics analysis** run by the Crick: Day 1 in QuPath, Day 2 in Python. It is modelled on [introduction-to-image-analysis](https://github.com/FrancisCrickInstitute/introduction-to-image-analysis). The full plan, with rationale, is in the shared doc [Spatial Biology Workshop Plan](https://claude.ai/artifact/CnmDq3CUzc3fMptRAinEtY).

The repo began as a fork of the [CellSurvey](https://github.com/FrancisCrickInstitute/CellSurvey) pipeline. That code was removed in the teardown step (step 1), and its history stays in git. For CellSurvey's architecture, gotchas and its survey of related tools (PANORAMIC, CELESTA, Novae, segger, Spotiflow, etc.), read **upstream `AGENTS.md`**. That survey is the source material for session 8, "evaluating new tools".

## Status

**2026-11-14:** steps 1 (teardown) and 2 (environment) are done and merged into `main`. Step 3 (data) is in progress: `notebooks/extra/prepare_xenium_dataset.ipynb` ran successfully on the real data on the HPC (2026-11-14) and produced the workshop Zarr and the QuPath files. The QuPath files have been checked in QuPath. Still to do: the Zenodo upload. Step 4 has started: notebook 06 (segmentation and QC) is drafted. Its first end-to-end run (2026-11-15, on a 16 GB laptop-class Windows machine) got through cell 5, then stalled in the first InstanSeg run because the machine was swapping. With memory freed, InstanSeg on the session's region takes 30 s and peaks at 1.2 GB. The programme then changed (2026-11-15): a new session 5 notebook (classic segmentation and classifiers on the Day 1 OME-TIFF, read with bioio) comes first. It is drafted but not yet run end to end (see Order of work). Notebook 06 will gain a SpatialData introduction. No other Day 2 notebooks or Day 1 guides exist yet.

The workshop environment is `pixi.toml` + `pixi.lock`, locked for linux-64, win-64 and osx-arm64. It uses Python 3.12, `sopa[instanseg]` 2.3, PyTorch, `spatialdata` 0.8 (pinned below 0.9, see Updating package versions), scanpy, squidpy, SegTraQ, bioio (Bio-Formats + OME-TIFF), scikit-image, geopandas and JupyterLab, with no TensorFlow and no napari. Tasks:
- `pixi run check` runs `Scripts/check_install.py`: imports, versions, compute device.
- `pixi run check-full` also downloads the InstanSeg model and segments a synthetic image.
- `pixi run lab` starts JupyterLab.

`requirements.txt` mirrors the PyPI deps for pip users, so keep it in step with `pixi.toml`. `pixi run check-full` passes on win-64 (CPU) and on linux-64 (CUDA, NVIDIA A100 on the Crick HPC, 2026-11-11), including the InstanSeg model download. osx-arm64 is locked but untested. On the HPC, pixi warns that its cache is on a network filesystem and redirects it to `/tmp`. This is harmless. On networks or VPNs that intercept HTTPS, pixi and the InstanSeg model download can fail with certificate errors (`UnknownIssuer` / `CERTIFICATE_VERIFY_FAILED`). `Pages/Installation-Instructions.md` covers this.

## Working in this repo
- **This is a training-workshop repo, not a software package.** There is no build, no tests and no CI. Day 2 material will be Jupyter notebooks, and nothing here is meant to be imported.
- **Don't restore the CellSurvey code.** Point to upstream [CellSurvey](https://github.com/FrancisCrickInstitute/CellSurvey) instead. An `upstream` git remote (SSH; HTTPS fails certificate checks on the maintainer's machine) may be configured for fetching it.
- **Keep participant-facing text and the plan in step.** The programme in `README.md` mirrors the table below.
- **The maintainer stages and commits.** Leave changes unstaged.
- **The maintainer runs pixi commands** (`pixi lock`, `pixi install`, `pixi update`, `pixi run ...`). Don't run them; say which command is needed. `pixi lock --check` (pixi 0.72) re-solved and rewrote `pixi.lock` instead of only checking it.

## Updating package versions (between workshops)
`pixi.lock` pins every package to the versions the material was tested with, so participants all get the same environment. The ecosystem moves fast (spatialdata, Sopa, spatialdata-io, SegTraQ, InstanSeg), so **update the environment deliberately before each run of the workshop**, early enough to fix what breaks: at least a month before, and not in the final week.

- **Any `pixi lock` can upgrade packages.** It resolves the newest versions `pixi.toml` allows, even when only an unrelated dependency changed. On 2026-11-16, removing napari also moved spatialdata from 0.8.0 to 0.9.0. Check the lock diff for version changes to the core packages every time.
- **Current upper pins** (temporary, to be lifted once retested):
  - `spatialdata <0.9` (added 2026-11-16): the workshop Zarr and notebooks 05/06 were built and tested on 0.8.
- **Update procedure:**
  1. Lift or raise the pins in `pixi.toml` (and `requirements.txt`), then `pixi update` (or `pixi lock`) and read the version changes in the lock diff.
  2. `pixi run check-full` on Windows, macOS and Linux.
  3. Rerun the preparation notebook. If spatialdata's Zarr format changed, the Zenodo bundle needs rebuilding and re-uploading, and the links updating.
  4. Run every solution notebook end to end on the new environment, on a laptop-class machine.
  5. Recheck the version-specific gotchas recorded below (they name the versions they were found on) and update or remove them.
  6. Update the versions named in this file.

## Decisions made
- **Keep this repo and its history.** No new repo.
- **No napari** (decided 2026-11-16). There's no time for napari-spatialdata in the programme, and QuPath covers interactive viewing. napari, napari-spatialdata and the Qt check in `check_install.py` were removed, which also drops Qt from the environment. Session 8 can still mention napari-spatialdata as a pointer.
- **One dataset across both days:** the 10x **Xenium Protein FFPE human renal cell carcinoma** (RCC) section, with transcripts, a 27-plex protein panel and post-Xenium H&E, all on the same section (see Dataset). Both hands-on tests passed on 2026-11-13: spatialdata-io reads it, and QuPath loads all 35 channels. The former fallback was BioImage Archive **S-BIAD1093** (Xenium + COMET IF, but no H&E). A cropped region is published on Zenodo as the workshop download.
- **Day 1 = the existing one-day Introduction to QuPath course** (Sara Salgueiro Torres, CALM STP, QuPath v0.7; source material in `qupath_content/`), ported to the workshop dataset. **No Groovy scripting**: Python is the only scripting language taught. Session 4 becomes spatial analysis (density maps, distances, Delaunay) plus export for Day 2.
- **InstanSeg on both days**: QuPath's InstanSeg extension on Day 1, and `sopa.segmentation.instanseg` (Sopa ≥ 2.3, `sopa[instanseg]`) on Day 2, using the same `fluorescence_nuclei_and_cells` model. Pass `pixel_size`, or it may return no cells. The workshop environment needs **no TensorFlow**.
- **Notebooks only for Day 2.** Session 8 points to upstream CellSurvey as the "notebooks → pipeline" example.
- **Distances in µm**, matching upstream CellSurvey (which converted its spatial parameters to µm on `feature/instanseg`).
- **No bring-your-own-data session.** Applications capture participants' projects and goals. The workshop teaches tool choice and how to ask the right questions, not analysis of attendees' own data.
- **Workshop crop (chosen 2026-11-13): x 1487.5–2987.5 µm, y 0–1500 µm** of the full slide (1.5 × 1.5 mm; Xenium pixels x 7000–14059, y 0–7059 at 0.2125 µm/px).
  - About 16,000 cells: 55% Tumor, 24% Immune infiltration, 21% unannotated tissue (no necrosis or adipose). It sits on the image's top edge, where the first Immune infiltration region borders the main Tumor region.
  - Rejected: the top-left corner (x 0–7059 px, immune-dominated) and two taller right-hand crops that also include Adipose (x 46501–53559 px; immune-dominated, about twice the cells, and not square). The candidate boxes are in `annotations_xenium_px_with_crop_candidates.geojson` in the HPC data folder.
  - The crop is given in µm; pixel bounds come from `pixel_size` in `experiment.xenium`.
- **Workshop data = one cropped, SpatialData/Sopa-ready Zarr** (decided 2026-11-13). Participants never touch raw Xenium output: they open one Zarr with `spatialdata.read_zarr` and can pass it straight to Sopa (`sopa.make_image_patches`, `sopa.segmentation.instanseg`, `sopa.aggregate`). It holds:
  - **Images:** `morphology_focus` (35 channels, +100 offset removed from the protein channels, pyramidal) and `he`, the H&E as scanned (cropped, pyramidal) with its alignment as an affine transform.
  - **Points:** `transcripts`, with `feature_name` as the gene column.
  - **Shapes:** 10x's `cell_boundaries` and `nucleus_boundaries` (for the session 6 comparison), plus `pathology_annotations`.
  - **Tables:** two tables over the same cells, both linked to `cell_boundaries` through `cell_id`.
    - `table` holds genes only (transcript counts). The control and codeword features are dropped, but the per-cell control counts stay as `obs` columns.
    - `protein` holds the 27 protein intensities.
    - Names stay natural (`CD4` in both), so the 9 gene/protein clashes don't matter. Each table gets its own normalisation: counts and intensities must not be normalised together.
  - **Coordinates:** `global` in pixels (as spatialdata-io uses) and `microns`.
  - **Attrs:** source URL, licence, XOA version, pixel size, the region's position on the slide (µm and px) and the offset removed.
- **Day 1 works on the same crop, exported for QuPath** (decided 2026-11-13). The same notebook run writes, in `qupath/` beside the Zarr:
  - `<NAME>_if.ome.tif`: the 35-channel IF image as a pyramidal OME-TIFF, offset-corrected so values match Day 2;
  - `<NAME>_he.ome.tif`: the H&E, **resampled into the IF image's frame and pixel size** (0.2125 µm), so annotations move between H&E, IF and Day 2 unchanged. The Zarr keeps the original H&E plus its transform instead, which shows SpatialData's way of handling registration in session 5;
  - `<NAME>_annotations.geojson`: 10x's pathology annotations, aligned and clipped to the crop;
  - `<NAME>_10x_cells.geojson`: 10x's cell boundaries, as detections;
  - `<NAME>_fovs.geojson`: the fields of view the image was stitched from, as annotations (added 2026-11-15, for session 5's thresholding discussion).
  - **No ready-made QuPath project** (decided 2026-11-14). Participants build their own project in session 1 from these files.
  - **Crop-local coordinates (option A).** The Zarr and the OME-TIFFs both start at the crop corner (0, 0) in µm and pixels, so Day 1 GeoJSON loads into the Zarr in session 5 without shifting. Nobody needs to apply an offset during the workshop.
    - The full-slide offset (x 1487.5 µm, y 0) is recorded for traceability only: in the Zarr's attrs, and in the OME-TIFFs as `Plane PositionX/PositionY`.
    - QuPath is believed to ignore OME stage positions and always start at (0, 0). Not yet verified, but it doesn't matter under option A.
    - Rejected, option B: keep slide coordinates in the Zarr and apply a translation when loading Day 1 GeoJSON.
- **`notebooks/extra/prepare_xenium_dataset.ipynb` is the single source of truth for the data** (decided 2026-11-13). There is no separate `prepare_data.py` to drift from it.
  - It builds everything from 10x's raw files in one run: the Day 2 Zarr and the Day 1 OME-TIFFs/GeoJSON, so attendees can reproduce the workshop data after the course.
  - It doubles as the post-workshop walkthrough for preparing the **whole slide**: download, reading, offset correction, splitting the tables, alignment, cropping (optional) and writing the Zarr.
  - It is parameterised by a crop box: `XENIUM_CROP=full` for the whole slide, the chosen box by default. The maintainer builds the Zenodo bundle by executing it headless on the HPC (`jupyter nbconvert --to notebook --execute`). `Scripts/` keeps only small helpers.
  - **It should work on other Xenium datasets too.** No values specific to this dataset are hard-coded:
    - URLs, file names and the crop box are parameters.
    - Pixel size and XOA version come from `experiment.xenium`.
    - Protein channels are found by matching image channel names to the table's Protein Expression features. The +100 offset is applied only for XOA ≥ 4.
    - The H&E, alignment and annotations are optional; those steps are skipped when absent.
    - The `protein` table is skipped for RNA-only runs.
    - Image reading follows whatever XOA version spatialdata-io supports.
- **Workshop logistics (decided 2026-11-14):** **25–26 February 2027**, for **20–30 participants**, on **their own laptops**. There is no shared compute, so everything must run on a typical CPU-only laptop (Windows, macOS on Apple Silicon or Linux; Intel Macs aren't supported for Day 2):
  - Day 2 relies on precomputed checkpoints (one SpatialData Zarr per notebook in the download). Live segmentation runs on one small tile only.
  - Keep memory use modest (aim for 8–16 GB RAM laptops), and avoid loading whole images or all 2.1 million transcripts at once.
  - The installation page and `pixi run check-full` must be done before the day. Plan time to chase attendees whose check fails.
- **Transcripts on Day 2 only** (decided 2026-11-14). Day 1 has no transcript import.
- **Session 5 = "From QuPath to Python"** (decided 2026-11-15). Before the full InstanSeg/Sopa analysis, participants redo a simple Day 1-style analysis in Python on a small tile (about 200 µm):
  - open the **same OME-TIFF and GeoJSON they used in QuPath** (not the Zarr). It is the more transferable skill (their own data will be TIFFs and proprietary formats), and it gives SpatialData a reason to exist when transcripts arrive in session 6;
  - threshold DAPI (manual, Otsu, a slider), split touching nuclei (distance transform + watershed), grow nuclei into cells (`expand_labels`), measure per-cell marker intensities (`regionprops_table`), and classify with single-marker thresholds combined into phenotypes (as in QuPath's composite classifier);
  - **key exercise:** sweep the threshold and the expansion distance, and see how nucleus counts, cell areas and the percentage of a phenotype (e.g. CD8+ T cells) change. Segmentation choices change biological conclusions;
  - end with InstanSeg on the same tile as a teaser, and save the outlines as GeoJSON (back to QuPath; a third segmentation for the SegTraQ comparison in session 6).
  - The deeper SpatialData tour (why a container, coordinate systems, transcripts, tables, H&E alignment, loading Day 1 GeoJSON into the Zarr) moves to the start of session 6.
- **Images are read with bioio, Bio-Formats first, pure Python as fallback** (decided 2026-11-15). Participants know Bio-Formats from Fiji.
  - `BioImage(path, reader=bioio_bioformats.Reader, dask_tiles=True, tile_size=(512, 512))` reads only the tiles it needs. If that raises **anything**, fall back to `BioImage(path, reader=bioio_ome_tiff.Reader)`, which gives the same channel names, pixel size and dimensions but reads whole planes (about 100 MB per channel of the crop, so read only the channels needed). bioio picks `bioio-ome-tiff` by default for `.ome.tif`, so Bio-Formats must be requested explicitly.
  - bioio-bioformats (through `bffile`) downloads its **own Java runtime (cjdk) and the Bio-Formats jars (Maven)** on first use. No installed Java is needed, and Fiji's bundled Java isn't used. A failed download surfaces as `UnsupportedFileFormatError` ("None of the specified readers were able to read this image"), with `CERTIFICATE_VERIFY_FAILED` inside it on intercepting networks. It failed that way in Claude Code's shell (2026-11-15); the fallback worked.
  - Neither reader reads pyramid levels (both read level 0), so a whole-crop overview means downsampling a channel.
  - `pixi run check-full` now tests both readers on a synthetic OME-TIFF: the fallback must pass, and a Bio-Formats failure is a `[WARN]` (the run still ends "Ready for the workshop, with warnings"). **Bio-Formats via bioio works** (maintainer's Windows machine, off the VPN, 2026-11-15): the first `check-full` downloaded Azul Zulu JRE 11.0.33 (38.6 MB) into `%LOCALAPPDATA%\cjdk\cache` plus the Bio-Formats jars, then read the test tile correctly. Later runs work from the cache with no network, including in Claude Code's shell. The line `jar tool not found at ...\bin\jar.exe` during that first run is harmless (the JRE has no `jar` tool). macOS and Linux are untested.
  - Dependencies added by the maintainer (2026-11-15): `bioio`, `bioio-bioformats`, `bioio-ome-tiff`, `scikit-image`, `geopandas` in `pixi.toml` (relocked) and `requirements.txt`.

## Programme (4 sessions/day, 09:30–17:00)
| Day 1 (QuPath) | Day 2 (Python) |
|---|---|
| 1. Images + spatial-biology primer | 5. From QuPath to Python: notebooks, the Day 1 OME-TIFF + GeoJSON via bioio, classic segmentation + simple classifiers |
| 2. H&E workflow (tissue, regions, cells) | 6. SpatialData Zarr (why a container, coordinates, transcripts, tables) + segmentation (InstanSeg via Sopa) + QC (SegTraQ, vs Xenium and session 5 segmentations) + aggregation |
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
- **XOA 4.0 adds a fixed +100 offset to protein pixel values** instead of allowing negative values after background subtraction (details under Data findings).
- **Downloads.** All are on `cf.10xgenomics.com/samples/xenium/4.0.0/Xenium_V1_Human_Kidney_FFPE_Protein_updated/`, named `Xenium_V1_Human_Kidney_FFPE_Protein_updated_<suffix>`. Sizes were checked on 2026-11-11.
  - `outs.zip` (**36.1 GB**) is the full bundle and the one the preparation notebook needs. It contains `morphology_focus/`, `morphology.ome.tif`, `transcripts.parquet`, `cells.parquet`, `cell_boundaries.parquet`, `nucleus_boundaries.parquet`, `cell_feature_matrix.h5`, `protein_panel.json`, `gene_panel.json`, `experiment.xenium` and the zarr.zip files.
  - `xe_outs.zip` (19.3 GB) is the Xenium Explorer subset. It has no parquet files, so it isn't enough for Day 2.
  - `he_image.ome.tif` (3.7 GB) is the post-Xenium H&E. `he_imagealignment.csv` is a 3×3 affine from H&E pixels into Xenium pixels.
  - `annotation.geojson` holds 9 pathology annotations in QuPath format, in **H&E pixels** (see Data findings). It is a reference for Day 1 session 2 and guided the choice of crop.
  - The page also offers a supplemental `cell_groups.csv` (10x's cell groupings), a possible comparison for session 7.
- **Fetching:** use an explicit byte range (curl `-r start-end`, or a `Range: bytes=start-end` header). The CDN ignored a suffix range (`-r -N`) on `outs.zip` and started sending the whole 36 GB. The 10x dataset pages rate-limit automated fetches (HTTP 429), and they load with browser-like request headers.
- **QuPath and Xenium:**
  - Images: opening `morphology_focus/ch0000_dapi.ome.tif` in QuPath 0.7 loads all 35 channels (confirmed by the maintainer, 2026-11-13). Participants get the cropped `_if.ome.tif` instead.
  - Cell boundaries: there is no built-in importer. The preparation notebook converts them to QuPath GeoJSON (µm → pixels).
  - Transcripts: there is no supported route, only community scripts and an open request on [uw-loci/qupath-extension-cell-analysis-tools#25](https://github.com/uw-loci/qupath-extension-cell-analysis-tools/issues/25). Large GeoJSON files strain QuPath's importer.
  - **Decided:** transcripts on Day 2 only (see Decisions made).
- The 36 GB bundle is downloaded on the HPC; participants only download the Zenodo crop.

## Data findings (HPC inspection, 2026-11-13)
`Scripts/inspect_xenium.py` ran on the real bundle. The data and `inspection_report.json` are in `/nemo/stp/lm/working/barryd/hpc/projects/stps/lm/spatial-bio-training/10x_xenium_data` (`Z:\working\...` from Windows). The preparation notebook already handles everything below; it is recorded for the session notebooks and for other datasets.

- **Reading.** `spatialdata_io.xenium(outs, gex_only=False, cells_labels=False, nucleus_labels=False, aligned_images=False)` (spatialdata-io 0.7.1) read the bundle in 82 s, using its XOA v4 path for the per-channel images. No bioio fallback is needed.
  - **Always pass `gex_only=False`.** The default (`True`) drops the Protein Expression features from the cell table. With `False`, spatialdata-io keeps them and undoes 10x's fixed-point scaling of protein values in `cell_feature_matrix.h5`. That is separate from the +100 offset in the images.
  - `morphology_focus` is a 5-level pyramid, 35 × 27328 × 54002 px (uint16), with proper channel names: DAPI, ATP1A1/CD45/E-Cadherin, 18S, alphaSMA/Vimentin, the four colour backgrounds, CD4, CD20, CD8A, CD3E, CD138, HLA-DR, CD11c, CD68, CD16, GranzymeB, CD163, PD-1, VISTA, PD-L1, LAG-3, CD45RA, PCNA, CD45RO, Ki-67, Beta-catenin, CD31, PTEN, PanCK, Vimentin, alphaSMA, CD45 and E-Cadherin.
  - `cell_boundaries` has 465,534 cells and `nucleus_boundaries` 471,228. The table is 465,534 cells × 543 features: 405 gene, 27 protein, plus control and codeword features.
  - The `global` coordinate system is in **pixels**. Points and shapes are stored in µm, with a `Scale(1/0.2125)` transform. Work in µm needs its own coordinate system (the workshop Zarr adds `microns`).
  - With labels skipped, spatialdata warns that the table annotates `cell_labels`, which isn't present. The notebook re-points both tables at `cell_boundaries`.
- **Protein and gene names clash** in 10x's single table, so its `var_names` aren't unique and name-based indexing fails (`InvalidIndexError`). The 9 clashes are CD163, CD3E, CD4, CD45RA, CD45RO, CD68, CD8A, PCNA and PTEN. Solved by splitting into `table` and `protein`.
- **Transcript count.** The SpatialData printout claims 847,626,296 (11 × the parquet rows, matching its 11 partitions), but the exact count is 77,056,936, the same as `transcripts.parquet`. Ignore the printout.
- **The +100 offset is only on the 27 protein channels** (`ch0008`–`ch0034`, median about 99–119 at the coarsest level).
  - DAPI, 18S, the three combined segmentation-stain channels (`ch0001`–`ch0003`) and the four colour backgrounds have no offset.
  - Every channel has 0 outside the imaged region, so subtract as `clip(x - 100, 0)` on protein channels only.
  - The cell table's protein values are already offset-free and unscaled: min 0, median 0, max 1055.5 with `gex_only=False`.
- **H&E.** `xenium_aligned_image` returns a single unpyramided 3 × 60680 × 24096 RGB array in one 4.4 GB chunk. The notebook avoids it: it reads the H&E lazily with tifffile + dask, crops it and attaches the alignment itself.
  - `he_imagealignment.csv` maps H&E pixels to Xenium pixels: a 90° rotation and ×1.2896 scale, so an H&E pixel is about 0.274 µm. Translation is (−11896, 28914).
- **`annotation.geojson` coordinates are in H&E pixels.** Its 9 polygons are Tumor ×3, Necrosis, Immune infiltration ×2, Hemorrhage, Adipose tissue and Blood vessels.
  - 5 of the 9 have only a `name` and no `classification`, and one "Immune infiltration" is classified "Immune cells". The notebook sets each class from its name.
  - **Transform them with `he_imagealignment.csv` before use** (shapely `affine_transform` with `[a, b, d, e, xoff, yoff]` from rows 1–2). Untransformed, they appear rotated 90° in QuPath (confirmed by the maintainer).
  - The transform was checked against cell density: Immune infiltration about 12,100 cells/mm², Tumor about 6,800, Adipose about 560, whole image about 7,000.
  - **Blood vessels and Hemorrhage lie entirely outside the Xenium region**, because the H&E covers more tissue than Xenium imaged. Adipose is only 0.75 mm² inside it. Within the Xenium image, only Tumor ×3, Immune infiltration ×2, Necrosis and part of Adipose are usable. Use CD31 to show vessels instead.
- **QuPath GeoJSON import requirements.** A first export failed in QuPath 0.7 with `Unable to parse PathClass`. When exporting GeoJSON for QuPath:
  - give every `classification` both `name` and `color` (an RGB list), with one colour per class name;
  - keep only Polygon/MultiPolygon geometries, since clipping can produce a GeometryCollection.
- **Cropping spatialdata-io elements.** Cropped copies of its GeoDataFrames and DataFrames keep the old transforms in `.attrs`, so clear them before `ShapesModel`/`PointsModel.parse` with new transforms.
- **Don't display a SpatialData object after `write()` if an element is read lazily through tifffile** (`tifffile.imread(..., aszarr=True)`). Once the object has a path, its summary traces each image back to its files and fails with `'ZarrTiffStore' object has no attribute 'root'` (spatialdata 0.8). Print it before writing, or display the object read back with `read_zarr`. Found on the HPC run, 2026-11-14.
- **Sopa on the workshop Zarr.** `sopa.aggregate` writes to `table` by default, which would overwrite 10x's gene table. In session 6 pass `key_added` and `image_key="morphology_focus"` (there are two images).
- `protein_panel.json` lists 28 targets under `payload.panel.targets`, against `num_targets: 27`. The gene panel's `payload.targets` has 465 entries.

## Target layout
```
README.md            workshop page (overview, registration, instructors, preparation, programme, venue, slides, FAQ)
Pages/               Installation-Instructions.md, Data.md, Day1/ (session guides), Day2/
qupath/              Day 1 classifiers + class lists (no project: participants build their own)
notebooks/           05_from_qupath_to_python, 06_segmentation_and_qc … 08_spatial_and_next_steps
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
3. **Data** (in progress): build the cropped Zarr and the Day 1 QuPath files with `notebooks/extra/prepare_xenium_dataset.ipynb` (see Decisions).
   - Done: inspection of the real bundle (`Scripts/inspect_xenium.py`, see Data findings), QuPath loading test, crop choice, and the notebook itself (2026-11-13).
   - Run it headless with `XENIUM_RAW_DIR`, `XENIUM_OUTPUT_DIR`, `XENIUM_NAME`, `XENIUM_DOWNLOAD=0/1`, `XENIUM_CROP=full|x0,y0,x1,y1` (µm), `XENIUM_VALIDATE=0/1` and `XENIUM_ZIP=0/1`. Relative folders count from the repo root, because nbconvert runs kernels in `notebooks/extra/`.
   - Every step after reading has been checked on a small synthetic Xenium-like dataset: protein offset, H&E resampling, annotation transform, table links, OME-TIFF pyramids and Plane positions, and the zips. The final check (read the Zarr back, then `sopa.make_image_patches` + `sopa.segmentation.instanseg` on a central 1024 px tile) also runs.
   - First real-data run (HPC, 2026-11-14): reading through to the Zarr write worked (the write took 731 s for the crop), then the cell failed while displaying the object (fixed; see the tifffile gotcha in Data findings). Steps 10–12 haven't run on real data yet.
   - Second real-data run (2026-11-14): the Zarr was written by 09:17 (about 13 min). The run then crawled through step 10 for over 5 hours: the IF OME-TIFF had reached only 588 MB.
     - Cause: the TIFF writer read 512-row strips back through the whole lazy chain from 10x's raw files, re-reading each 4096 × 4096 source tile about 8 times per channel and rebuilding the smaller pyramid levels from scratch.
     - Fixed: step 10 now writes the QuPath TIFFs from the Zarr just saved (it is already cropped and corrected, and stores every level), reading 2048-row strips aligned to its chunks. Rechecked on the synthetic data: the TIFF matches the Zarr pixel for pixel at every level.
   - Every `print` in the notebook now goes through `log()`, which also appends to `<OUTPUT_DIR>/prepare_log.txt` with timestamps. On a headless run, follow it with `tail -f` (nbconvert shows nothing until the end).
   - **Third real-data run succeeded (2026-11-14), in about 14 min end to end.** Outputs are in `/nemo/.../spatial-bio-training/workshop_data` on the HPC, alongside `prepare_log.txt` and `executed.ipynb`.
     - Timings: reading 38 s, cropping about 20 s, Zarr write 722 s (now the slowest step, reading from the raw files), IF TIFF 45 s, H&E TIFF 16 s, Sopa check about 40 s.
     - Contents: region 7059 × 7059 px = 1.50 × 1.50 mm; 16,045 cells, 16,202 nuclei, 2,096,052 transcripts; `table` 16,045 × 405, `protein` 16,045 × 27; offset removed from 27 channels; annotations in the crop are Tumor and Immune infiltration.
     - Sopa + InstanSeg found 284 cells in the central 1024 px tile (about 6,000/mm²).
     - Sizes: Zarr 934 MB, `_if.ome.tif` 805 MB, `_he.ome.tif` 150 MB, `_10x_cells.geojson` 17 MB, `_annotations.geojson` 9 KB. About 1.9 GB in total.
     - **Alignment checked visually** on a 1/8-scale overlay of the exported TIFFs and GeoJSON: H&E nuclei coincide with DAPI across the crop, and the Tumor and Immune infiltration outlines follow the tissue.
   - **QuPath check passed (maintainer, 2026-11-14):** the IF and H&E OME-TIFFs and both GeoJSON files load, line up and look good in QuPath 0.7.
   - **Next:** rerun the notebook on the HPC (it now also writes `qupath/<NAME>_fovs.geojson`, see step 4, session 5), then upload the bundle to Zenodo, rerunning with `XENIUM_ZIP=1` or zipping the outputs, and add the link to `README.md` and `Pages/Installation-Instructions.md`.
   - Possible improvement for `XENIUM_CROP=full`: the notebook filters transcripts with dask (`points[inside].compute()`), which loads every transcript in the region. Fine for the crop; for the whole slide (77 M transcripts) it may need more memory than a laptop has. Filtering `transcripts.parquet` with pyarrow would be lighter.
4. **Day 2 notebooks**: 06 first (riskiest), then 05, 07, 08.
   - **05 drafted, NOT YET RUN (2026-11-15).** Files: `notebooks/05_from_qupath_to_python.ipynb` (exercise cells are stubs) and `solutions/05_from_qupath_to_python.ipynb`. The individual reads and the tile choice were tested (below), but the assembled notebook hasn't run end to end. The DAPI threshold now comes from automatic methods (below). The marker thresholds in the solution are placeholders until the run: CD3E 20, CD8A 15, CD68 20, PanCK 15.
     - Reads from `../data/qupath/` (the Day 1 files). The maintainer's copy is in `data/qupath/`, copied from `workshop_data/qupath` on the HPC.
     - Structure:
       1. A QuPath-to-Python table, then Jupyter basics.
       2. Open the IF TIFF with bioio (Bio-Formats, falling back to `bioio-ome-tiff`); dims, pixel size, channel names; read the tile lazily.
       3. Day 1 GeoJSON (annotations and 10x cells) with geopandas, overlaid via `imshow(extent=...)` in full-image pixels.
       4. Nuclei, **no fixed threshold** (decided 2026-11-15, to link back to the introductory workshop and show a QuPath limitation: its cell detection takes one fixed value):
          - Gaussian (sigma 1 px) and the histogram; `filters.try_all_threshold` (Fiji's "Try all"); the values of Otsu, Li, Yen, Triangle, Isodata and Mean, marked on the histogram; an optional ipywidgets slider.
          - `find_nuclei()`: mask, distance transform, `peak_local_max` (min distance 2.5 µm), watershed, small objects (< 10 µm²) removed.
          - Exercise 1: nuclei found by each method. Participants then set `METHOD` (default Otsu), which the rest of the notebook uses.
          - **"One image, or many?"**: read and smooth the whole DAPI channel (about 100 MB as read, float32 after smoothing), then compute the chosen method on the whole stitched image and per FOV (from `xenium_rcc_crop_fovs.geojson`). Show a map of the per-FOV values, then the tile segmented with the whole-image, own-FOV and own-tile thresholds.
          - Discussion: seams; mostly-empty or single-tissue FOVs (the 54 µm bottom slivers); 10x's images are already illumination-corrected, so here the FOV differences are mainly tissue content. Then `threshold_local` (20 µm block) as the adaptive extreme, and why InstanSeg avoids thresholds (per-patch normalisation).
       5. Cells: `expand_labels` (3 µm), then `measure_cells()` with `regionprops_table` (area in µm², centroid, mean of each channel).
       6. Marker histograms, `MARKER_THRESHOLDS` (exercise 2), composite phenotypes (CD8+ T cell, Other T cell, Macrophage, PanCK+, Other) and a phenotype map.
       7. **Key exercise 3:** `analyse(threshold, expansion)` over every method plus the whole-image threshold, and over expansions of 0–8 µm, plotting the cell count and % CD8+ T cells.
       8. The same classifier on 10x's cells (polygons drawn into a label image with `skimage.draw.polygon`) and on InstanSeg (`InstanSeg.eval_small_image` on DAPI + boundary stain, using its cells output), compared as a table and as phenotype maps.
       9. Save the threshold cells as QuPath detections (outlines traced with `skimage.measure.find_contours`, classification name and colour) to `../data/session5_cells.geojson`.
     - **Tile (chosen 2026-11-15): x 940–1140 µm, y 840–1040 µm** (px 4424–5365, 3953–4894). About 270 10x cells in the tumour, with CD8+ and CD3+CD8− T cells, CD68+ macrophages and PanCK+ cells. Its DAPI mixes large, dim tumour nuclei with small, bright lymphocytes, which is good for showing threshold trade-offs. The candidates compared were (1000, 1150), (400, 560) and (700, 600). The top-scoring windows on marker density were lymphoid aggregates (CD20 follicles) along the top edge, with no tumour.
     - Marker survey of the crop (scale2, 99th percentiles): DAPI 435, CD3E 83, CD8A 54, CD68 85, PanCK 31, E-Cadherin 13, Beta-catenin 14, CD31 46, Vimentin 141, CD45 78. B-cell follicles (CD20) sit top left, αSMA vessels follow the immune band, and PanCK is patchy in the tumour.
     - **Reading the tile, measured** (5 channels, 941 × 941 px, from `data/qupath/xenium_rcc_crop_if.ome.tif` on the maintainer's machine):
       - Bio-Formats (`dask_tiles=True`, `tile_size=(512, 512)`): opening 3.3 s, reading 1.5 s, peak 0.37 GB;
       - `bioio-ome-tiff`: opening 0.1 s, reading 2.3 s, peak 0.41 GB;
       - the pixels are identical. Both readers report dims T1 C35 Z1 Y7059 X7059, 0.2125 µm and all 35 channel names.
     - **bffile gotcha:** with Bio-Formats, `get_image_dask_data("CYX", C=[list of indices])` fails at `.compute()` with `NotImplementedError: fancy indexing with arrays is not supported`. Read one channel at a time (`get_image_dask_data("YX", C=index)`) and stack them; the notebook's `read_channel()` does this.
     - Day 1 GeoJSON as read by geopandas: annotations have `objectType`, `name` and `classification` (a dict with name and colour); the 10x cells have `objectType="detection"` and `name` (the 10x cell ID); 16,045 rows load in 1.7 s.
     - `rasterio` is installed (pulled in by another package) but not declared, so the notebook doesn't use it.
     - **Fields of view (checked 2026-11-15).** 10x's `aux_outputs/morphology_fov_locations.json` (inside `outs/aux_outputs.tar.gz`, 179 MB, not extracted on the HPC) gives `{"fov_locations": {name: {x, y, width, height}}, "units": "micron"}`: the top-left corner in slide µm, 151 FOVs of 629 × 748 µm each. It matches the extents of each FOV's transcripts (`fov_name`) to within 1–3 µm.
       - The crop overlaps 9 FOVs, a 3 × 3 grid (Y3–Y5, Z3–Z5, AA3–AA5) overlapping by about 25 µm. AA3–AA5 are 54 µm slivers along the bottom edge. The session tile is in Z5, about 13 µm from its left seam.
       - Otsu on smoothed DAPI: whole crop 153; per FOV 127 (Z4/Z5, tumour) to 184 (Y3, dense lymphoid aggregate). Li: whole crop 54; per FOV 47–72. The method matters far more than the FOV.
       - Windows gotcha: `aux` is a reserved device name, so a scratch folder can't be called `aux`.
     - **FOV grid added to the data bundle (decided 2026-11-15).** The preparation notebook now has `fov_boxes()` (section 6): it reads the JSON (extracted, or straight from `aux_outputs.tar.gz` with `tarfile`), falls back to `fov_name` extents in the transcripts, and returns `None` if neither exists. Boxes are crop-local and clipped to the region. Section 10 writes `<NAME>_fovs.geojson` into `qupath/` as annotations classed "Field of view" (colour 0, 200, 200).
       - Tested against the real JSON and the crop's transcripts through all four routes (JSON, tar.gz, fallback, none). The 2026-11-14 bundle doesn't have the file, so **rerun the preparation notebook on the HPC before the Zenodo upload**.
       - Meanwhile, `data/qupath/xenium_rcc_crop_fovs.geojson` on the maintainer's machine was written with the same code from the extracted JSON, as a local stand-in for developing session 5.
       - The README text the notebook writes into the bundle doesn't mention the FOV file yet.
     - **Next:** run the solution notebook end to end, set the thresholds from the real histograms, check the figures and the timings, and check that the saved GeoJSON imports into QuPath. Then update notebook 06's start: a SpatialData introduction, and the session 5 GeoJSON as a third segmentation in SegTraQ.
     - Tools used while drafting lived in the session scratchpad and may be lost: the percent-format source `nb05.py`, the converter `py_to_nb.py` (lines beginning `#> ` are the exercise stubs) and the runner `run_cells.py` (runs cells in turn, times them, saves figures, stops at the first error). If they're gone, treat the solution notebook as the source. Moving the converter and runner into `Scripts/` would avoid this. Participants keep the workshop data in `data/` in the workshop folder (gitignored), so the notebooks read `../data/xenium_rcc_crop.zarr`. The installation page should say so once the Zenodo link exists.
   - **06 drafted; first end-to-end run INCOMPLETE (2026-11-15).** Files: `notebooks/06_segmentation_and_qc.ipynb` (exercise cells are stubs) and `solutions/06_segmentation_and_qc.ipynb` (complete). Every API step was prototyped on the real crop on the 32 GB desktop (below).
     - The run used the maintainer's Windows machine: 15.4 GB RAM, with about 2.5 GB free even when idle, because PyCharm, Firefox, CrashPlan, Dropbox and OneDrive were open. That is close to the laptops participants will bring. The workshop Zarr was copied from the HPC into `data/`, which took 14.5 min over the `Z:` share at about 1 MB/s. The copy is identical: 942 files, 972,143,490 bytes.
     - **Fixed:** `REGION` must be a list, not a tuple. `sd.bounding_box_query` (spatialdata 0.8) converts only lists to arrays, and fails on a tuple slice with `'tuple' object has no attribute 'dtype'`. Changed in both notebooks.
     - Per-cell timings on that machine: imports + `read_zarr` 77 s; overview figure 2.6 s; region query 6.5 s; 10x zoom figure 3.0 s. Both figures were produced.
     - **Stall, since explained:** the first `sopa.segmentation.instanseg` call (DAPI only, 9 patches of 1024 px) ran for about 30 min without finishing. Claude Code then stopped it because the machine was critically low on memory.
     - **Diagnosis (same day, same machine):** the machine was swapping, and the notebook isn't at fault. The diagnostic ran after PyCharm and other apps were closed, leaving 7.5 GB free; CrashPlan, which IT manages, kept running. Each case ran in a fresh process. The machine has 4 physical cores, and PyTorch 2.15 (CPU) used 4 threads.
       - One central 1024 px tile, read lazily from the Zarr with all 35 channels: InstanSeg 6.5 s, process peak 0.9 GB, 284 cells.
       - The same tile with only DAPI loaded into memory first: 6.6 s, peak 0.9 GB, 284 cells. Lazy reading costs nothing: Sopa reads only the requested channel.
       - The notebook's whole 440 µm region (`bounding_box_query` of every element, 9 patches): region query 1.9 s; InstanSeg 29.5 s, peak 1.2 GB; 1,249 cells found, 1,117 after merging the patches.
       - Imports took 14 s, against 77 s in the stalled run, which is further evidence of swapping then.
       - So InstanSeg on the region fits a laptop comfortably. **Participants need several GB of free RAM**, so the installation page and the session should tell them to close other apps. The notebook's time estimates ("less than a minute" per step) hold on this machine.
     - Sopa warns "Running without parallelization backend can be slow" and suggests `sopa.settings.parallelization_backend = 'dask'`. It isn't needed at region scale; untested for the whole-crop cell.
     - **Next:** rerun the solution notebook end to end on this machine with memory free, check the figures, then commit both notebooks without outputs.
     - Running cells headless: nbconvert shows nothing until the end. A small runner that `exec`s each code cell in turn, timing each, saving figures (Agg backend) and stopping at the first error, is quicker to debug with. It lived in the session scratchpad, so it may need rewriting.
   - Exercise/solution sync: the two versions were generated from one percent-format script whose `#> ` lines are the exercise stubs. The script and converter lived in the session scratchpad and may be lost, so treat the solution notebook as the source and keep the exercise version in step by hand (or add a small `Scripts/` converter).
   - Structure: (1) choose a 440 µm region (`REGION = [530, 530, 970, 970]` µm, about 1,200 cells) with `bounding_box_query` in `microns`, copied into a new in-memory `SpatialData`; (2) 10x's segmentation (`segmentation_method`, a 100 µm zoom with DAPI and the boundary stain); (3) InstanSeg via Sopa with DAPI only, then DAPI + `ATP1A1/CD45/E-Cadherin` (exercise 1), plus `target="nuclei"`; (4) `sopa.aggregate` with `key_added="instanseg_table"` and both filters at 0, then `sopa.spatial.assign_transcript_to_cell`; (5) SegTraQ baseline and region similarity for 10x vs InstanSeg; (6) exercise 2: grow the outlines with `sopa.shapes.expand_radius(..., 0.5, no_overlap=True)` and remeasure.
   - **Region or whole crop (decided 2026-11-15):** the setup cell has `WHOLE_CROP = False`. When it's `True`, section 1 sets `REGION` to the whole crop (from the image size), and the *whole* session runs on it unchanged: segmentation, aggregation, SegTraQ and the exercises. This replaced a separate section 7 that only segmented the whole crop and compared cell counts. A whole-crop run means 3 InstanSeg runs of about 6 min each on the desktop, plus SegTraQ on about 16,000 cells (region similarity took about 20 s for 1,200 cells), so expect 30 min or more on a laptop. Not yet timed; memory at that scale is also untested.
   - Exercise/solution check: comparing the two notebooks cell by cell, they should differ only in the two exercise cells (`# Your code here`). Check this after every edit.
   - Measured on the maintainer's desktop (Xeon E5-2630 v4, 10 cores, 32 GB RAM, CPU only):
     - InstanSeg: a 1024 px tile takes 12–15 s; the 2048 px region about 45 s; the **whole crop with DAPI only takes 370 s** and finds 14,610 cells (10x has 16,045). Too slow and risky to run live on 30 mixed laptops, hence the 440 µm region by default and `WHOLE_CROP` as an opt-in. The whole crop with DAPI + boundary stain hasn't been timed.
     - Central 1024 px tile: DAPI only gives 284 cells (median 39 µm²); DAPI + boundary stain gives 315 cells (median 48 µm²).
     - 2048 px central region: 10x has 1,212 cells, 19% of transcripts unassigned, median 72 transcripts per cell, median area 69 µm², nucleus–cell IoU 0.42, border admixture 0.10. InstanSeg (DAPI + boundary) has 1,252 cells, 47% unassigned, median 48 transcripts per cell, median area 47 µm², IoU 0.62, border admixture 0.095. SegTraQ baseline takes about 1 s and region similarity about 20 s on this region.
     - Expanding the outlines (exercise 2) is not yet measured.
   - **Sopa gotchas** found while prototyping:
     - `sopa.settings.auto_save_on_disk` is on, so Sopa writes results into the Zarr of a backed `SpatialData`. Always segment an in-memory copy, never `sd.read_zarr(...)` of the workshop data directly.
     - Sopa names its cells in 10x style (`aaaaaaaa-1`), which can be mistaken for 10x IDs.
     - InstanSeg outlines are stored in image pixels (with transforms), while 10x outlines and transcripts are in µm. Use `sd.transform(..., to_coordinate_system="microns")`.
     - `assign_transcript_to_cell(unassigned_value=0)` returns 1-based positions, not cell names.
   - **SegTraQ 0.0.7 gotchas:**
     - It wants one segmentation at a time, with fixed keys (`transcripts` with `cell_id`, `cell_boundaries` with index name `cell_id`, `table` with an `obs["cell_id"]`), in one unit. The notebook's `run_segtraq()` helper packages each segmentation in µm.
     - It modifies the object it is given (it filters transcripts with qv < 20 and controls, and resets shapes indexes and CRS), so give it a copy.
     - The workshop tables have no `x_centroid`/`y_centroid`; pass `tables_area_key=None` and both centroid keys as `None` so it computes them from the outlines.
     - Pass `nucleus_shapes_cell_id_key=None`: nuclei are matched to cells by overlap.
5. **Day 1**: port the QuPath exercises to the RCC data and write the `Pages/Day1/` guides (QuPath GUI work, led by the instructors).
   - **Adapt the IF exercise's markers to RCC.** PanCK is sparse and patchy in the workshop crop (common in RCC), so it won't separate tumour from stroma the way it did in the lung image. Choose more suitable markers instead (candidates to check in QuPath: E-Cadherin, Beta-catenin, Vimentin, CD31, alphaSMA).

## Open questions
- Does QuPath ignore OME `Plane PositionX/PositionY`? Believed so; it doesn't matter under option A.
- Source and sharing terms of the original liver `.vsi` and `LungImg1.ome.tif` course images (the maintainer is enquiring).
