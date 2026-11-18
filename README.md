[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/) [![Built with Pixi](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json)](https://pixi.sh) ![GitHub](https://img.shields.io/github/license/FrancisCrickInstitute/spatial-bio-training?color=green&style=plastic)

> **Note:** this workshop is under development. Registration and materials will be added here as they are finalised.

**Dates:** 25–26 February 2027 · **Places:** 20–30 · **Bring your own laptop** (see [Preparation](#preparation))

# Overview

A two-day, hands-on workshop on analysing spatial biology data. **Day 1** uses [QuPath](https://qupath.github.io/) to explore, segment and classify cells interactively. **Day 2** rebuilds the same analysis in **Python**, then goes further with transcripts, segmentation quality control and spatial statistics.

Both days use the same public tissue section, which has multiplex immunofluorescence (protein), H&E and in situ transcript data.

By the end of the workshop you should be able to:

1. Explain how multiplex IF, H&E and in situ transcript data relate on one section, and what each can and can't tell you.
2. Segment nuclei and cells, and measure per-cell marker intensities and transcript counts.
3. Classify cells by marker thresholds (QuPath) and by unsupervised clustering (Python).
4. Describe spatial organisation: neighbourhoods, cell–cell co-location, tissue niches.
5. Move results between QuPath and Python, and judge which tool suits which question.

The workshop will not analyse your own data. Its aim is to give you enough grounding to choose the right tools for your data, and to ask the right questions when evaluating new ones.

# Registration

Registration is by application and is not yet open. The application form asks about your research and what you hope to get from the workshop.

# Instructors

TBC

# Preparation

You will work on your own laptop throughout: Windows, macOS on Apple Silicon (M1 or later) or Linux. You do not need a GPU. Before the workshop:

1. Install QuPath and the Python environment, following the [installation instructions](Pages/Installation-Instructions.md). The Python environment works on Windows, Linux and macOS (Apple Silicon).
2. From the repository folder, check the Python environment with `pixi run check-full`. This also downloads the cell segmentation model, so run it with an internet connection and preferably off any VPN.
3. Download the workshop data (link to follow).

# Program

## Day 1: spatial biology in QuPath

| Session | Topic |
|---|---|
| 1 | Digital images and an introduction to spatial biology |
| 2 | H&E workflow: tissue detection, region classification, cell detection |
| 3 | Multiplex IF workflow: cell segmentation with InstanSeg, cell classification, phenotypes |
| 4 | Spatial analysis in QuPath, and exporting results for Day 2 |

## Day 2: spatial omics in Python

| Session | Topic | Notebook |
|---|---|---|
| 5 | From QuPath to Python: Jupyter notebooks, opening the Day 1 images, classic segmentation and simple classifiers | [05](https://github.com/FrancisCrickInstitute/spatial-bio-training/blob/main/notebooks/05_from_qupath_to_python.ipynb) |
| 6 | The SpatialData data model, transcripts, deep-learning cell segmentation and quality control | [06](https://github.com/FrancisCrickInstitute/spatial-bio-training/blob/main/notebooks/06_segmentation_and_qc.ipynb) |
| 7 | Cell types: clustering and comparison with Day 1 | [07](https://github.com/FrancisCrickInstitute/spatial-bio-training/blob/main/notebooks/07_cell_types.ipynb) |
| 8 | Spatial statistics and niches, and where to go next | [08](https://github.com/FrancisCrickInstitute/spatial-bio-training/blob/main/notebooks/08_spatial_and_next_steps.ipynb) |

Completed versions of the notebooks are in [`solutions/`](https://github.com/FrancisCrickInstitute/spatial-bio-training/tree/main/solutions). You'll run the notebooks on your own laptop during the workshop, from the workshop folder you download in [Preparation](#preparation).

# Venue

TBC

# Slides

TBC

# Additional material

- [CellSurvey](https://github.com/FrancisCrickInstitute/CellSurvey): a pipeline that runs the Day 2 analysis end to end, built on [Sopa](https://prism-oncology.github.io/sopa).
- [Introduction to image analysis](https://github.com/FrancisCrickInstitute/introduction-to-image-analysis): our general image-analysis workshop.

# FAQ

TBC

