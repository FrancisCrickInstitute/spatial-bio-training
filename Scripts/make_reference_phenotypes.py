"""Write a STAND-IN for the Day 1 reference phenotypes: 10x's cells, classified as in QuPath, as QuPath GeoJSON.

Maintainer-only, and temporary. Notebook 07 compares its cell types with "Day 1 phenotypes" of the same 10x cells,
read from `qupath/xenium_rcc_crop_10x_phenotypes.geojson`. The real file should be made by the instructors in
QuPath: import `xenium_rcc_crop_10x_cells.geojson` into the IF image, add intensity features, classify the cells with
single-measurement classifiers combined into a composite classifier, and export them as GeoJSON (File > Export objects
as GeoJSON, "Export as FeatureCollection"). Until then, this script writes a file of the same shape, so the notebook
can be developed and tested.

It applies the same kind of classifier to 10x's protein table: one threshold per marker (chosen with Otsu's method on
arcsinh(x / 5) of the per-cell mean intensities, rounded), combined in order, first match wins. The outlines are 10x's
cell boundaries in image pixels, and each object's `name` is its 10x cell ID, as in the Day 1 import file, so the
notebook can join on it.

Usage, from the repository folder:

    pixi run python Scripts/make_reference_phenotypes.py [data/xenium_rcc_crop.zarr] [data/qupath]
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import spatialdata as sd
from shapely.geometry import mapping

THRESHOLDS = {"CD3E": 8, "CD8A": 7, "CD4": 3, "CD20": 8, "CD68": 6, "CD163": 3.5, "CD31": 5, "alphaSMA": 3.5}

# (class, colour, rule) in order: the first rule a cell meets gives its class
RULES = [
    ("CD8+ T cell", [255, 255, 0], lambda p: p["CD3E"] & p["CD8A"]),
    ("CD4+ T cell", [0, 255, 0], lambda p: p["CD3E"] & p["CD4"]),
    ("Other T cell", [0, 160, 0], lambda p: p["CD3E"]),
    ("B cell", [0, 128, 255], lambda p: p["CD20"]),
    ("Macrophage", [255, 0, 255], lambda p: p["CD68"] | p["CD163"]),
    ("Endothelial", [255, 0, 0], lambda p: p["CD31"]),
    ("Smooth muscle", [255, 128, 0], lambda p: p["alphaSMA"]),
]
OTHER = ("Other", [128, 128, 128])


def main():
    zarr = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/xenium_rcc_crop.zarr")
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/qupath")
    sdata = sd.read_zarr(zarr)
    pixel_size = sdata.attrs["pixel_size_um"]

    protein = sdata["protein"]
    values = pd.DataFrame(protein.X.toarray() if hasattr(protein.X, "toarray") else protein.X,
                          columns=protein.var_names, index=protein.obs["cell_id"].astype(str).values)
    positive = pd.DataFrame({marker: values[marker] > threshold for marker, threshold in THRESHOLDS.items()})

    classes = pd.Series(OTHER[0], index=values.index)
    colours = {OTHER[0]: OTHER[1]}
    for name, colour, rule in reversed(RULES):  # earlier rules overwrite later ones, so they win
        classes[rule(positive)] = name
        colours[name] = colour

    cells = sdata["cell_boundaries"]  # stored in µm
    in_pixels = cells.geometry.scale(1 / pixel_size, 1 / pixel_size, origin=(0, 0))
    features = [{"type": "Feature", "geometry": mapping(geometry),
                 "properties": {"objectType": "detection", "name": str(cell_id),
                                "classification": {"name": classes[str(cell_id)],
                                                   "color": colours[classes[str(cell_id)]]}}}
                for cell_id, geometry in zip(cells.index, in_pixels)]

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "xenium_rcc_crop_10x_phenotypes.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    print(f"{len(features):,} cells written to {path} (stand-in for the instructors' QuPath export)")
    print(classes.value_counts().to_string())


if __name__ == "__main__":
    main()
