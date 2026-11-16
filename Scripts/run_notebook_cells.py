"""Run a notebook's code cells in order without Jupyter, for checking the workshop notebooks.

For each code cell it prints the time taken, the process memory (RSS) and the cell's printed output plus the value
of its last expression (as Jupyter would show it). Figures are saved as PNGs instead of shown. It stops at the first
error, with the traceback. Lines starting with % or ! (IPython magics and shell commands) are skipped.

Usage, from the repository folder (notebooks run from their own folder, so relative data paths work):

    pixi run python Scripts/run_notebook_cells.py solutions/05_from_qupath_to_python.ipynb figures/ [first] [last]

`first` and `last` are optional cell indexes (0-based, counting markdown cells too) to run a range.
"""

import ast
import contextlib
import io
import json
import os
import sys
import time
import traceback
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import psutil  # noqa: E402


def display(*objects, **_):
    """Stand-in for IPython's display: print tables and values, cutting long lines."""
    for obj in objects:
        text = obj.to_string(max_rows=40) if hasattr(obj, "to_string") else repr(obj)
        print("\n".join(line[:160] for line in text.splitlines()))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    notebook, figure_dir = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    first = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    last = int(sys.argv[4]) if len(sys.argv) > 4 else sys.maxsize
    figure_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(notebook.parent)
    cells = json.loads(notebook.read_text(encoding="utf-8"))["cells"]

    process, peak, start_all = psutil.Process(), 0.0, time.time()
    namespace = {"__name__": "__main__", "display": display}
    plt.show = lambda *args, **kwargs: None

    for index, cell in enumerate(cells):
        if cell["cell_type"] != "code" or not first <= index <= last:
            continue
        lines = [line for line in "".join(cell["source"]).splitlines() if not line.lstrip().startswith(("%", "!"))]
        heading = next((line for line in lines if line.strip()), "")[:70]
        start, output = time.time(), io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                tree = ast.parse("\n".join(lines))
                final = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
                exec(compile(tree, f"cell{index}", "exec"), namespace)
                if final is not None:  # show the value of the last expression, as Jupyter does
                    value = eval(compile(ast.Expression(final.value), f"cell{index}", "eval"), namespace)
                    if value is not None and not hasattr(value, "savefig") and not isinstance(value, (list, tuple)):
                        display(value)
        except Exception:
            print(f"--- cell {index} FAILED after {time.time() - start:.1f} s: {heading}")
            print(output.getvalue()[-3000:])
            traceback.print_exc()
            sys.exit(1)
        rss = process.memory_info().rss / 1e9
        peak = max(peak, rss)
        figures = plt.get_fignums()
        for number in figures:
            plt.figure(number).savefig(figure_dir / f"cell{index:02d}_fig{number}.png", dpi=80)
        plt.close("all")
        print(f"--- cell {index}: {time.time() - start:6.1f} s, RSS {rss:4.1f} GB, {len(figures)} fig | {heading}")
        text = output.getvalue().strip()
        if text:
            print("    " + "\n    ".join(text.splitlines()[:40]))
        sys.stdout.flush()
    print(f"=== done in {time.time() - start_all:.0f} s, peak RSS {peak:.1f} GB")


if __name__ == "__main__":
    main()
