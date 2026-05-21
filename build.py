"""Rebuild Nova Borwerk site from catalog source."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
PYTHON = sys.executable

STEPS = [
    ("build_site_assets.py", "CSS, JS ve OG görseli"),
    ("generate_urunler_site.py", "HTML sayfaları, sitemap, robots"),
    ("audit_site.py", "Kırık link kontrolü"),
]


def run(script: str) -> None:
    print(f"\n>> python scripts/{script}")
    subprocess.check_call([PYTHON, str(SCRIPTS / script)], cwd=ROOT)


def main() -> None:
    for script, label in STEPS:
        print(f"--- {label} ---")
        run(script)
    print("\nSite build tamamlandi.")


if __name__ == "__main__":
    main()
