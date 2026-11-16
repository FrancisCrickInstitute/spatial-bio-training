"""Check that the Day 2 workshop environment is installed and working.

Run it with pixi from the repository root:

    pixi run check        # imports, versions, compute device
    pixi run check-full   # also tests image reading (downloading Java and Bio-Formats on first run),
                          # downloads the InstanSeg model and segments a test image

If anything fails, send the full output to the workshop organisers before the course.
"""

import argparse
import importlib
import importlib.metadata
import logging
import platform
import sys
import traceback

# (module to import, distribution name used for its version, what it is for)
PACKAGES = [
    ("sopa", "sopa", "reading, segmenting and aggregating spatial data"),
    ("spatialdata", "spatialdata", "the SpatialData data model"),
    ("spatialdata_io", "spatialdata-io", "reading Xenium output"),
    ("spatialdata_plot", "spatialdata-plot", "plotting SpatialData objects"),
    ("anndata", "anndata", "cell-by-feature tables"),
    ("scanpy", "scanpy", "clustering and cell types"),
    ("squidpy", "squidpy", "spatial statistics"),
    ("networkx", "networkx", "graphs and Louvain communities"),
    ("igraph", "python-igraph", "fast Leiden clustering"),
    ("segtraq", "segtraq", "segmentation quality control"),
    ("torch", "torch", "deep learning backend for InstanSeg"),
    ("instanseg", "instanseg-torch", "cell segmentation"),
    ("jupyterlab", "jupyterlab", "notebooks"),
    ("bioio", "bioio", "reading microscopy images"),
    ("bioio_bioformats", "bioio-bioformats", "reading images through Bio-Formats"),
    ("bioio_ome_tiff", "bioio-ome-tiff", "reading OME-TIFF without Java (fallback)"),
    ("skimage", "scikit-image", "classic image analysis"),
    ("geopandas", "geopandas", "outlines and GeoJSON"),
]

OK = "[ OK ]"
WARN = "[WARN]"
FAIL = "[FAIL]"
WARNINGS = []  # problems the workshop can work around


def check_python():
    version = sys.version_info
    ok = (version.major, version.minor) == (3, 12)
    print(f"{OK if ok else FAIL} Python {platform.python_version()} ({sys.executable})")
    if not ok:
        print("       Expected Python 3.12. Are you running this with `pixi run check`?")
    return ok


def check_imports():
    all_ok = True
    for module, dist, purpose in PACKAGES:
        try:
            importlib.import_module(module)
            version = importlib.metadata.version(dist)
            print(f"{OK} {dist:<20} {version:<12} {purpose}")
        except Exception as error:  # report every failure, not just the first
            all_ok = False
            print(f"{FAIL} {dist:<20} {'':<12} {purpose}")
            print(f"       {type(error).__name__}: {error}")
    return all_ok


def check_device():
    import torch

    if torch.cuda.is_available():
        device = f"cuda ({torch.cuda.get_device_name(0)})"
    elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        device = "mps (Apple GPU)"
    else:
        device = "cpu"
    print(f"{OK} Compute device for InstanSeg: {device}")
    if device == "cpu":
        print("       No GPU found. That's fine for the workshop: live segmentation uses a small tile.")
    return True


def make_test_image(size=256, pixel_size_um=0.5, seed=0):
    """A two-channel synthetic image: round 'nuclei' and larger 'cells' around them."""
    import numpy as np

    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[:size, :size]
    nuclei = np.zeros((size, size), dtype=np.float32)
    cells = np.zeros((size, size), dtype=np.float32)
    nucleus_radius = 4.0 / pixel_size_um  # 4 µm
    cell_radius = 8.0 / pixel_size_um  # 8 µm
    spacing = int(2.2 * cell_radius)
    for cy in range(spacing // 2, size, spacing):
        for cx in range(spacing // 2, size, spacing):
            cy_j, cx_j = cy + rng.integers(-3, 4), cx + rng.integers(-3, 4)
            dist = np.hypot(yy - cy_j, xx - cx_j)
            nuclei[dist < nucleus_radius] = 1.0
            cells[dist < cell_radius] = 0.6
    image = np.stack([nuclei, cells], axis=-1)  # (Y, X, C)
    image += rng.normal(0, 0.05, image.shape).astype(np.float32)
    return image


def check_instanseg():
    import warnings

    import numpy as np
    from instanseg import InstanSeg

    # PyTorch/InstanSeg emit harmless deprecation and "no CUDA" warnings; hide them here
    # so participants aren't alarmed. They still appear in the notebooks.
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning)

    pixel_size_um = 0.5
    print("       Downloading/loading the InstanSeg model (first run only needs internet)...")
    try:
        model = InstanSeg("fluorescence_nuclei_and_cells", verbosity=0)
    except Exception as error:
        if "CERTIFICATE_VERIFY_FAILED" in str(error):
            print(f"{FAIL} InstanSeg model download: a secure connection to github.com was refused.")
            print("       Your network (or VPN, or antivirus) is probably intercepting HTTPS traffic.")
            print("       Try again off the VPN or on another network, or ask the organisers for help.")
            return False
        raise
    image = make_test_image(pixel_size_um=pixel_size_um)
    labels = model.eval_small_image(image, pixel_size=pixel_size_um, return_image_tensor=False)
    labels = np.asarray(labels.cpu()).squeeze()  # (2, Y, X): nuclei, cells
    counts = [len(np.unique(channel)) - 1 for channel in labels]
    ok = max(counts) > 0
    # Exact counts don't matter: this only checks the model loads and runs.
    print(f"{OK if ok else FAIL} InstanSeg segmented a test image: "
          f"{counts[0]} nuclei, {counts[-1]} cells")
    return ok


def check_image_reading():
    """Read a tile from a small OME-TIFF through Bio-Formats, and through the pure-Python fallback.

    The first Bio-Formats read downloads a Java runtime and the Bio-Formats library (first run only needs
    internet). If that fails, the notebooks fall back to bioio-ome-tiff, so it is only a warning."""
    import tempfile
    from pathlib import Path

    import bioio_bioformats
    import bioio_ome_tiff
    import numpy as np
    import tifffile
    from bioio import BioImage

    data = np.random.default_rng(0).integers(0, 1000, (2, 512, 512), dtype=np.uint16)
    expected = data[1, 100:300, 200:400]
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "test.ome.tif"
        tifffile.imwrite(path, data, ome=True, tile=(256, 256),
                         metadata={"axes": "CYX", "Channel": {"Name": ["DAPI", "CD3E"]},
                                   "PhysicalSizeX": 0.2125, "PhysicalSizeY": 0.2125})

        def read_tile(reader, **kwargs):
            image = BioImage(path, reader=reader, **kwargs)
            tile = image.get_image_dask_data("YX", C=image.channel_names.index("CD3E"))[100:300, 200:400]
            return np.array_equal(np.asarray(tile.compute()), expected)

        ok = read_tile(bioio_ome_tiff.Reader)
        print(f"{OK if ok else FAIL} Reading OME-TIFF without Java (bioio-ome-tiff)")

        print("       Starting Bio-Formats (the first run downloads Java and Bio-Formats, and needs internet)...")
        logging.getLogger("bioio").setLevel(logging.CRITICAL)  # it logs the same error again
        try:
            bf_ok = read_tile(bioio_bioformats.Reader, dask_tiles=True, tile_size=(256, 256))
            print(f"{OK if bf_ok else WARN} Reading images through Bio-Formats")
            if not bf_ok:
                WARNINGS.append("Bio-Formats read the test image incorrectly")
        except Exception as error:
            WARNINGS.append("Bio-Formats isn't available")
            print(f"{WARN} Bio-Formats isn't available: {type(error).__name__}: {str(error)[:300]}")
            if "CERTIFICATE_VERIFY_FAILED" in str(error):
                print("       Your network (or VPN, or antivirus) is probably intercepting HTTPS traffic.")
                print("       Try again off the VPN or on another network.")
            print("       The workshop still works without it: the notebooks use bioio-ome-tiff instead.")
    return ok


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--full", action="store_true",
                        help="also download the InstanSeg model and segment a test image")
    args = parser.parse_args()

    print(f"Workshop environment check on {platform.system()} {platform.machine()}\n")
    results = [check_python(), check_imports()]
    for check in [check_device] + ([check_image_reading, check_instanseg] if args.full else []):
        try:
            results.append(check())
        except Exception:
            results.append(False)
            print(f"{FAIL} {check.__name__} raised an error:")
            traceback.print_exc()

    print()
    if all(results) and WARNINGS:
        print(f"Ready for the workshop, with warnings: {'; '.join(WARNINGS)}.")
        print("See the [WARN] lines above. If you can, fix them before the workshop; the notebooks work either way.")
        return 0
    if all(results):
        print("Everything looks good. You're ready for the workshop.")
        if not args.full:
            print("Run `pixi run check-full` too, to test the segmentation model download.")
        return 0
    print("Some checks failed. Please send the full output above to the workshop organisers.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
