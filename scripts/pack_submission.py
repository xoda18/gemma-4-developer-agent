#!/usr/bin/env python3
"""Packs the contents of submission/ into submission.zip with agent.yaml at
the archive root (the harness requires the root config directly in the zip,
not nested inside a 'submission/' directory)."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBMISSION_DIR = ROOT / "submission"
OUTPUT_ZIP = ROOT / "submission.zip"


def main() -> int:
    if not (SUBMISSION_DIR / "agent.yaml").exists():
        print(f"error: {SUBMISSION_DIR / 'agent.yaml'} not found", file=sys.stderr)
        return 1

    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(SUBMISSION_DIR.rglob("*")):
            if path.is_dir():
                continue
            if path.name == ".gitkeep":
                continue
            arcname = path.relative_to(SUBMISSION_DIR)
            zf.write(path, arcname)
            print(f"  + {arcname}")

    size_mb = OUTPUT_ZIP.stat().st_size / (1024 * 1024)
    print(f"\nWrote {OUTPUT_ZIP} ({size_mb:.2f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
