"""Generate the Marmara service-area map (marmara-siyah.svg) for index.html.

Uses Natural Earth coastline data. For a full-country outline, see create_turkey_map.py.
"""
import json
import urllib.request
from pathlib import Path

from shapely.geometry import MultiPolygon, Polygon, box, shape

from _paths import SITE_ROOT

OUT = SITE_ROOT / "assets" / "harita" / "marmara-siyah.svg"

MIN_LON, MAX_LON = 25.85, 31.05
MIN_LAT, MAX_LAT = 39.35, 41.52
MARMARA_BOX = box(MIN_LON, MIN_LAT, MAX_LON, MAX_LAT)

PAD = 30
SCALE = 136
SVG_W = (MAX_LON - MIN_LON) * SCALE + PAD * 2
SVG_H = (MAX_LAT - MIN_LAT) * SCALE + PAD * 2

NE_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
    "master/geojson/ne_10m_admin_0_countries.geojson"
)

CITIES = [
    ("Tekirdağ", 27.52, 40.98),
    ("Çanakkale", 26.55, 40.15),
    ("Balıkesir", 27.89, 39.65),
    ("Bursa", 29.06, 40.19),
    ("Yalova", 29.28, 40.65),
    ("Kocaeli", 29.92, 40.77),
    ("Sakarya", 30.40, 40.69),
]
HUB = ("Avcılar / İstanbul", 28.72, 41.02)


def proj(lon: float, lat: float) -> tuple[float, float]:
    x = (lon - MIN_LON) * SCALE + PAD
    y = (MAX_LAT - lat) * SCALE + PAD
    return x, y


def ring_to_svg(ring) -> str:
    parts = []
    for i, (lon, lat) in enumerate(ring):
        x, y = proj(lon, lat)
        parts.append(f"{'M' if i == 0 else 'L'}{x:.2f},{y:.2f}")
    parts.append("Z")
    return " ".join(parts)


def polygon_paths(poly: Polygon) -> list[str]:
    paths = [ring_to_svg(list(poly.exterior.coords))]
    for interior in poly.interiors:
        paths.append(ring_to_svg(list(interior.coords)))
    return paths


def load_marmara_land():
    data = json.loads(urllib.request.urlopen(NE_URL, timeout=45).read())
    turkey = None
    for feature in data["features"]:
        props = feature.get("properties", {})
        if props.get("ISO_A3") == "TUR" or props.get("ADMIN") == "Turkey":
            turkey = shape(feature["geometry"])
            break
    if turkey is None:
        raise RuntimeError("Turkey not found in Natural Earth dataset")

    land = turkey.intersection(MARMARA_BOX).buffer(0)
    land = land.simplify(0.008, preserve_topology=True)

    paths = []
    if isinstance(land, Polygon):
        polys = [land]
    elif isinstance(land, MultiPolygon):
        polys = sorted(land.geoms, key=lambda p: p.area, reverse=True)
    else:
        polys = []

    for poly in polys:
        if poly.area < 0.002:
            continue
        paths.extend(polygon_paths(poly))
    return paths


def main():
    land_paths = load_marmara_land()
    if not land_paths:
        raise RuntimeError("No land geometry for Marmara")

    hx, hy = proj(HUB[1], HUB[2])
    lines = []
    labels = []
    for name, lon, lat in CITIES:
        cx, cy = proj(lon, lat)
        lines.append(
            f'<line x1="{hx:.2f}" y1="{hy:.2f}" x2="{cx:.2f}" y2="{cy:.2f}" '
            f'stroke="#f5c542" stroke-width="1.1" stroke-opacity="0.22" stroke-dasharray="4 6"/>'
        )
        labels.append(
            f'<g><circle cx="{cx:.2f}" cy="{cy:.2f}" r="4.2" fill="#ff5959" stroke="#ffd970" stroke-width="1.3"/>'
            f'<text x="{cx:.2f}" y="{cy + 15:.2f}" text-anchor="middle" fill="#eef3ff" '
            f'font-family="Segoe UI,Arial,sans-serif" font-size="10.5" font-weight="700">{name}</text></g>'
        )

    sea_cx, sea_cy = proj(28.95, 40.58)
    land_svgs = "\n  ".join(
        f'<path d="{d}" fill="url(#landGrad)" stroke="#627089" stroke-width="1.4" stroke-linejoin="round" stroke-linecap="round"/>'
        for d in land_paths
    )

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W:.0f} {SVG_H:.0f}" role="img" aria-label="Marmara Bölgesi haritası">
  <defs>
    <linearGradient id="seaGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0c2244"/>
      <stop offset="100%" stop-color="#050810"/>
    </linearGradient>
    <linearGradient id="landGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#303948"/>
      <stop offset="100%" stop-color="#171e29"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#seaGrad)"/>
  <ellipse cx="{sea_cx:.1f}" cy="{sea_cy:.1f}" rx="185" ry="78" fill="#1a4480" fill-opacity="0.35"/>
  {land_svgs}
  {''.join(lines)}
  {''.join(labels)}
  <g>
    <circle cx="{hx:.2f}" cy="{hy:.2f}" r="20" fill="#f5c542" fill-opacity="0.12"/>
    <circle cx="{hx:.2f}" cy="{hy:.2f}" r="6.5" fill="#ff5959" stroke="#ffd970" stroke-width="2"/>
    <rect x="{hx - 52:.1f}" y="{hy - 28:.1f}" width="104" height="20" rx="10" fill="#0a1020" fill-opacity="0.9" stroke="#f5c542" stroke-opacity="0.5"/>
    <text x="{hx:.2f}" y="{hy - 14:.1f}" text-anchor="middle" fill="#ffd970" font-family="Segoe UI,Arial,sans-serif" font-size="10.5" font-weight="800">{HUB[0]}</text>
  </g>
</svg>
"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Saved {OUT} ({SVG_W:.0f}x{SVG_H:.0f}) — {len(land_paths)} coastline paths")


if __name__ == "__main__":
    main()
