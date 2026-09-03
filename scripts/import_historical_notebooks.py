"""Import historical notebooks without leaking workstation metadata.

The script deliberately preserves analytical cells and visual outputs: the goal is
to expose the depth of the original work, not to replace it with a small demo.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

HISTORICAL_NOTEBOOKS = (
    "P3_01_notebook.ipynb",
    "p3_quant.ipynb",
    "p3_qual.ipynb",
    "P3_01_plotly.ipynb",
    "P3_01_voila.ipynb",
)

PROVENANCE_CELL = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        (
            "> **Historical study — preserved evidence.** This notebook records the original "
            "P3 exploration and outputs. Workstation paths and transient runtime metadata were "
            "redacted for publication. The maintained, typed implementation lives in "
            "`src/off_quality`; the historical notebook is retained to demonstrate the breadth "
            "and evolution of the work."
        )
    ],
}

PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE),
    re.compile(r"[A-Za-z]:\\ProgramData\\[^\n\r\"]+", re.IGNORECASE),
    re.compile(r"/home/[^/\s]+", re.IGNORECASE),
)


def redact_text(value: str) -> str:
    for pattern in PATH_PATTERNS:
        value = pattern.sub("<LOCAL_PATH>", value)
    return value


def sanitize(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, Mapping):
        return {str(key): sanitize(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [sanitize(item) for item in value]
    return value


def sanitize_notebook(source: Path, destination: Path) -> None:
    notebook = sanitize(json.loads(source.read_text(encoding="utf-8")))
    notebook["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    }
    for cell in notebook.get("cells", []):
        cell["metadata"] = {}
        if cell.get("cell_type") != "code":
            cell.pop("execution_count", None)
    notebook["cells"].insert(0, PROVENANCE_CELL)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(notebook, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    for name in HISTORICAL_NOTEBOOKS:
        sanitize_notebook(args.source / name, args.destination / name)


if __name__ == "__main__":
    main()
