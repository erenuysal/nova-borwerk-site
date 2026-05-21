"""Generate a full Turkey outline SVG (turkiye-siyah.svg).

Used as a reference asset; the live site uses create_marmara_map.py for the
Marmara service-area map on index.html.
"""
import json
import urllib.request
from pathlib import Path

SITE = Path(r"C:\Users\hmzis\Desktop\eren dosya\nova-borwerk-site-main")
OUT = SITE / "assets" / "harita" / "turkiye-siyah.svg"

url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/TUR.geo.json"
data = json.loads(urllib.request.urlopen(url, timeout=15).read())
coords = data["features"][0]["geometry"]["coordinates"]

min_lon, min_lat, max_lon, max_lat = 26.04, 35.82, 44.79, 42.14
pad = 20
scale = 40
min_lon2 = min_lon - pad / scale
max_lat2 = max_lat + pad / scale
svg_w = (max_lon - min_lon) * scale + pad * 2
svg_h = (max_lat - min_lat) * scale + pad * 2


def ring_to_path(ring):
    parts = []
    for i, (lon, lat) in enumerate(ring):
        x = (lon - min_lon2) * scale + pad
        y = (max_lat2 - lat) * scale + pad
        parts.append(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}")
    parts.append("Z")
    return " ".join(parts)


paths = []


def add_paths(obj):
    if not obj:
        return
    if (
        isinstance(obj, list)
        and len(obj) >= 2
        and isinstance(obj[0], (list, tuple))
        and len(obj[0]) == 2
        and isinstance(obj[0][0], (int, float))
    ):
        paths.append(ring_to_path(obj))
        return
    if isinstance(obj, list):
        for item in obj:
            add_paths(item)


add_paths(coords)

svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w:.0f} {svg_h:.0f}" role="img" aria-label="Türkiye haritası">
  <rect width="100%" height="100%" fill="#060a14"/>
  <path fill="#0f1419" stroke="#2d3748" stroke-width="2" d="{' '.join(paths)}"/>
</svg>
"""
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg, encoding="utf-8")
print(f"Saved {OUT}")

cities = {
    "Tekirdag": (27.52, 40.98),
    "Istanbul": (28.72, 41.02),
    "Yalova": (29.28, 40.65),
    "Kocaeli": (29.92, 40.77),
    "Sakarya": (30.40, 40.69),
    "Bursa": (29.06, 40.19),
    "Balikesir": (27.89, 39.65),
    "Canakkale": (26.41, 40.15),
}
for name, (lon, lat) in cities.items():
    x = (lon - min_lon2) * scale + pad
    y = (max_lat2 - lat) * scale + pad
    print(f"{name}: top:{y / svg_h * 100:.1f}%; left:{x / svg_w * 100:.1f}%")
