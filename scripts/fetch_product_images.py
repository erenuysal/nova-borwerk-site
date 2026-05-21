#!/usr/bin/env python3
"""Download high-quality product images from official GAP manufacturer sites.

Sources (preferred, manufacturer/distributor):
  - https://www.gapkompresor.com  — compressors, dryers, filters
  - https://gaptools.net          — lifts, tools, service equipment

Usage:
  python fetch_product_images.py                  # all products, rate-limited
  python fetch_product_images.py --categories pistonlu-hava-kompresorleri,vidali-hava-kompresorleri
  python fetch_product_images.py --dry-run        # match only, no downloads
  python fetch_product_images.py --force          # overwrite existing WebP files
  python fetch_product_images.py --delay 1.5      # seconds between HTTP requests

Output:
  - WebP images under assets/urunler/{category_id}/
  - Manifest: assets/urunler/image_sources_manifest.json
  - Log: fetch_product_images.log
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import logging
import re
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urljoin

import requests
from PIL import Image

from _paths import REPO_ROOT, SITE_ROOT, CATALOG_PATH, MANIFEST_PATH

LOG_PATH = REPO_ROOT / "fetch_product_images.log"

GAP_BASE = "https://www.gapkompresor.com"
TOOLS_BASE = "https://gaptools.net"
USER_AGENT = "Mozilla/5.0 (compatible; NovaBorwerkImageBot/1.0; +https://novaborwerk.com)"

# Seed URLs discovered from gapkompresor.com navigation (category pages need numeric suffix).
GAP_INDEX_PATHS = [
    "/tr/kategori/pistonlu-hava-kompresorleri/1",
    "/tr/kategori/vidali-hava-kompresorleri/2",
    "/tr/kategori/sessiz-ve-yagsiz-hava-kompresorleri/3",
    "/tr/kategori/basincli-hava-ekipmanlari/5",
    "/tr/model/gp-serisi-8-bar/1",
    "/tr/model/gpk-serisi-12-bar/2",
    "/tr/model/gpv-a-serisi-sabit-devirli/3",
    "/tr/model/gpv-e-serisi-invertorlu/4",
    "/tr/model/gpv-a-e-serisi-depo-ustu/5",
    "/tr/model/gpv-e-serisi-16-bar/6",
    "/tr/model/gps-750-serisi/7",
    "/tr/model/gps-1100-serisi/8",
    "/tr/model/gpy-1500-serisi-yuksek-devir/10",
    "/tr/model/gphk-serisi-hava-kurutuculari/11",
    "/tr/model/gpdk-serisi-kimyasal-kurutucular/12",
    "/tr/model/gpf-serisi-su-seperatoru/13",
    "/tr/model/gpht-serisi-hava-tanklari/14",
]

TOOLS_INDEX_PATHS = [
    "/tr/urunler",
    "/tr/kategori/arac-kaldirma-liftleri/1",
    "/tr/kategori/oto-servis-ekipmanlari/2",
    "/tr/kategori/oto-yikama-makinalari/3",
    "/tr/kategori/havali-gres-pompalari/4",
    "/tr/kategori/havali-el-aletleri/5",
    "/tr/kategori/kaldirma-ekipmanlari/6",
    "/tr/kategori/kaynak-ve-kaporta-cektirme-makinalari/7",
    "/tr/kategori/takim-arabalari-ve-tezgahlari/8",
]

# Catalog category -> preferred source base URL
CATEGORY_SOURCE: dict[str, str] = {
    "pistonlu-hava-kompresorleri": GAP_BASE,
    "sessiz-ve-yagsiz-hava-kompresorleri": GAP_BASE,
    "yuksek-emisli-yagsiz-kompresorler": GAP_BASE,
    "vidali-hava-kompresorleri": GAP_BASE,
    "hava-kurutucu-ve-filtreler": GAP_BASE,
    "arac-kaldirma-liftleri": TOOLS_BASE,
    "oto-servis-ekipmanlari": TOOLS_BASE,
    "yaglama-ve-yikama": TOOLS_BASE,
    "sarjli-ve-havali-el-aletleri": TOOLS_BASE,
    "vinc-ve-kaldırma-ekipmanlari": TOOLS_BASE,
    "vinc-ve-kaldirma-ekipmanlari": TOOLS_BASE,
    "kaynak-ve-kaporta-cektirme": TOOLS_BASE,
    "takim-arabalari-ve-tezgahlari": TOOLS_BASE,
}

MODEL_RE = re.compile(
    r"\b(GP[A-Z]?[\s-]?\d{2,4}[A-Z0-9]*(?:X\d+)?|GPS[\s-]?\d{3,4}(?:X\d+)?|"
    r"GPV[\s-]?[A-Z]?[\s-]?\d+|GPY[\s-]?\d+|GPHK[\s-]?\d{3,5}|GPDK[\s-]?\d+|"
    r"GPF[\s-]?\d+|GPHT[\s-]?\d+|GPT[\s-]?\d+|GPM[\s-]?\d+|GPC\dT\dM|GPH\dT)\b",
    re.I,
)
KURUTUCU_RE = re.compile(r"(\d{3,5})\s*l[uü]k\s+hava\s+kurutucu", re.I)


@dataclass
class RemoteProduct:
    base: str
    path: str
    title: str
    images: list[str]
    models: list[str] = field(default_factory=list)
    norm_title: str = ""

    @property
    def page_url(self) -> str:
        return urljoin(self.base, self.path)

    @property
    def source_name(self) -> str:
        return "gapkompresor.com" if self.base == GAP_BASE else "gaptools.net"


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def normalize_text(value: str) -> str:
    if not value:
        return ""
    text = html_lib.unescape(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    for src, dst in (
        ("&", " "),
        ("×", "x"),
        ("'", ""),
        ('"', ""),
    ):
        text = text.replace(src, dst)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _add_model_variants(found: list[str], token: str) -> None:
    token = re.sub(r"\s+", " ", token.strip().upper())
    token_compact = re.sub(r"\s+", "", token)
    for variant in {token, token_compact, token.replace(" ", "-")}:
        if variant and variant not in found:
            found.append(variant)


def extract_models(text: str) -> list[str]:
    found: list[str] = []
    raw = html_lib.unescape(text or "")
    for m in MODEL_RE.findall(raw):
        _add_model_variants(found, m)
    norm = normalize_text(raw)
    kurutucu = KURUTUCU_RE.search(norm)
    if kurutucu:
        _add_model_variants(found, f"GPHK {kurutucu.group(1)}")
    return found


def similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


class ImageFetcher:
    def __init__(self, delay: float = 1.0, timeout: float = 30.0) -> None:
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self._last_request = 0.0
        self.remote_by_model: dict[str, list[RemoteProduct]] = {}
        self.remote_all: list[RemoteProduct] = []

    def _wait(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

    def get(self, url: str) -> requests.Response:
        self._wait()
        resp = self.session.get(url, timeout=self.timeout)
        self._last_request = time.monotonic()
        resp.raise_for_status()
        return resp

    def discover_product_paths(self, base: str, seed_paths: list[str]) -> set[str]:
        paths: set[str] = set()
        for seed in seed_paths:
            url = urljoin(base, seed)
            try:
                html = self.get(url).text
            except requests.RequestException as exc:
                logging.warning("Index fetch failed %s: %s", url, exc)
                continue
            for link in re.findall(r'href="(/tr/urun/[^"]+)"', html):
                paths.add(link)
            # Expand nested category/model links one level
            for nested in re.findall(r'href="(/tr/(?:kategori|model)/[^"]+)"', html):
                if nested in seed_paths:
                    continue
                try:
                    nested_html = self.get(urljoin(base, nested)).text
                    paths.update(re.findall(r'href="(/tr/urun/[^"]+)"', nested_html))
                except requests.RequestException:
                    pass
        return paths

    def parse_product_page(self, base: str, path: str) -> RemoteProduct | None:
        url = urljoin(base, path)
        try:
            html = self.get(url).text
        except requests.RequestException as exc:
            logging.warning("Product page failed %s: %s", url, exc)
            return None

        title_m = re.search(r"<h2[^>]*>\s*([^<]+?)\s*</h2>", html, re.I | re.S)
        title = html_lib.unescape(title_m.group(1).strip()) if title_m else ""
        if not title:
            return None

        images = sorted(
            set(
                re.findall(
                    r'src="(/Content/images/product/[^"]+\.(?:png|jpg|jpeg|webp))"',
                    html,
                    re.I,
                )
            )
        )
        if not images:
            return None

        models = extract_models(title)
        norm = normalize_text(title)
        return RemoteProduct(
            base=base,
            path=path,
            title=title,
            images=images,
            models=models,
            norm_title=norm,
        )

    def build_index(self) -> None:
        logging.info("Indexing gapkompresor.com …")
        gap_paths = self.discover_product_paths(GAP_BASE, GAP_INDEX_PATHS)
        logging.info("Found %d GAP product URLs", len(gap_paths))

        logging.info("Indexing gaptools.net …")
        tools_paths = self.discover_product_paths(TOOLS_BASE, TOOLS_INDEX_PATHS)
        logging.info("Found %d GAP Tools product URLs", len(tools_paths))

        seen: set[tuple[str, str]] = set()
        for base, path in [(GAP_BASE, p) for p in gap_paths] + [(TOOLS_BASE, p) for p in tools_paths]:
            key = (base, path)
            if key in seen:
                continue
            seen.add(key)
            product = self.parse_product_page(base, path)
            if not product:
                continue
            self.remote_all.append(product)
            for model in product.models:
                self.remote_by_model.setdefault(model, []).append(product)
                compact = re.sub(r"[\s-]+", "", model)
                self.remote_by_model.setdefault(compact, []).append(product)

        logging.info("Indexed %d remote products with images", len(self.remote_all))

    def find_match(
        self,
        category_id: str,
        title: str,
        model: str,
    ) -> tuple[RemoteProduct | None, str, float]:
        preferred_base = CATEGORY_SOURCE.get(category_id)
        candidates = self.remote_all
        if preferred_base:
            preferred = [p for p in self.remote_all if p.base == preferred_base]
            if preferred:
                candidates = preferred

        product_models = extract_models(model) + extract_models(title)
        for token in product_models:
            for key in (token, re.sub(r"[\s-]+", "", token)):
                hits = self.remote_by_model.get(key.upper()) or self.remote_by_model.get(key)
                if hits:
                    scoped = [h for h in hits if not preferred_base or h.base == preferred_base] or hits
                    return scoped[0], f"model:{key}", 1.0

        # GPHK air dryers on gapkompresor.com use titles like "1200'lük Hava Kurutucu"
        gphk = re.search(r"\bGPHK[\s-]?(\d{3,5})\b", f"{model} {title}", re.I)
        if gphk:
            num = gphk.group(1)
            for remote in self.remote_all:
                if num in remote.norm_title and "kurutucu" in remote.norm_title:
                    return remote, f"gphk-capacity:{num}", 0.95

        norm_title = normalize_text(title)
        best: RemoteProduct | None = None
        best_score = 0.0
        for remote in candidates:
            score = similarity(norm_title, remote.norm_title)
            if score > best_score:
                best_score = score
                best = remote

        if best and best_score >= 0.72:
            return best, "title-fuzzy", best_score

        # Token overlap fallback for long descriptive titles
        title_tokens = set(norm_title.split())
        for remote in candidates:
            remote_tokens = set(remote.norm_title.split())
            if len(title_tokens) < 4:
                continue
            overlap = len(title_tokens & remote_tokens) / max(len(title_tokens), 1)
            score = overlap * 0.85 + similarity(norm_title, remote.norm_title) * 0.15
            if score > best_score and overlap >= 0.55:
                best_score = score
                best = remote

        if best and best_score >= 0.55:
            return best, "title-overlap", best_score

        return None, "none", 0.0

    def download_image(self, base: str, image_path: str) -> bytes | None:
        url = urljoin(base, image_path)
        try:
            resp = self.get(url)
            if resp.status_code == 200 and resp.content:
                return resp.content
        except requests.RequestException as exc:
            logging.warning("Image download failed %s: %s", url, exc)
        return None

    @staticmethod
    def save_as_webp(data: bytes, dest: Path, quality: int = 88) -> tuple[int, int]:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(__import__("io").BytesIO(data)) as img:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
            if img.mode == "RGBA":
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")
            img.save(dest, format="WEBP", quality=quality, method=6)
            return img.size


def load_catalog() -> dict:
    with CATALOG_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def resolve_output_path(relative: str) -> Path:
    rel = relative.replace("/", "\\") if "\\" in str(SITE_ROOT) else relative
    if relative.startswith("assets/"):
        return SITE_ROOT / relative
    return SITE_ROOT / relative


def process_products(
    fetcher: ImageFetcher,
    categories_filter: set[str] | None,
    dry_run: bool,
    force: bool,
) -> dict:
    catalog = load_catalog()
    manifest: dict = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "legal_note": (
            "Images sourced from official manufacturer websites (gapkompresor.com, gaptools.net). "
            "Use for Nova Borwerk product catalog representation as authorized dealer/distributor. "
            "Verify licensing for commercial use."
        ),
        "sources": {
            "gapkompresor.com": GAP_BASE,
            "gaptools.net": TOOLS_BASE,
        },
        "products": {},
        "summary": {},
    }

    stats = {
        "total": 0,
        "matched": 0,
        "downloaded": 0,
        "skipped_existing": 0,
        "failed": 0,
        "no_match": 0,
    }

    for category in catalog.get("categories", []):
        cat_id = category["id"]
        if categories_filter and cat_id not in categories_filter:
            continue

        for product in category.get("products", []):
            stats["total"] += 1
            pid = product["id"]
            title = product.get("title", "")
            model = product.get("model", "")
            image_paths: list[str] = product.get("images") or []
            if not image_paths:
                thumb = product.get("thumb")
                if thumb:
                    image_paths = [thumb]

            remote, match_method, match_score = fetcher.find_match(cat_id, title, model)
            entry = {
                "product_id": pid,
                "category_id": cat_id,
                "title": title,
                "model": model,
                "status": "pending",
                "match_method": match_method,
                "match_score": round(match_score, 3),
                "source_page": remote.page_url if remote else None,
                "source_name": remote.source_name if remote else None,
                "images": [],
            }

            if not remote:
                stats["no_match"] += 1
                entry["status"] = "no_match"
                manifest["products"][pid] = entry
                logging.warning("NO MATCH: [%s] %s", cat_id, title)
                continue

            stats["matched"] += 1
            logging.info(
                "MATCH (%s %.2f): %s -> %s",
                match_method,
                match_score,
                title[:60],
                remote.title[:60],
            )

            if dry_run:
                entry["status"] = "dry_run"
                entry["remote_images"] = [urljoin(remote.base, p) for p in remote.images]
                manifest["products"][pid] = entry
                continue

            primary_dest = resolve_output_path(image_paths[0]) if image_paths else None
            if primary_dest and primary_dest.exists() and not force:
                stats["skipped_existing"] += 1
                entry["status"] = "skipped_existing"
                manifest["products"][pid] = entry
                continue

            downloaded_any = False
            for idx, rel_path in enumerate(image_paths):
                dest = resolve_output_path(rel_path)
                if dest.exists() and not force and idx > 0:
                    continue
                src_idx = min(idx, len(remote.images) - 1)
                img_path = remote.images[src_idx]
                img_url = urljoin(remote.base, img_path)
                data = fetcher.download_image(remote.base, img_path)
                if not data:
                    entry["images"].append({"path": rel_path, "status": "download_failed", "url": img_url})
                    continue
                try:
                    w, h = ImageFetcher.save_as_webp(data, dest)
                    entry["images"].append(
                        {
                            "path": rel_path,
                            "status": "ok",
                            "url": img_url,
                            "width": w,
                            "height": h,
                        }
                    )
                    downloaded_any = True
                    logging.info("  saved %s (%dx%d)", rel_path, w, h)
                except OSError as exc:
                    entry["images"].append({"path": rel_path, "status": "convert_failed", "url": img_url, "error": str(exc)})
                    logging.error("  convert failed %s: %s", rel_path, exc)

            if downloaded_any:
                stats["downloaded"] += 1
                entry["status"] = "downloaded"
            else:
                stats["failed"] += 1
                entry["status"] = "failed"

            manifest["products"][pid] = entry

    manifest["summary"] = stats
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch official GAP product images for Nova Borwerk catalog.")
    parser.add_argument(
        "--categories",
        type=str,
        default="",
        help="Comma-separated category IDs (default: all)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Match only, do not download")
    parser.add_argument("--force", action="store_true", help="Overwrite existing WebP files")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between HTTP requests (seconds)")
    args = parser.parse_args()

    setup_logging()
    categories_filter = {c.strip() for c in args.categories.split(",") if c.strip()} or None

    fetcher = ImageFetcher(delay=args.delay)
    fetcher.build_index()

    manifest = process_products(fetcher, categories_filter, args.dry_run, args.force)

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    s = manifest["summary"]
    logging.info(
        "Done. total=%d matched=%d downloaded=%d skipped=%d failed=%d no_match=%d",
        s["total"],
        s["matched"],
        s["downloaded"],
        s["skipped_existing"],
        s["failed"],
        s["no_match"],
    )
    logging.info("Manifest written to %s", MANIFEST_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
