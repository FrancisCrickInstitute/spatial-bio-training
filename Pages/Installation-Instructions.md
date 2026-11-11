# Preparation for the Spatial Biology Workshop

Please complete these steps **before the workshop**, on the laptop you will bring. Installation downloads several gigabytes, so use a good internet connection, preferably **not** over a VPN (see [Troubleshooting](#troubleshooting)).

If you have trouble, contact the organisers (contact details to follow) and send them the full output of `pixi run check-full`.

You will need:

| Day | Software | Used for |
|---|---|---|
| 1 | QuPath 0.7, with the InstanSeg and Deep Java Library extensions | Interactive image analysis |
| 2 | pixi, which installs Python 3.12 and every package used in the notebooks | Analysis in Python (Jupyter notebooks) |

Supported systems are **Windows** (64-bit), **macOS** on Apple Silicon (M1 or later), and **Linux** (64-bit). Macs with Intel processors are not supported for Day 2. You do not need a GPU.

## 1. Download the workshop materials

Either:

- **Without git:** on the [repository page](https://github.com/FrancisCrickInstitute/spatial-bio-training), click the green **Code** button, then **Download ZIP**, and unzip it somewhere in your home folder.
- **With git:**

  ```bash
  git clone https://github.com/FrancisCrickInstitute/spatial-bio-training.git
  ```

The folder you end up with, which contains `pixi.toml`, is called the **workshop folder** below.

## 2. Install QuPath (Day 1)

1. Download **QuPath 0.7** for your operating system from [qupath.github.io](https://qupath.github.io/). On a Mac, choose the Apple Silicon (`aarch64`) build unless your Mac has an Intel processor.
2. Install it, and start QuPath once to check it opens.
   > **macOS:** if macOS says QuPath "cannot be opened", right-click (or Control-click) the app in Finder and choose **Open**.
3. Install the extensions:
   1. Open **Extensions › Manage extensions**.
   2. In the QuPath catalog, click the green **+** next to **InstanSeg** and install it. Do the same for **Deep Java Library** if it isn't installed with InstanSeg.
   3. Restart QuPath.
4. Download PyTorch, which InstanSeg needs. Open **Extensions › Deep Java Library › Manage DJL engines** and download **PyTorch** (over 100 MB). If you skip this step, InstanSeg downloads PyTorch the first time you run it, but it is better done now, on a good connection.
5. Download the segmentation model:
   1. Open **Extensions › InstanSeg**.
   2. Click the folder icon and choose a folder to keep models in (for example, a `qupath-models` folder in your home folder).
   3. Select **fluorescence_nuclei_and_cells** from the model list and click the download button.

## 3. Install pixi (Day 2)

[pixi](https://pixi.sh) installs Python and all the packages the Day 2 notebooks need into the workshop folder. It does not change any other Python or conda installation you already have.

- **Windows:** open **PowerShell** and run:

  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm -useb https://pixi.sh/install.ps1 | iex"
  ```

- **macOS / Linux:** open **Terminal** and run:

  ```bash
  curl -fsSL https://pixi.sh/install.sh | sh
  ```

Close and reopen PowerShell or Terminal, then run:

```bash
pixi --version
```

You need **pixi 0.68 or later**. If you already had an older pixi, update it with `pixi self-update`.

## 4. Set up the Python environment

In PowerShell or Terminal, go to the workshop folder and install the environment:

```bash
cd path/to/spatial-bio-training
pixi install
```

This downloads several gigabytes and can take a while. pixi installs the exact package versions recorded in `pixi.lock`, the same versions the workshop was tested with.

## 5. Check that everything works

From the workshop folder, run:

```bash
pixi run check-full
```

This checks that every package imports, reports whether a GPU is available, and downloads the InstanSeg model the notebooks use, then segments a small test image. It needs an internet connection the first time. The last lines should be:

```text
[ OK ] InstanSeg segmented a test image: ...

Everything looks good. You're ready for the workshop.
```

`Compute device for InstanSeg: cpu` is fine: the workshop is designed to run without a GPU. Warnings printed before the `[ OK ]` lines can be ignored.

If any line says `[FAIL]`, see [Troubleshooting](#troubleshooting), then send the full output to the organisers.

## 6. Download the workshop data

The data download link will be added here.

## During the workshop

To start JupyterLab for the Day 2 notebooks, go to the workshop folder and run:

```bash
pixi run lab
```

Always start JupyterLab this way, from the workshop folder, so that it uses the workshop environment rather than another Python installation.

## Troubleshooting

### Certificate errors (`UnknownIssuer`, `CERTIFICATE_VERIFY_FAILED`)

Some networks, VPNs and antivirus programs intercept secure (HTTPS) connections. pixi then fails with an error mentioning `UnknownIssuer` or invalid certificates, and the InstanSeg model download fails with `CERTIFICATE_VERIFY_FAILED`. The QuPath model and PyTorch downloads can fail the same way.

Disconnect from the VPN, or use a different network (for example, at home), and try again. Once installed, everything works on any network.

### `pixi install` says the lock file version is not supported

Your pixi is too old to read `pixi.lock`. Run `pixi self-update`, then `pixi install` again.

### I already have Python, conda or Anaconda

That's fine. pixi keeps the workshop environment in a hidden `.pixi` folder inside the workshop folder and doesn't interfere with other installations. Just make sure you run the workshop commands with `pixi run`.

### "Cache is on a network filesystem" warning (HPC and shared drives)

If your home folder is on a network drive, pixi may warn that its cache is on a network filesystem and redirect it. This is harmless.

### I can't use pixi

pixi is the supported installation route. If you can't use it, `requirements.txt` lists the same packages for pip, with version ranges rather than the exact tested versions. In a new **Python 3.12** virtual environment, run `pip install -r requirements.txt`, then `python Scripts/check_install.py --full`. We may not be able to help with problems in environments set up this way.
