"""Repository paths — every script imports these instead of hard-coding a directory.

Override the repository root with the APD_ROOT environment variable if you run
the scripts from somewhere else.
"""
import os
from pathlib import Path

ROOT      = Path(os.environ.get("APD_ROOT", Path(__file__).resolve().parents[1]))
RAW       = ROOT / "data" / "raw"        # third-party sources, not redistributed
REFERENCE = ROOT / "data" / "reference"  # small crosswalks, tracked
DERIVED   = ROOT / "data" / "derived"    # panels produced by code/01_build
FIG       = ROOT / "output" / "figures"
TAB       = ROOT / "output" / "tables"

for _p in (RAW, REFERENCE, DERIVED, FIG, TAB):
    _p.mkdir(parents=True, exist_ok=True)
