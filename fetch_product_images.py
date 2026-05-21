#!/usr/bin/env python3
"""Fetch official GAP product images — run from repo root."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

from fetch_product_images import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
