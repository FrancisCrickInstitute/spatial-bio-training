"""Download the 10x Xenium Protein RCC dataset and check how well our tools read it.

This is a one-off maintainer script, meant for the HPC, not for participants. It answers
the open questions in AGENTS.md before `prepare_data.py` is written:

1. Does `spatialdata_io.xenium` read all the per-channel protein images in XOA 4.0's
   `morphology_focus/` folder, with the right channel names?
2. What do the raw protein values look like (XOA 4.0 adds a +100 offset)?
3. What do the cell table, transcripts and boundaries look like once read?

Usage (from the repository root):

    pixi run python Scripts/inspect_xenium.py --data-dir /path/with/80GB/free
    pixi run python Scripts/inspect_xenium.py --data-dir ... --with-he    # also fetch and read the 3.7 GB H&E

Downloads resume if interrupted, and steps that are already done are skipped. A JSON
report is written next to the data (`inspection_report.json`).

Data: 10x Genomics, "Xenium In Situ Gene and Protein Expression data for FFPE Human Renal
Cell Carcinoma", CC BY 4.0.
https://www.10xgenomics.com/datasets/xenium-protein-ffpe-human-renal-carcinoma
"""

import argparse
import json
import shutil
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import requests

BASE_URL = (
    "https://cf.10xgenomics.com/samples/xenium/4.0.0/Xenium_V1_Human_Kidney_FFPE_Protein_updated/"
    "Xenium_V1_Human_Kidney_FFPE_Protein_updated_"
)
OUTS = "outs.zip"  # 36.1 GB: everything Day 2 needs
SMALL_FILES = ["he_imagealignment.csv", "annotation.geojson"]
HE_IMAGE = "he_image.ome.tif"  # 3.7 GB, only with --with-he
HEADERS = {"User-Agent": "spatial-bio-training/0.1 (workshop data preparation)"}
CHUNK = 8 * 1024 * 1024
GB = 1024**3

report: dict = {}


def section(title):
    print(f"\n=== {title} " + "=" * max(0, 70 - len(title)))


# --------------------------------------------------------------------------- download


def remote_size(url):
    response = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=60)
    response.raise_for_status()
    if "Content-Length" in response.headers:
        return int(response.headers["Content-Length"])
    # Fall back to a one-byte range request: "Content-Range: bytes 0-0/<total>"
    response = requests.get(url, headers={**HEADERS, "Range": "bytes=0-0"}, timeout=60)
    response.raise_for_status()
    return int(response.headers["Content-Range"].rsplit("/", 1)[1])


def download(url, dest, attempts=10):
    """Download url to dest, resuming a partial file.

    Always sends an explicit `bytes=start-end` range: the 10x CDN ignored a suffix
    range (`bytes=-N`) and started sending the whole file.
    """
    total = remote_size(url)
    for attempt in range(1, attempts + 1):
        have = dest.stat().st_size if dest.exists() else 0
        if have == total:
            print(f"  {dest.name}: complete ({total / GB:.2f} GB)")
            return
        if have > total:
            dest.unlink()
            have = 0
        print(f"  {dest.name}: {have / GB:.2f} of {total / GB:.2f} GB, downloading (attempt {attempt})")
        headers = {**HEADERS, "Range": f"bytes={have}-{total - 1}"}
        try:
            with requests.get(url, headers=headers, stream=True, timeout=120) as response:
                response.raise_for_status()
                if have and response.status_code != 206:
                    print("  Server ignored the range request; starting again from zero.")
                    have = 0
                mode = "ab" if have else "wb"
                next_report = have + GB
                with open(dest, mode) as handle:
                    for chunk in response.iter_content(CHUNK):
                        handle.write(chunk)
                        have += len(chunk)
                        if have >= next_report:
                            print(f"    {have / GB:6.1f} / {total / GB:.1f} GB", flush=True)
                            next_report += GB
        except (requests.ConnectionError, requests.Timeout, requests.exceptions.ChunkedEncodingError) as error:
            print(f"  Interrupted ({type(error).__name__}); retrying in 10 s.")
            time.sleep(10)
    raise RuntimeError(f"Could not download {url} after {attempts} attempts")


def fetch(data_dir, with_he):
    section("Download")
    needed = (36.1 + 40 + (3.7 if with_he else 0)) * GB  # zip + extracted copy (+ H&E)
    free = shutil.disk_usage(data_dir).free
    print(f"  Free space in {data_dir}: {free / GB:.0f} GB (roughly {needed / GB:.0f} GB needed for a fresh run)")
    names = [OUTS, *SMALL_FILES] + ([HE_IMAGE] if with_he else [])
    for name in names:
        download(BASE_URL + name, data_dir / name)


def extract(data_dir, delete_zip):
    section("Extract")
    target = data_dir / "outs"
    done = target / ".extracted"
    if done.exists():
        print(f"  Already extracted to {target}")
    else:
        zip_path = data_dir / OUTS
        print(f"  Extracting {zip_path.name} to {target} (this takes a while)...")
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(target)
        done.touch()
        if delete_zip:
            zip_path.unlink()
            print(f"  Deleted {zip_path.name}")
    # The archive may or may not have a top-level folder: find the folder holding experiment.xenium
    matches = sorted(target.rglob("experiment.xenium"), key=lambda p: len(p.parts))
    if not matches:
        raise FileNotFoundError(f"No experiment.xenium found under {target}")
    outs = matches[0].parent
    print(f"  Xenium output folder: {outs}")
    return outs


# --------------------------------------------------------------------------- inspection


def inspect_experiment(outs):
    section("experiment.xenium")
    experiment = json.loads((outs / "experiment.xenium").read_text())
    for key, value in experiment.items():
        if not isinstance(value, (dict, list)):
            print(f"  {key}: {value}")
    report["experiment"] = {k: v for k, v in experiment.items() if not isinstance(v, (dict, list))}
    for panel_file in ["gene_panel.json", "protein_panel.json"]:
        path = outs / panel_file
        if path.exists():
            # The layout isn't documented, so describe it rather than assume where the targets are.
            panel = json.loads(path.read_text())
            print(f"  {panel_file} structure:")
            report[panel_file] = describe_json(panel)


def describe_json(value, prefix="    ", depth=0, max_depth=3):
    """Print the keys of a JSON object (and lengths of its lists) a few levels deep."""
    summary = {}
    if isinstance(value, dict) and depth < max_depth:
        for key, child in value.items():
            if isinstance(child, list):
                print(f"{prefix}{key}: list of {len(child)}")
                summary[key] = f"list of {len(child)}"
                if child and isinstance(child[0], dict):
                    print(f"{prefix}  first item keys: {list(child[0])}")
            elif isinstance(child, dict):
                print(f"{prefix}{key}:")
                summary[key] = describe_json(child, prefix + "  ", depth + 1, max_depth)
            else:
                print(f"{prefix}{key}: {child}")
                summary[key] = child
    return summary


def inspect_focus_files(outs):
    """Read each morphology_focus file directly with tifffile, as a baseline to compare against."""
    import tifffile

    section("morphology_focus/ files (read directly with tifffile)")
    files = sorted((outs / "morphology_focus").glob("*.ome.tif"))
    print(f"  {len(files)} files. Values below are from each file's smallest pyramid level.")
    print(f"  {'file':<40} {'level 0 shape':<16} {'dtype':<7} {'min':>6} {'p50':>7} {'p99':>7} {'max':>7}")
    rows = []
    for path in files:
        # is_ome=False: otherwise tifffile follows the OME-XML and opens the combined
        # 35-file image from every file, instead of this file's own channel.
        with tifffile.TiffFile(path, is_ome=False) as tif:
            series = tif.series[0]
            level0 = series.levels[0]
            smallest = series.levels[-1]
            if np.prod(smallest.shape) <= 50_000_000:
                coarse = smallest.asarray()
            else:  # no usable pyramid: sample a central 4096 x 4096 window instead
                import zarr

                store = zarr.open(smallest.aszarr(), mode="r")
                cy, cx = (s // 2 for s in smallest.shape[-2:])
                coarse = np.asarray(store[..., cy - 2048:cy + 2048, cx - 2048:cx + 2048])
        stats = np.percentile(coarse, [0, 50, 99, 100])
        shape = "x".join(str(s) for s in level0.shape)
        print(f"  {path.name:<40} {shape:<16} {str(level0.dtype):<7} "
              f"{stats[0]:>6.0f} {stats[1]:>7.0f} {stats[2]:>7.0f} {stats[3]:>7.0f}")
        rows.append({"file": path.name, "shape": list(level0.shape), "dtype": str(level0.dtype),
                     "levels": len(series.levels), "min": float(stats[0]), "p50": float(stats[1]),
                     "p99": float(stats[2]), "max": float(stats[3])})
    print("  If protein channels have a minimum of about 100, that is XOA 4.0's +100 offset:")
    print("  subtract it before measuring intensities.")
    report["morphology_focus_files"] = rows
    return files


def inspect_spatialdata(outs, n_focus_files):
    import spatialdata_io

    section("spatialdata_io.xenium (test 1)")
    print("  Reading with gex_only=False, so protein features stay in the table. Labels and")
    print("  aligned images are skipped here: they aren't what's being tested.")
    start = time.time()
    sdata = spatialdata_io.xenium(
        outs,
        gex_only=False,
        cells_labels=False,
        nucleus_labels=False,
        aligned_images=False,
    )
    print(f"  Read in {time.time() - start:.0f} s")
    print(sdata)

    result = {}
    for name, image in sdata.images.items():
        node = image["scale0"].image if hasattr(image, "children") else image  # DataTree (multiscale) or DataArray
        channels = [str(c) for c in node.coords["c"].values] if "c" in node.coords else []
        print(f"  image {name}: dims {dict(node.sizes)}, {len(channels)} channels")
        print(f"    channels: {', '.join(channels)}")
        result[name] = {"sizes": {k: int(v) for k, v in node.sizes.items()}, "channels": channels}

    focus = result.get("morphology_focus", {})
    passed = len(focus.get("channels", [])) == n_focus_files
    print(f"\n  TEST 1 {'PASSED' if passed else 'FAILED'}: morphology_focus has "
          f"{len(focus.get('channels', []))} channels for {n_focus_files} files.")
    report["test1_morphology_focus_all_channels"] = passed
    report["images"] = result

    for name, shapes in sdata.shapes.items():
        print(f"  shapes {name}: {len(shapes)} rows, geometry {shapes.geometry.geom_type.iloc[0]}")
        report.setdefault("shapes", {})[name] = len(shapes)
    import pyarrow.parquet as pq

    parquet = pq.ParquetFile(outs / "transcripts.parquet")
    parquet_rows = parquet.metadata.num_rows
    print(f"  transcripts.parquet: {parquet_rows:,} rows in {parquet.metadata.num_row_groups} row groups")
    report["transcripts_parquet_rows"] = parquet_rows
    for name, points in sdata.points.items():
        print(f"  points {name}: columns {list(points.columns)}, {points.npartitions} partitions")
        # The SpatialData printout showed 11x the parquet row count: count exactly.
        start = time.time()
        n_points = int(points.map_partitions(len).compute().sum())
        same = n_points == parquet_rows
        print(f"    exact row count: {n_points:,} ({time.time() - start:.0f} s) "
              f"{'= parquet rows' if same else f'!= parquet rows ({n_points / parquet_rows:.2f}x)'}")
        report.setdefault("points", {})[name] = {"columns": list(points.columns),
                                                 "npartitions": int(points.npartitions),
                                                 "rows": n_points, "matches_parquet": same}

    for name, table in sdata.tables.items():
        types = table.var["feature_types"].value_counts().to_dict() if "feature_types" in table.var else {}
        print(f"  table {name}: {table.n_obs:,} cells x {table.n_vars} features {types}")
        report.setdefault("tables", {})[name] = {"n_obs": int(table.n_obs), "feature_types": types}
        if "feature_types" not in table.var:
            continue
        # Select by position, not name: protein and gene names can be the same (e.g. CD4),
        # so var_names aren't unique and name-based indexing fails.
        is_protein = (table.var["feature_types"] == "Protein Expression").to_numpy()
        is_gene = (table.var["feature_types"] == "Gene Expression").to_numpy()
        protein = list(table.var_names[is_protein])
        clashes = sorted(set(protein) & set(table.var_names[is_gene]))
        duplicated = sorted(set(table.var_names[table.var_names.duplicated()]))
        print(f"    duplicated var names: {len(duplicated)} {duplicated}")
        print(f"    protein names that are also gene names: {clashes}")
        if protein:
            x = table.X[:, is_protein]
            x = x.toarray() if hasattr(x, "toarray") else np.asarray(x)
            print(f"    protein values: min {x.min():.2f}, median {np.median(x):.2f}, max {x.max():.2f}")
            print(f"    protein features: {', '.join(protein)}")
        report["tables"][name].update({"duplicated_var_names": duplicated, "protein_gene_clashes": clashes,
                                       "protein_features": protein})

    print("  Coordinate systems:", ", ".join(sdata.coordinate_systems))
    report["coordinate_systems"] = list(sdata.coordinate_systems)
    return passed


def inspect_he(data_dir, outs):
    from spatialdata_io import xenium_aligned_image

    section("H&E alignment")
    image = xenium_aligned_image(data_dir / HE_IMAGE, data_dir / "he_imagealignment.csv")
    node = image["scale0"].image if hasattr(image, "children") else image
    print(f"  H&E: dims {dict(node.sizes)}")
    report["he"] = {k: int(v) for k, v in node.sizes.items()}


def inspect_annotations(data_dir):
    section("annotation.geojson (10x pathology annotations)")
    data = json.loads((data_dir / "annotation.geojson").read_text())
    features = data["features"] if isinstance(data, dict) else data
    classes = {}
    for feature in features:
        # 10x's file is inconsistent: some annotations have only a `name`, and one has a
        # classification that differs from its name. Report both.
        props = feature.get("properties", {})
        cls = props.get("classification")
        cls_name = cls.get("name") if isinstance(cls, dict) else None
        label = props.get("name", "unnamed") + (f" (class: {cls_name})" if cls_name != props.get("name") else "")
        classes[label] = classes.get(label, 0) + 1
    print(f"  {len(features)} annotations: {classes}")
    report["annotations"] = classes


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", type=Path, required=True,
                        help="where to download and extract the data (needs ~80 GB free)")
    parser.add_argument("--with-he", action="store_true", help="also download and read the 3.7 GB H&E image")
    parser.add_argument("--skip-download", action="store_true", help="use files already in --data-dir")
    parser.add_argument("--delete-zip", action="store_true", help="delete outs.zip after extracting it")
    args = parser.parse_args()

    data_dir = args.data_dir.resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    if not args.skip_download:
        fetch(data_dir, args.with_he)
    outs = extract(data_dir, args.delete_zip)

    inspect_experiment(outs)
    files = inspect_focus_files(outs)
    passed = inspect_spatialdata(outs, len(files))
    inspect_annotations(data_dir)
    if args.with_he:
        inspect_he(data_dir, outs)

    report_path = data_dir / "inspection_report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str))
    section("Done")
    print(f"  Report written to {report_path}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
