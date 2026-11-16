"""Check that each exercise notebook matches its solution except in the exercise cells.

Compares every notebooks/*.ipynb with solutions/ of the same name, cell by cell, and lists the cells whose source
differs. Expected differences are the exercise stubs (`# Your code here`, or a line with `...` placeholders).
Exits with status 1 if the notebooks have different numbers of cells, or a solution is missing.

Usage, from the repository folder:

    pixi run python Scripts/check_exercises.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sources(path):
    return ["".join(cell["source"]) for cell in json.loads(path.read_text(encoding="utf-8"))["cells"]]


def main():
    problems = False
    for exercise in sorted((ROOT / "notebooks").glob("*.ipynb")):
        solution = ROOT / "solutions" / exercise.name
        if not solution.exists():
            print(f"{exercise.name}: no solution")
            problems = True
            continue
        a, b = sources(exercise), sources(solution)
        if len(a) != len(b):
            print(f"{exercise.name}: {len(a)} cells, but the solution has {len(b)}")
            problems = True
            continue
        differing = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        print(f"{exercise.name}: {len(a)} cells, {len(differing)} differ from the solution")
        for i in differing:
            first_line = a[i].splitlines()[0] if a[i] else ""
            print(f"    cell {i}: {first_line[:80]}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
