"""Shared paths for Nova Borwerk build scripts."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_ROOT = REPO_ROOT
SOURCE_DIR = REPO_ROOT / "source"
CATALOG_PATH = SITE_ROOT / "assets" / "urunler" / "catalog.json"
MANIFEST_PATH = SITE_ROOT / "assets" / "urunler" / "image_sources_manifest.json"
PDF_PATH = SOURCE_DIR / "e-katalog.pdf"
SITE_ASSETS = SITE_ROOT / "assets" / "urunler"
