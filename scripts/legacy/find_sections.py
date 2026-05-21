import fitz
import re
from pathlib import Path

pdf_path = Path(r"C:\Users\hmzis\Desktop\eren dosya\e-katalog-fiyatsiz.pdf")
doc = fitz.open(pdf_path)

SECTION_KEYWORDS = [
    "KOMPRES",
    "HAVA",
    "VİDALI",
    "VIDALI",
    "PİSTON",
    "PISTON",
    "SESSİZ",
    "SESSIZ",
    "YAĞSIZ",
    "YAGSIZ",
    "DİZEL",
    "DIZEL",
    "KURUTUCU",
    "FİLTRE",
    "FILTRE",
    "HAVA TABANCA",
    "TABANCA",
    "HORTUM",
    "PNÖMAT",
    "PNOMAT",
    "ALET",
    "KAYNAK",
    "JENERAT",
    "POMPA",
    "LASTİK",
    "LASTIK",
    "KAPORTA",
    "LİFT",
    "LIFT",
    "GÖÇÜK",
    "GOCUK",
    "TOOLS",
]

for i, page in enumerate(doc):
    text = page.get_text()
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    upper_lines = [line for line in lines if line.isupper() and len(line) > 8]
    title_candidates = []
    for line in lines[:12]:
        upper_ratio = sum(1 for c in line if c.isupper()) / max(len(line.replace(" ", "")), 1)
        if len(line) >= 10 and upper_ratio > 0.7:
            if any(kw in line.upper() for kw in SECTION_KEYWORDS):
                title_candidates.append(line)

    if title_candidates:
        print(f"Page {i+1:3d}: {title_candidates[0][:90]}")

doc.close()
