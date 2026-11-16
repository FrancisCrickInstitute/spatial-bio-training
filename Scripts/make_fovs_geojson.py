"""Write the fields-of-view (FOV) GeoJSON for a crop, without rerunning the whole preparation notebook.

Maintainer-only. It reproduces the `fov_boxes()` step of notebooks/extra/prepare_xenium_dataset.ipynb (section 6)
and its `<NAME>_fovs.geojson` export (section 10): the FOV boxes from 10x's morphology_fov_locations.json (extracted,
or read straight from aux_outputs.tar.gz), made crop-local, clipped to the crop and converted to pixels, as QuPath
annotations classed "Field of view". If you change one, change the other.

Usage:

    pixi run python Scripts/make_fovs_geojson.py OUTS_DIR OUTPUT.geojson [x_min,y_min,x_max,y_max]

OUTS_DIR is the unzipped Xenium `outs` folder. The crop is in µm on the full slide; it defaults to the workshop
crop (1487.5,0,2987.5,1500).
"""

import json
import sys
import tarfile
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box, mapping


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    outs, output = Path(sys.argv[1]), Path(sys.argv[2])
    crop = tuple(float(v) for v in sys.argv[3].split(",")) if len(sys.argv) > 3 else (1487.5, 0.0, 2987.5, 1500.0)

    # The region snapped to whole pixels, as in the preparation notebook
    pixel_size = json.loads((outs / "experiment.xenium").read_text())["pixel_size"]
    c0, r0 = (max(0, round(v / pixel_size)) for v in crop[:2])
    c1, r1 = round(crop[2] / pixel_size), round(crop[3] / pixel_size)
    x0, y0, x1, y1 = c0 * pixel_size, r0 * pixel_size, c1 * pixel_size, r1 * pixel_size

    json_path, tar_path = outs / "aux_outputs" / "morphology_fov_locations.json", outs / "aux_outputs.tar.gz"
    locations = None
    if json_path.exists():
        locations = json.loads(json_path.read_text())
    elif tar_path.exists():
        with tarfile.open(tar_path) as archive:
            for member in archive:  # stop at the file rather than unpacking everything
                if member.name.endswith("morphology_fov_locations.json"):
                    locations = json.load(archive.extractfile(member))
                    break
    if locations is None:
        sys.exit(f"No morphology_fov_locations.json in {outs}")
    assert locations.get("units", "micron") == "micron", locations.get("units")

    region = box(0, 0, x1 - x0, y1 - y0)
    boxes = {name: box(f["x"] - x0, f["y"] - y0, f["x"] + f["width"] - x0, f["y"] + f["height"] - y0)
             for name, f in locations["fov_locations"].items()}
    clipped = {name: geometry.intersection(region) for name, geometry in boxes.items()}
    clipped = {name: geometry for name, geometry in clipped.items() if geometry.area > 0}
    fovs = gpd.GeoDataFrame({"name": list(clipped)}, geometry=list(clipped.values()))
    in_pixels = fovs.geometry.scale(1 / pixel_size, 1 / pixel_size, origin=(0, 0))

    features = [{"type": "Feature", "geometry": mapping(geometry),
                 "properties": {"objectType": "annotation", "name": str(name),
                                "classification": {"name": "Field of view", "color": [0, 200, 200]}}}
                for geometry, name in zip(in_pixels, fovs["name"])]
    output.write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    print(f"{len(fovs)} FOVs ({', '.join(fovs['name'])}) written to {output}")


if __name__ == "__main__":
    main()
