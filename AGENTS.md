# AGENTS.md

This repo holds the material for a **two-day workshop on spatial biology/omics analysis** run by the Crick: Day 1 in QuPath, Day 2 in Python. It is modelled on [introduction-to-image-analysis](https://github.com/FrancisCrickInstitute/introduction-to-image-analysis). The full plan, with rationale, is in the shared doc [Spatial Biology Workshop Plan](https://claude.ai/artifact/CnmDq3CUzc3fMptRAinEtY).

The repo began as a fork of the [CellSurvey](https://github.com/FrancisCrickInstitute/CellSurvey) pipeline. That code was removed in the teardown step (step 1), and its history stays in git. For CellSurvey's architecture, gotchas and its survey of related tools (PANORAMIC, CELESTA, Novae, segger, Spotiflow, etc.), read **upstream `AGENTS.md`**. That survey is the source material for session 8, "evaluating new tools".

## Status

**2026-11-17: a complete first draft of the Day 2 material exists, and work is paused while the maintainer tests it.**
- **Steps 1 (teardown) and 2 (environment)** are done.
- **Step 3 (data)** is nearly done. `notebooks/extra/prepare_xenium_dataset.ipynb` ran on the real data on the HPC (2026-11-14), and the QuPath files have been checked in QuPath. It now also writes the fields-of-view GeoJSON, so it must be **rerun on the HPC before the Zenodo upload**, which is still to do.
- **Step 4 (Day 2 notebooks)**: all four are drafted, and every solution runs end to end:
  - **05** From QuPath to Python;
  - **06** SpatialData, segmentation and QC;
  - **07** cell types;
  - **08** spatial statistics, niches and evaluating tools (added 2026-11-17).

  Timings: 19 s, 104 s and 50 s for 05–07 on the 128 GB workstation; 08 took 41 s on the 32 GB desktop. Each peaked at 0.7–1.4 GB. The maintainer is now reading through all four notebooks.
- **No Day 1 guides exist yet.** Day 1 session 4 must end by exporting the classified cells for session 7 (see Decisions made).
- **Everything still to do is listed under [Remaining work](#remaining-work).**

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
  - Live segmentation runs on small areas only: a 200 µm tile in session 5 and a 440 µm region in session 6 (`WHOLE_CROP` is an opt-in). Whole-crop analyses (session 7) use 10x's cells and tables from the workshop Zarr. Each notebook saves what the next one needs (`session5_cells.geojson`, `session6_cells.zarr`, `session7_cell_types.csv` in `data/`), and the next one falls back to the workshop data if a file is missing. There are no separate precomputed checkpoints in the download (this replaced the original plan of one Zarr per notebook).
  - Keep memory use modest (aim for 8–16 GB RAM laptops), and avoid loading whole images or all 2.1 million transcripts at once.
  - The installation page and `pixi run check-full` must be done before the day. Plan time to chase attendees whose check fails.
- **Transcripts on Day 2 only** (decided 2026-11-14). Day 1 has no transcript import.
- **Session 5 = "From QuPath to Python"** (decided 2026-11-15). Before the full InstanSeg/Sopa analysis, participants redo a simple Day 1-style analysis in Python on a small tile (about 200 µm):
  - open the **same OME-TIFF and GeoJSON they used in QuPath** (not the Zarr). It is the more transferable skill (their own data will be TIFFs and proprietary formats), and it gives SpatialData a reason to exist when transcripts arrive in session 6;
  - threshold DAPI with **automatic methods** (Otsu, Li, Yen, Triangle, Isodata, Mean; `try_all_threshold`, like Fiji's "Try all") rather than a fixed value, linking back to the introductory workshop and to a QuPath limitation (its cell detection takes one fixed value);
  - show that **no single threshold suits a large stitched image**, however it was chosen: compare one threshold for the whole image with one per field of view (the equivalent of the introductory workshop's "one value per image"), then local thresholding as the extreme;
  - split touching nuclei (distance transform + watershed), grow nuclei into cells (`expand_labels`), measure per-cell marker intensities (`regionprops_table`), and classify with single-marker thresholds combined into phenotypes (as in QuPath's composite classifier);
  - **key exercise:** sweep the threshold method and the expansion distance, and see how cell counts, cell areas and the percentage of a phenotype (e.g. CD8+ T cells) change. Segmentation choices change biological conclusions;
  - end with InstanSeg on the same tile as a teaser, and save the outlines as GeoJSON (back to QuPath; a third segmentation for the SegTraQ comparison in session 6).
  - The deeper SpatialData tour (why a container, coordinate systems, transcripts, tables, H&E alignment, loading Day 1 GeoJSON into the Zarr) moves to the start of session 6.
- **Images are read with bioio, Bio-Formats first, pure Python as fallback** (decided 2026-11-15). Participants know Bio-Formats from Fiji.
  - `BioImage(path, reader=bioio_bioformats.Reader, dask_tiles=True, tile_size=(512, 512))` reads only the tiles it needs. If that raises **anything**, fall back to `BioImage(path, reader=bioio_ome_tiff.Reader)`, which gives the same channel names, pixel size and dimensions but reads whole planes (about 100 MB per channel of the crop, so read only the channels needed). bioio picks `bioio-ome-tiff` by default for `.ome.tif`, so Bio-Formats must be requested explicitly.
  - bioio-bioformats (through `bffile`) downloads its **own Java runtime (cjdk) and the Bio-Formats jars (Maven)** on first use. No installed Java is needed, and Fiji's bundled Java isn't used. A failed download surfaces as `UnsupportedFileFormatError` ("None of the specified readers were able to read this image"), with `CERTIFICATE_VERIFY_FAILED` inside it on intercepting networks. It failed that way in Claude Code's shell (2026-11-15); the fallback worked.
  - Neither reader reads pyramid levels (both read level 0), so a whole-crop overview means downsampling a channel.
  - `pixi run check-full` now tests both readers on a synthetic OME-TIFF: the fallback must pass, and a Bio-Formats failure is a `[WARN]` (the run still ends "Ready for the workshop, with warnings"). **Bio-Formats via bioio works** (maintainer's Windows machine, off the VPN, 2026-11-15): the first `check-full` downloaded Azul Zulu JRE 11.0.33 (38.6 MB) into `%LOCALAPPDATA%\cjdk\cache` plus the Bio-Formats jars, then read the test tile correctly. Later runs work from the cache with no network, including in Claude Code's shell. The line `jar tool not found at ...\bin\jar.exe` during that first run is harmless (the JRE has no `jar` tool). macOS and Linux are untested.
  - Dependencies added by the maintainer (2026-11-15): `bioio`, `bioio-bioformats`, `bioio-ome-tiff`, `scikit-image`, `geopandas` in `pixi.toml` (relocked) and `requirements.txt`.
- **Session 7 = a worked example, then the same on the participants' own work** (decided 2026-11-16). The pattern may suit session 8 too.
  - **Worked example (everyone sees the same results):** 10x's cells for the whole crop (the `table` and `protein` tables in the workshop Zarr), compared with **reference Day 1 phenotypes** for those same cells. They join exactly, because each object's `name` is its 10x cell ID.
  - **Exercise 3 (own work):** the participant's InstanSeg cells from session 6 (`data/session6_cells.zarr`, written at the end of notebook 06), compared with their **own Day 1 phenotypes** (`data/day1_cells.geojson`, exported in Day 1 session 4). The two segmentations don't share IDs, so cells are matched by position: each session 6 cell gets the class of the Day 1 cell containing its centre.
  - **Fallbacks:** without `session6_cells.zarr`, 10x's cells in the session 6 region; without `day1_cells.geojson`, the reference phenotypes. The notebook says which it used.
  - **This sets two requirements outside the notebooks:**
    - **Day 1 session 4** must have participants export their classified cells from QuPath as GeoJSON (File › Export objects as GeoJSON, "Export as FeatureCollection"), saved as `data/day1_cells.geojson` in the workshop folder. Their cells must have classifications, and must cover the session 6 region (x 820–1260, y 720–1160 µm), for the matching to be useful.
    - **The instructors** must make the reference file `qupath/xenium_rcc_crop_10x_phenotypes.geojson` in QuPath: import `xenium_rcc_crop_10x_cells.geojson` into the IF image, add intensity features, classify with single-measurement classifiers combined into a composite classifier, and export as GeoJSON. It must keep each cell's `name` (its 10x ID). It then goes into the Zenodo bundle. Until then, `Scripts/make_reference_phenotypes.py` writes a **stand-in** of the same shape (see Notebook tools).

- **The repo is published as a GitHub Pages site** (decided 2026-11-18; live the same day), at https://franciscrickinstitute.github.io/spatial-bio-training/, with the README as its home page, like introduction-to-image-analysis. `_config.yml` sets it up:
  - **Theme:** Just the Docs, as a remote theme pinned to `v0.12.0` (`remote_theme: just-the-docs/just-the-docs@v0.12.0`, plugins `jekyll-remote-theme` and `jekyll-include-cache`). It builds with GitHub's standard "Deploy from a branch", with no Actions workflow. Update the pin deliberately.
  - **Navigation:** titles and order come from `defaults:` in `_config.yml` (README = "Home", installation page = "Installation"), not from front matter, because GitHub shows front matter as a table at the top of a file. Add new pages (e.g. `Pages/Day1/...`) to `defaults:` the same way. The notebooks and solutions are external navigation links to GitHub.
  - **Excluded from the site:** `AGENTS.md`, `CLAUDE.md`, `Scripts/`, `notebooks/`, `solutions/`, `assets/`, `data/`, `qupath_content/`, the pixi files and `requirements.txt`. If the README starts using images from `assets/`, take `assets/` out of the exclude list.
  - **Rules for Markdown that appears on the site** (README and `Pages/`):
    - Link notebooks, folders and excluded files with full GitHub URLs (`https://github.com/FrancisCrickInstitute/spatial-bio-training/blob/main/...`). Pages would serve `.ipynb` files raw, and has no folder listings.
    - Relative links between `.md` pages are fine, because GitHub Pages converts them to the rendered pages.
    - Don't use GitHub-only syntax, such as alert blocks (`> [!NOTE]`), which show as literal text.
    - Jekyll runs every published page through Liquid, **including the text inside code blocks**, so `{{ ... }}` and `{% ... %}` are processed (or vanish) on the site while looking fine on GitHub. Wrap any code that contains them (for example Python with doubled braces in an f-string) in `{% raw %}` ... `{% endraw %}`.
    - Keep maintainer-only content (to-do lists, HPC paths) out of the README; it belongs here.

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
README.md            workshop page (overview, registration, instructors, preparation, programme, venue, slides, FAQ); the website's home page
_config.yml          GitHub Pages / Just the Docs settings (see Decisions made)
Pages/               Installation-Instructions.md, Data.md, Day1/ (session guides), Day2/
qupath/              Day 1 classifiers + class lists (no project: participants build their own)
notebooks/           05_from_qupath_to_python, 06_segmentation_and_qc, 07_cell_types, 08_spatial_and_next_steps
                     extra/prepare_xenium_dataset.ipynb (post-workshop: download + prepare the full slide; also builds the bundle)
solutions/           completed notebooks (committed without outputs so far; see Open questions)
Scripts/             check_install.py; maintainer tools: inspect_xenium.py, make_fovs_geojson.py and the notebook tools below
assets/
pixi.toml
```

`assets/` still holds two CellSurvey output figures. They can be replaced once the workshop data produces its own.

### Notebook tools (`Scripts/`, maintainer-only, added 2026-11-16)
Run them with `pixi run python Scripts/<name>.py` (or the environment's own Python, `.pixi/envs/default/python.exe`). They can be removed from the repo later if they stop being useful.
- `run_notebook_cells.py NOTEBOOK FIG_DIR [first] [last]`: runs a notebook's code cells without Jupyter, from the notebook's folder. Prints the time, the process memory and the output of each cell, including the value of its last expression, saves figures as PNGs and stops at the first error. Uses `psutil`, which comes in with the environment's other packages but isn't declared.
- `check_exercises.py`: compares every `notebooks/*.ipynb` with its `solutions/` copy and lists the cells that differ. Only the exercise cells should differ.
- `show_notebook_cells.py NOTEBOOK TEXT...`: prints the cells containing some text, with their indexes.
- `make_reference_phenotypes.py [ZARR] [QUPATH_DIR]`: writes the **stand-in** `xenium_rcc_crop_10x_phenotypes.geojson` (10x's cells, as QuPath detections named by 10x cell ID, classified from the `protein` table). The classifier uses one threshold per marker, from Otsu on arcsinh(x/5), rounded: CD3E 8, CD8A 7, CD4 3, CD20 8, CD68 6, CD163 3.5, CD31 5, αSMA 3.5. The first matching rule wins: CD8+ T, CD4+ T, Other T, B cell, Macrophage, Endothelial, Smooth muscle, Other. Replace its output with the instructors' QuPath export when it exists.
- `make_fovs_geojson.py OUTS_DIR OUTPUT [crop]`: writes `<NAME>_fovs.geojson` from 10x's raw `outs` folder, using the same logic as the preparation notebook. Keep the two in step.
- Editing notebooks by script: Git stores the `.ipynb` files with LF and checks them out with CRLF (`core.autocrlf`). Normalise to LF before matching text, and check the result with `json.loads` before writing.

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
   - **05 drafted; the solution runs end to end (2026-11-16).** Files: `notebooks/05_from_qupath_to_python.ipynb` (exercise cells are stubs) and `solutions/05_from_qupath_to_python.ipynb`. The DAPI threshold comes from automatic methods (below).
     - **Threshold decisions (2026-11-16):**
       - **Default `METHOD = "Triangle"`.** On the tile it finds 228 nuclei with whole, smooth outlines on the large, dim tumour nuclei. By comparison, Otsu finds 147 and misses most tumour nuclei, Li 238 but breaks textured dim nuclei into pieces, and Mean 234. Triangle suits a large background peak with a long, thin tail of nuclei. Otsu stays in exercise 1 as the cautionary example. The text after exercise 1 suggests Triangle and says why.
       - **Yen** finds no nuclei on this tile (threshold 630, above almost every pixel). Exercise 1 asks why, and exercise 3 explains its 0-cell, NaN row.
       - **Marker thresholds stay manual** (exercise 2, read off the per-cell histograms, as with QuPath's single-measurement classifier). Solution values: **CD3E 10, CD8A 12, CD68 15, PanCK 5**, replacing the placeholders 20, 15, 20, 15. On the Triangle cells (3 µm expansion), 36%, 37%, 24% and 14% of cells are positive. CD8A is stable across 8–15 because its gap is real. PanCK 5 lands mostly on the bright PanCK patches, while 3 picks up dim background. CD3E and CD68 still need a visual check at full resolution, in the notebook or in QuPath.
       - Rejected: automatic marker thresholds (e.g. Otsu on arcsinh of per-cell means, as `make_reference_phenotypes.py` does), so that participants keep the judgement QuPath users make on Day 1.
     - **Run after the decisions (2026-11-16, 32 GB Xeon desktop, Bio-Formats):** 68 s, peak 1.1 GB, every cell ran.
       - Phenotypes (Triangle, 3 µm): Other 89, CD8+ T cell 76, Macrophage 35, PanCK+ 22, Other T cell 6.
       - Exercise 3 (CD8+ T cells / PanCK+): Otsu 44% / 3% (147 cells); Li 30% / 11%; Triangle 33% / 10%; Isodata 44% / 4%; Mean 32% / 12%; whole-image Triangle 32% / 10%; Yen 0 cells. Expansion 0 → 8 µm: CD8+ 34% → 25%, PanCK+ 6% → 17%.
       - Per-FOV Triangle thresholds 20–30, against 24 for the whole image.
       - Same classifier on three segmentations (threshold + watershed / 10x / InstanSeg): CD8+ T cells 33% / 34% / 35%; PanCK+ 10% / 8% / 10%. With a sensible method the segmentations agree, so the big swings come from the threshold method and the expansion. That makes a sharper teaching message than before.
       - Small leftovers: the optional slider still starts at Otsu's value; saving `session5_cells.geojson` prints a geopandas "'crs' was not provided" warning.
     - **First full run (2026-11-16)** on a 128 GB Windows workstation with spatialdata 0.8.0, reading through Bio-Formats: every cell ran, 19 s in total, peak process memory 1.4 GB (the whole-crop DAPI read in the FOV section). The memory figure should hold on laptops; the timings will be slower there.
     - **Fixed:** `gpd.read_file` labels GeoJSON as longitude/latitude (EPSG:4326, the GeoJSON default), so geopandas' `.plot()` "corrects" the aspect for latitude and fails with `aspect must be finite and positive` on pixel coordinates. Both notebooks now read the Day 1 GeoJSON through a `read_geojson()` helper that calls `.set_crs(None, allow_override=True)`, with a short explanation for participants.
     - Results on the tile:
       - DAPI thresholds and nuclei: Otsu 135 → 147, Li 51 → 238, Yen 630 → 0, Triangle 23 → 228, Isodata 131 → 146, Mean 43 → 234; whole image (Otsu) 138 → 144. For comparison, 10x has 271 cells in the tile and InstanSeg 296.
       - Otsu and Isodata miss most of the large, dim tumour nuclei. That makes the method choice a strong teaching point, but with the default `METHOD = "Otsu"` the later sections run on only about half the cells, and few tumour (PanCK+) cells.
       - Yen's threshold is above almost every pixel, so it finds no nuclei and gives NaN rows in the exercise 3 table. Worth a sentence in the notebook, so participants aren't confused.
       - Per-FOV Otsu thresholds: 113 (Z4, AA3, AA4) to 169 (Y3).
       - Expansion (Otsu, current marker thresholds): CD8+ T cells 35% at 0 µm, 40% at 1 µm, 23% at 3 µm, 9% at 8 µm. Larger cells dilute the mean of membrane markers.
       - Same classifier, three segmentations (current thresholds): CD8+ T cells 23% (threshold + watershed), 26% (10x), 26% (InstanSeg).
       - Marker histograms (per-cell means): CD3E has a gap at about 8–10, CD8A at about 8–12; CD68 has a tail with no clear gap; PanCK is dim everywhere (max cell mean 19). Candidate thresholds CD3E 10, CD8A 12, CD68 15, PanCK 5 raise CD8+ T cells from 23% to 44% (Otsu nuclei) and from 14% to 30% (Li nuclei); dense T-cell clusters may inflate this through spill-over between neighbours. (Adopted on 2026-11-16, see the threshold decisions above.)
     - The saved `../data/session5_cells.geojson` has `classification` as a nested `{name, color}` object, as QuPath expects. Not yet imported into QuPath.
     - The fields-of-view GeoJSON on the workstation (`data/qupath/xenium_rcc_crop_fovs.geojson`) was rebuilt from `outs/aux_outputs.tar.gz` on the HPC share with the preparation notebook's `fov_boxes()` logic: 9 FOVs, as expected.
     - Reads from `../data/qupath/` (the Day 1 files). The maintainer's copy is in `data/qupath/`, copied from `workshop_data/qupath` on the HPC.
     - Structure:
       1. A QuPath-to-Python table, then Jupyter basics.
       2. Open the IF TIFF with bioio (Bio-Formats, falling back to `bioio-ome-tiff`); dims, pixel size, channel names; read the tile lazily.
       3. Day 1 GeoJSON (annotations and 10x cells) with geopandas, overlaid via `imshow(extent=...)` in full-image pixels.
       4. Nuclei, **no fixed threshold** (decided 2026-11-15, to link back to the introductory workshop and show a QuPath limitation: its cell detection takes one fixed value):
          - Gaussian (sigma 1 px) and the histogram; `filters.try_all_threshold` (Fiji's "Try all"); the values of Otsu, Li, Yen, Triangle, Isodata and Mean, marked on the histogram; an optional ipywidgets slider.
          - `find_nuclei()`: mask, distance transform, `peak_local_max` (min distance 2.5 µm), watershed, small objects (< 10 µm²) removed.
          - Exercise 1: nuclei found by each method. Participants then set `METHOD` (default Triangle since 2026-11-16), which the rest of the notebook uses.
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
       - The README text the notebook writes into the bundle mentions the FOV file (added 2026-11-17).
     - **Next:** check the CD3E and CD68 thresholds visually at full resolution, import the saved GeoJSON into QuPath, and time the notebook on a laptop-class machine. (Notebook 06 now has the SpatialData introduction and compares the session 5 cells; done 2026-11-16.)
     - The percent-format source and converter used to draft the notebook are lost; the solution notebook is the source. Participants keep the workshop data in `data/` in the workshop folder (gitignored), so the notebooks read `../data/xenium_rcc_crop.zarr`. The installation page should say so once the Zenodo link exists.
   - **06 drafted; the solution runs end to end (2026-11-16).** Files: `notebooks/06_segmentation_and_qc.ipynb` (exercise cells are stubs) and `solutions/06_segmentation_and_qc.ipynb` (complete). Every API step was prototyped on the real crop on the 32 GB desktop (below).
     - **First complete run (2026-11-16)** on the 128 GB workstation (spatialdata 0.8.0, region mode): 93 s in total, peak process memory 1.3 GB. Each InstanSeg run took 13–14 s, and SegTraQ about 11 s per segmentation. All five figures were checked: region overview, 10x zoom, the three segmentations, QC histograms and the expanded outlines.
     - **Fixed:** the exercise 2 setup cell (growing the outlines) had never run. `sopa.shapes.expand_radius` returns a GeoDataFrame whose `.attrs` still holds the transforms, so passing `transformations=` to `ShapesModel.parse` raised "Transformations are both specified for the element and also passed as an argument". It now clears `.attrs` first, in both notebooks (the same gotcha as cropping spatialdata-io elements).
     - Results on the old region (`[530, 530, 970, 970]`, before the restructure below): 10x 1,231 cells; InstanSeg with DAPI only 1,117 (median 37.5 µm²), with DAPI + boundary 1,290 (47.8 µm²), nuclei 1,332.
     - SegTraQ (10x / InstanSeg / InstanSeg grown by half the mean radius):
       - transcripts outside every cell: 19% / 47% / 22%;
       - median transcripts per cell: 71 / 48 / 74.5; median genes per cell: 31 / 24 / 32;
       - median area: 69 / 48 / 91 µm²;
       - nucleus–cell IoU: 0.43 / 0.62 / 0.34;
       - border admixture: 0.06 / 0.07 / 0.06.
       - Growing the outlines recovers most transcripts without raising admixture, but cells become larger than 10x's and IoU drops. A good discussion point for the exercise.
     - Runs on the 16 GB laptop-class machine are still to be timed with memory free.
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
     - **Restructured (2026-11-16)** for the new programme. Run end to end on the 128 GB workstation: 104 s, peak 1.4 GB.
       - New section 1, "One container for everything: SpatialData", before any segmentation:
         - the five element types against their session 5 equivalents; the image pyramid, which stays a lazy dask array;
         - transcripts: 2,096,052 of 515 features (genes plus controls), with the top genes (VIM 473k, HLA-DRA 120k); counting takes 0.1 s;
         - tables: `uns["spatialdata_attrs"]` (the link to `cell_boundaries` through `cell_id`), and 10x cells in the session 5 tile coloured by CD8A protein, joined by hand from the `protein` table;
         - coordinate systems: the transformations of the image, transcripts, outlines and H&E (an affine: 90° rotation and about 0.274 µm per H&E pixel);
         - H&E next to DAPI in an 80 µm window, both made with `sd.bounding_box_query` + `sd.rasterize(..., target_coordinate_system="microns", target_unit_to_pixels=1/PIXEL_SIZE)` (1.5 s), with 10x's outlines on both. They line up;
         - `read_qupath_geojson()`: QuPath GeoJSON → `ShapesModel` with `global` Identity and `microns` Scale(0.2125), keeping the classification name. It loads `../data/session5_cells.geojson`. If that file is missing, section 7 is skipped with a message.
       - **The region moved to `[820, 720, 1260, 1160]` µm**, centred on the session 5 tile (940–1140, 840–1040 µm), so InstanSeg covers it. `ZOOM` is now `(1000, 900, 1100, 1000)`, inside the tile. Region: 10x 1,284 cells; InstanSeg with DAPI only 1,113, with DAPI + boundary 1,315.
       - New section 7, "Your session 5 cells": the session 5 cells are added to `region`, aggregated and assigned like InstanSeg's, then 10x, InstanSeg and session 5 are compared with SegTraQ on the tile only (`tile_qc()`).
         - Cells count if their centre is in the tile. Transcripts assigned to cells centred outside it are dropped, so cells cut by the edge don't count against anyone.
         - The session 5 cells use InstanSeg's nuclei, because session 5 didn't save its nuclei.
         - `run_segtraq()` gained an optional `points` argument for this.
       - Tile results (10x / InstanSeg / session 5 with Otsu and 3 µm): cells 242 / 262 / 147; transcripts outside every cell 26% / 52% / 62%; median transcripts per cell 87 / 61.5 / 111; median area 62 / 46 / 87 µm²; IoU 0.45 / 0.62 / 0.32; border admixture 0.03 / 0.05 / 0.08. The Otsu cells miss the dim tumour nuclei, as session 5 showed.
       - **Rerun with session 5's new Triangle default (2026-11-16, 32 GB Xeon desktop):** 346 s in total (against 104 s on the 128 GB workstation), peak 1.4 GB. Tile results (10x / InstanSeg / session 5 Triangle): cells 242 / 262 / 228; transcripts outside every cell 26% / 52% / 27%; median transcripts per cell 87 / 61.5 / 107.5; median genes 35 / 27 / 40.5; median area 62 / 46 / 94 µm²; IoU 0.45 / 0.62 / 0.30; admixture 0.03 / 0.05 / 0.08. The session 5 cells now capture transcripts as well as 10x's, but they are the largest and have the most border admixture, so some of those transcripts come from neighbours. Section 7's questions now ask about this ("Is that all good news?"). Region results are unchanged.
       - Region results (10x / InstanSeg / grown): transcripts outside every cell 20% / 47% / 22%; median transcripts per cell 97 / 66 / 102; median area 74 / 51 / 92 µm²; IoU 0.42 / 0.61 / 0.35; admixture 0.05 / 0.07 / 0.05.
       - **Fixed:** on the new region `expand_radius(..., no_overlap=True)` left 2 empty geometries ("Found 2 NaN geometries after removing the overlap"), and `sopa.aggregate` then failed with a shape mismatch in `obsm["spatial"]`. The exercise 2 setup now drops empty geometries.
       - Section numbers: 1 SpatialData, 2 region, 3 10x, 4 InstanSeg, 5 aggregation, 6 SegTraQ, 7 session 5 cells, 8 exercise (grow the cells).
     - **Next:** time a full run on the 16 GB machine with memory free.
     - Running cells headless: nbconvert shows nothing until the end, so use `Scripts/run_notebook_cells.py` (see Notebook tools).
     - **Save step added (2026-11-16):** a last section writes the participant's `instanseg_cells` outlines and `instanseg_table` (key `table`) to `../data/session6_cells.zarr` (1 s; 1,315 cells), for session 7.
   - **07 drafted; the solution runs end to end (2026-11-16).** Files: `notebooks/07_cell_types.ipynb` and `solutions/07_cell_types.ipynb` (42 cells; 3 exercise cells). On the 128 GB workstation it took 50 s in total, with a peak of 1.0 GB. All figures were checked.
     - Sections:
       1. two tables (counts vs intensities), filtering cells with fewer than 20 transcripts (14,261 of 16,045 kept), `normalise_rna()` (normalize_total + log1p) and `normalise_protein()` (arcsinh(x/5) + scale);
       2. `cluster()`: PCA 30, 15 neighbours, UMAP and Leiden 0.5 (igraph), giving 9 clusters in about 30 s. Exercise 1 tries resolutions 0.2 and 1.0 (6 and 12 clusters);
       3. `MARKERS` (9 cell types, 4 panel genes each), a dot plot, and `name_clusters()` (`sc.tl.score_genes`, highest mean score per cluster). Exercise 2 checks the names against the top 5 genes from `rank_genes_groups`;
       4. a map of the crop, coloured by cell type;
       5. protein means per RNA cell type (matrixplot); CD8A RNA vs protein per cell (Spearman 0.54); protein-only clusters (15) against the RNA types (ARI 0.34);
       6. the reference Day 1 phenotypes, joined by ID, as a crosstab;
       7. exercise 3 on the participant's own cells and Day 1 phenotypes, with fallbacks;
       8. 10x cell types saved to `../data/session7_cell_types.csv` (cell_id, leiden, cell_type) for session 8.
     - **Panel caveat:** the panel lacks the classic ccRCC markers (CA9, NDUFA4L2, PAX8, PAX2). The tumour list uses MET, CDH2, KRT8 and CAV1, which are data-driven (the top genes of the tumour cluster); the notebook says so. Also absent: COL1A1/COL3A1/DCN/LUM, LYZ, C1QA/B, JCHAIN, TPSAB1, CXCL13, SPP1, APOE.
     - RNA clusters at resolution 0.5, all named correctly by `name_clusters()`: B cell 1,157; T cell 2,705; Macrophage 2,819; Tumour 1,427; Fibroblast 1,925; Smooth muscle 1,595; Lymphatic endothelium 710; Plasma cell 166; Blood endothelium 1,757.
     - Against the stand-in reference: B cells 81% B; blood endothelium 78% Endothelial; T cells 61% CD8+ and 18% CD4+; macrophages 64%; tumour 85% Other (no tumour marker in the Day 1 classifier). **Plasma cells are 87% "Other T cell"**: they are CD3E-bright in the protein data (cross-reactivity or spill-over); the notebook asks about it.
     - Exercise 3 on the saved session 6 cells: 1,226 of 1,315 matched a reference cell by position; 6 cell types (no B, plasma or lymphatic cells in this tumour region).
     - scanpy turns string `obs` columns into categoricals behind the scenes, so `cell_type_map()` converts to `object` before `fillna`.
     - **Next:** replace the stand-in reference with the instructors' QuPath export; time a run on a laptop-class machine; settle the Day 1 session 4 export (see Decisions).
   - **08 drafted; the solution runs end to end (2026-11-17).** Files: `notebooks/08_spatial_and_next_steps.ipynb` and `solutions/08_spatial_and_next_steps.ipynb` (34 cells; 3 exercise cells). On the 32 GB Xeon desktop it took 41 s, peak 0.7 GB. All figures were checked.
     - **Inputs:** the workshop Zarr (10x's cells: `protein` table, `obsm["spatial"]` already in crop-local µm, `cell_boundaries`, `pathology_annotations`) and `../data/session7_cell_types.csv`. If the CSV is missing, it falls back to the reference phenotypes (`qupath/xenium_rcc_crop_10x_phenotypes.geojson`, classes joined by 10x ID) and says so. The fallback path hasn't been run.
     - Sections:
       1. Neighbours: `sq.gr.spatial_neighbors_delaunay` (squidpy 1.8.4; the older `spatial_neighbors(..., delaunay=True)` is deprecated and goes in 1.9), the edge-length histogram, then `remove_long_edges()` by hand at `MAX_EDGE_UM = 30` (the text mentions `radius=` as the built-in alternative). Linked to QuPath's Delaunay clustering. Exercise 1 counts the long edges and maps them.
       2. `sq.gr.nhood_enrichment` (200 permutations, `rng=0`, about 2 s; squidpy 1.8.4 takes `rng`, not `seed`) as an annotated z-score heatmap; `sq.gr.co_occurrence` (10–200 µm, about 1 s) with a `plot_co_occurrence()` helper. Exercise 2 plots two more cell types.
       3. Niches: the composition of each cell's 50 µm neighbourhood (`NearestNeighbors.radius_neighbors`), k-means with 6 niches, a profile heatmap, side-by-side maps, then a comparison with the pathology annotations (each cell's centre by `sjoin`; crosstab + ARI). Exercise 3 varies the radius and the number of niches.
       4. CellSurvey's communities: the same method as upstream `network_analysis.py` (Delaunay ≤ 50 µm, edge weight 1 + correlation of arcsinh(x/5) protein profiles, `nx.community.louvain_communities`, seed 42), at resolutions 0.1 and 0.01.
       5. Back to QuPath: `../data/session8_cells.geojson`, with 10x's outlines in pixels as detections, classification = cell type (with colour), `measurements` = Niche and Community (resolution 0.1) for QuPath's measurement maps. 14,261 cells, about 5 s. Not yet imported into QuPath.
       6. Evaluating new tools: a 7-question checklist and a table of tools by step, drawn from upstream CellSurvey's survey (InstanSeg, Cellpose, segger, Baysor, Proseg, Sopa, SegTraQ, CELESTA, Novae, SACCELERATOR, PANORAMIC, VALIS, LazySlide, napari-spatialdata, CellSurvey). A discussion, not a coding exercise.
     - **Results (session 7's 9 RNA cell types, 14,261 cells):**
       - Delaunay: 42,754 edges, median 11.6 µm, longest 1,021 µm (across vessels and gaps). Over 20 / 30 / 50 / 100 µm: 14.5% / 3.2% / 0.8% / 0.3%. After the 30 µm cut: 41,366 edges, median 6 neighbours, no isolated cells.
       - Enrichment z-scores: the diagonal is strongly positive (B cell 141, Tumour 71, Lymphatic endothelium 49); blood endothelium–smooth muscle +34 (vessels); fibroblast–lymphatic endothelium +15; T cell–Tumour −11; T cell–Macrophage +3.
       - Co-occurrence near tumour: tumour 6.8× chance at 10–20 µm, falling to 2.6× at 200 µm; macrophages and smooth muscle above 1; B cells about 0.02 and plasma cells about 0.1.
       - Niches (50 µm, k = 6) map onto the tissue: B-cell follicles, T-cell zones and a fibroblast/lymphatic stroma niche in and around Immune infiltration; tumour-rich and vascular (smooth muscle + endothelium + macrophage + tumour) niches in Tumor. ARI against the annotations 0.30. Exercise 3: 25 µm 0.19, 100 µm 0.53, k = 4 0.51, k = 10 0.24.
       - Louvain: resolution 0.1 gives 8 communities (largest 2,653) with ARI 0.27, and cuts the fairly uniform tumour into large left/right patches, a boundary the cell types don't show (the notebook asks about it). Resolution 0.01 gives 3 communities (8,594, 5,665 and 2 cells) with ARI 0.63, matching the annotations best of all. The 2-cell communities are isolated cells.
     - The notebook was drafted from a percent-format script in the session scratchpad; the solution notebook is the source from now on.
   - Exercise/solution sync: the solution notebook is the source. Edit both versions the same way, and run `Scripts/check_exercises.py` afterwards. (Notebooks 07 and 08 were generated from builder scripts in the session scratchpad; treat the solution notebooks as their source from now on.)
   - Structure, before the 2026-11-16 restructure (see above for the current one): (1) choose a 440 µm region (`REGION = [530, 530, 970, 970]` µm, about 1,200 cells) with `bounding_box_query` in `microns`, copied into a new in-memory `SpatialData`; (2) 10x's segmentation (`segmentation_method`, a 100 µm zoom with DAPI and the boundary stain); (3) InstanSeg via Sopa with DAPI only, then DAPI + `ATP1A1/CD45/E-Cadherin` (exercise 1), plus `target="nuclei"`; (4) `sopa.aggregate` with `key_added="instanseg_table"` and both filters at 0, then `sopa.spatial.assign_transcript_to_cell`; (5) SegTraQ baseline and region similarity for 10x vs InstanSeg; (6) exercise 2: grow the outlines with `sopa.shapes.expand_radius(..., 0.5, no_overlap=True)` and remeasure.
   - **Region or whole crop (decided 2026-11-15):** the setup cell has `WHOLE_CROP = False`. When it's `True`, section 1 sets `REGION` to the whole crop (from the image size), and the *whole* session runs on it unchanged: segmentation, aggregation, SegTraQ and the exercises. This replaced a separate section 7 that only segmented the whole crop and compared cell counts. A whole-crop run means 3 InstanSeg runs of about 6 min each on the desktop, plus SegTraQ on about 16,000 cells (region similarity took about 20 s for 1,200 cells), so expect 30 min or more on a laptop. Not yet timed; memory at that scale is also untested.
   - Exercise/solution check: comparing the two notebooks cell by cell, they should differ only in the two exercise cells (`# Your code here`). Check this after every edit.
   - Measured on the maintainer's desktop (Xeon E5-2630 v4, 10 cores, 32 GB RAM, CPU only):
     - InstanSeg: a 1024 px tile takes 12–15 s; the 2048 px region about 45 s; the **whole crop with DAPI only takes 370 s** and finds 14,610 cells (10x has 16,045). Too slow and risky to run live on 30 mixed laptops, hence the 440 µm region by default and `WHOLE_CROP` as an opt-in. The whole crop with DAPI + boundary stain hasn't been timed.
     - Central 1024 px tile: DAPI only gives 284 cells (median 39 µm²); DAPI + boundary stain gives 315 cells (median 48 µm²).
     - 2048 px central region: 10x has 1,212 cells, 19% of transcripts unassigned, median 72 transcripts per cell, median area 69 µm², nucleus–cell IoU 0.42, border admixture 0.10. InstanSeg (DAPI + boundary) has 1,252 cells, 47% unassigned, median 48 transcripts per cell, median area 47 µm², IoU 0.62, border admixture 0.095. SegTraQ baseline takes about 1 s and region similarity about 20 s on this region.
     - Expanding the outlines (exercise 2) on the region: see the 2026-11-16 run above.
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
   - **Session 4 must end with exporting the classified cells** as `data/day1_cells.geojson` (see the session 7 decision). The instructors also make the reference phenotype file for 10x's cells.
   - **Adapt the IF exercise's markers to RCC.** PanCK is sparse and patchy in the workshop crop (common in RCC), so it won't separate tumour from stroma the way it did in the lung image. Choose more suitable markers instead (candidates to check in QuPath: E-Cadherin, Beta-catenin, Vimentin, CD31, alphaSMA).

## Remaining work
Compiled 2026-11-17, when the first full draft of Day 2 was finished. Detail for each item is under Order of work and Decisions made. (A short copy in `README.md` was removed on 2026-11-18, because the README is now the public website's home page; this list is the only one.)

**Data and release** (maintainer, on the HPC)
1. Rerun the preparation notebook on the HPC, so the bundle includes `<NAME>_fovs.geojson`. (The README it writes into the bundle mentions the file since 2026-11-17.)
2. Upload the bundle to Zenodo, including the instructors' reference phenotypes once they exist (item 9).
3. Add the Zenodo link to `README.md` and `Pages/Installation-Instructions.md`, saying the data goes in the workshop folder's `data/` (with `qupath/` inside it).

**Day 2 notebooks**
4. The maintainer reads through all four notebooks (in progress from 2026-11-17).
5. Session 5: check the CD3E and CD68 thresholds by eye at full resolution, and fix the small leftovers (the slider starts at Otsu's value; saving the GeoJSON prints a geopandas "'crs' was not provided" warning).
6. Import the saved GeoJSON files into QuPath to confirm they load: `session5_cells.geojson`, and `session8_cells.geojson` with its Niche/Community measurement maps.
7. Time all four notebooks on a laptop-class machine (8–16 GB) with memory free, plus session 6's `WHOLE_CROP` mode, which has never been timed.
8. Run session 8's fallback path (no `session7_cell_types.csv`), and session 7's fallbacks, at least once.
9. Decide whether the solution notebooks ship with outputs (see Open questions).

**Day 1** (maintainer and instructors)
10. Make the real reference phenotypes in QuPath (10x's cells, classified and exported with each cell's 10x ID as its name), replacing the stand-in from `make_reference_phenotypes.py`.
11. Port Sara's exercises to the RCC data, using markers other than PanCK, and write the `Pages/Day1/` guides.
12. Make sure Day 1 session 4 ends by exporting the classified cells as `data/day1_cells.geojson` (FeatureCollection, with classifications, covering the session 6 region).
13. Copy only classifiers and class lists from `qupath_content/` into `qupath/`.

**Installation and environment**
14. Run `pixi run check-full` on an Apple Silicon Mac and on Linux (Bio-Formats is untested on both, and everything is untested on macOS).
15. Add the organisers' contact details to the installation page.
16. At least a month before the workshop, follow "Updating package versions", including lifting the `spatialdata <0.9` pin.

**Workshop page and logistics**
17. Fill in `README.md`: instructors, venue, slides, registration and FAQ.
18. Write the slides (Google Drive), including the spatial-biology primer for Day 1 session 1.
19. Find out where the original liver `.vsi` and lung TIFF images came from, and whether they may be shared (the maintainer is enquiring). This only matters if any of them stay in Day 1.

**Housekeeping**
20. Bring the shared plan doc up to date with this file, or retire it and point to this file instead.
21. Replace the two CellSurvey figures in `assets/` with figures from the workshop data.
22. Optionally, add `Pages/Data.md` describing the bundle's contents (and add it to `defaults:` in `_config.yml`).

**Website (GitHub Pages)**
23. **Mostly done (2026-11-18): the site is live** at https://franciscrickinstitute.github.io/spatial-bio-training/ (remote theme built fine). Checked by fetching the pages:
    - navigation (Home, Installation, Day 2 notebooks, Solutions) and the "View on GitHub" link;
    - search;
    - the notebook links (GitHub blob URLs) and the README → Installation link (converted to `/spatial-bio-training/Pages/Installation-Instructions.html`);
    - the installation page's anchors, which match its heading IDs, including `#certificate-errors-unknownissuer-certificate_verify_failed`;
    - `AGENTS.html` and `notebooks/*.ipynb` return 404, as intended.

    Still to do: check the look in a browser (the fetch tool can't show whether the tables and the "Note:" blockquote render), and add the address to the repo's About box.

## Open questions
- Does QuPath ignore OME `Plane PositionX/PositionY`? Believed so; it doesn't matter under option A.
- Source and sharing terms of the original liver `.vsi` and `LungImg1.ome.tif` course images (the maintainer is enquiring).
- Should the solution notebooks be committed **with outputs**, so participants can read results without running anything? So far both versions are committed without outputs. Outputs would add images to git, and they would need regenerating whenever a notebook or the data changes.
