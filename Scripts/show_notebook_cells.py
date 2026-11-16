"""Print the cells of a notebook that contain any of the given text, with their indexes.

Useful for reading or reviewing notebook code from a terminal, and for finding a cell's index to pass to
run_notebook_cells.py.

Usage:

    pixi run python Scripts/show_notebook_cells.py NOTEBOOK TEXT [TEXT ...]
"""

import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cells = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["cells"]
    for index, cell in enumerate(cells):
        source = "".join(cell["source"])
        if any(text in source for text in sys.argv[2:]):
            print(f"===== cell {index} ({cell['cell_type']})\n{source}\n")


if __name__ == "__main__":
    main()
