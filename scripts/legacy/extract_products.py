import fitz
import re
import os
from pathlib import Path

pdf_candidates = [
    Path(r"C:\Users\hmzis\Desktop\eren dosya\e-katalog-fiyatsiz.pdf"),
    Path(r"C:\Users\hmzis\Desktop\eren dosya\e-katalog.pdf"),
    Path(r"C:\Users\hmzis\Desktop\eren dosya\e-katalog-yedek.pdf"),
]
pdf_path = next((p for p in pdf_candidates if p.exists()), None)
if not pdf_path:
    raise SystemExit("PDF not found")

doc = fitz.open(pdf_path)
pages_dir = Path(r"C:\Users\hmzis\Desktop\eren dosya\sayfalar")

for i, page in enumerate(doc):
    text = page.get_text()
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    title = ""
    for line in lines[:20]:
        if " - " in line and len(line) > 10:
            title = line
            break
        if any(
            kw in line.lower()
            for kw in [
                "kompres",
                "hava",
                "vidal",
                "piston",
                "yağsız",
                "sessiz",
                "silobas",
                "kurutucu",
                "filtre",
                "tabanca",
                "hortum",
                "pnömatik",
                "alet",
                "kaynak",
                "matkap",
                "zımpara",
                "spiral",
                "vidalama",
                "taşlama",
                "kesme",
                "aparat",
                "pençe",
                "göçük",
                "kapı",
                "jeneratör",
                "pompa",
                "motor",
                "regülatör",
                "manometre",
                "valf",
                "nipel",
                "rakor",
            ]
        ):
            if len(line) > 8 and not title:
                title = line

    model = ""
    for line in lines[:25]:
        match = re.search(
            r"\b(GP\s*\d+|GT\s*\d+|GS\s*\d+|GA\s*\d+|GL\s*\d+|GK\s*\d+|GV\s*\d+|GR\s*\d+|GN\s*\d+|GM\s*\d+|GAP\s*\d+)\b",
            line,
            re.I,
        )
        if match:
            model = match.group(1).replace(" ", " ")
            break

    print(f"Page {i + 1:3d} | {title[:70] if title else '(no title)':70s} | {model}")

doc.close()
print(f"\nPNG files in sayfalar: {len(list(pages_dir.glob('*.png'))) if pages_dir.exists() else 0}")
