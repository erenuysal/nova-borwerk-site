"""Organize nova-borwerk-site assets into subfolders and update HTML paths."""
from pathlib import Path

SITE = Path(r"C:\Users\hmzis\Desktop\eren dosya\nova-borwerk-site-main")
ASSETS = SITE / "assets"

FILE_MAP = {
    "Logo.jpg": "branding/Logo.jpg",
    "logo-nova-borwerk.jpg": "branding/logo-nova-borwerk.jpg",
    "favicon.png": "branding/favicon.png",
    "gallery-borwerk-1.jpg": "galeri/gallery-borwerk-1.jpg",
    "gallery-borwerk-2.jpg": "galeri/gallery-borwerk-2.jpg",
    "content-note-1.jpg": "galeri/content-note-1.jpg",
    "content-note-2.jpg": "galeri/content-note-2.jpg",
    "content-note-3.jpg": "galeri/content-note-3.jpg",
    "kompresor-pistonlu.jpg": "kompresor/kompresor-pistonlu.jpg",
    "kompresor-vidali.jpg": "kompresor/kompresor-vidali.jpg",
    "kompresor-silobas.jpg": "kompresor/kompresor-silobas.jpg",
    "reference-aksoy-metal.png": "referanslar/reference-aksoy-metal.png",
    "reference-albayrak-beton.png": "referanslar/reference-albayrak-beton.png",
    "reference-dvm-mold.jpg": "referanslar/reference-dvm-mold.jpg",
    "reference-fiba-yapi.png": "referanslar/reference-fiba-yapi.png",
    "reference-mertsan.png": "referanslar/reference-mertsan.png",
    "reference-yukseller-metal.png": "referanslar/reference-yukseller-metal.png",
    "autocad-sertifikasi.pdf": "belgeler/autocad-sertifikasi.pdf",
    "ibrahim-sari-teknik-profil.pdf": "belgeler/ibrahim-sari-teknik-profil.pdf",
    "ornek-teklif-dosyasi.pdf": "belgeler/ornek-teklif-dosyasi.pdf",
    "sapanlama-sertifikasi.pdf": "belgeler/sapanlama-sertifikasi.pdf",
    "ustalik-belgesi.pdf": "belgeler/ustalik-belgesi.pdf",
    "vinc-operatorlugu.pdf": "belgeler/vinc-operatorlugu.pdf",
}

PATH_REPLACEMENTS = [
    ("assets/favicon.png", "assets/branding/favicon.png"),
    ("assets/Logo.jpg", "assets/branding/Logo.jpg"),
    ("assets/logo-nova-borwerk.jpg", "assets/branding/logo-nova-borwerk.jpg"),
    ("assets/gallery-borwerk-1.jpg", "assets/galeri/gallery-borwerk-1.jpg"),
    ("assets/gallery-borwerk-2.jpg", "assets/galeri/gallery-borwerk-2.jpg"),
    ("assets/content-note-1.jpg", "assets/galeri/content-note-1.jpg"),
    ("assets/content-note-2.jpg", "assets/galeri/content-note-2.jpg"),
    ("assets/content-note-3.jpg", "assets/galeri/content-note-3.jpg"),
    ("assets/kompresor-pistonlu.jpg", "assets/kompresor/kompresor-pistonlu.jpg"),
    ("assets/kompresor-vidali.jpg", "assets/kompresor/kompresor-vidali.jpg"),
    ("assets/kompresor-silobas.jpg", "assets/kompresor/kompresor-silobas.jpg"),
    ("assets/reference-aksoy-metal.png", "assets/referanslar/reference-aksoy-metal.png"),
    ("assets/reference-albayrak-beton.png", "assets/referanslar/reference-albayrak-beton.png"),
    ("assets/reference-dvm-mold.jpg", "assets/referanslar/reference-dvm-mold.jpg"),
    ("assets/reference-fiba-yapi.png", "assets/referanslar/reference-fiba-yapi.png"),
    ("assets/reference-mertsan.png", "assets/referanslar/reference-mertsan.png"),
    ("assets/reference-yukseller-metal.png", "assets/referanslar/reference-yukseller-metal.png"),
    ("assets/autocad-sertifikasi.pdf", "assets/belgeler/autocad-sertifikasi.pdf"),
    ("assets/ibrahim-sari-teknik-profil.pdf", "assets/belgeler/ibrahim-sari-teknik-profil.pdf"),
    ("assets/ornek-teklif-dosyasi.pdf", "assets/belgeler/ornek-teklif-dosyasi.pdf"),
    ("assets/sapanlama-sertifikasi.pdf", "assets/belgeler/sapanlama-sertifikasi.pdf"),
    ("assets/ustalik-belgesi.pdf", "assets/belgeler/ustalik-belgesi.pdf"),
    ("assets/vinc-operatorlugu.pdf", "assets/belgeler/vinc-operatorlugu.pdf"),
    ("https://novaborwerk.com/assets/logo.jpg", "https://novaborwerk.com/assets/branding/Logo.jpg"),
]


def move_assets():
    moved = 0
    for name, rel_target in FILE_MAP.items():
        src = ASSETS / name
        dst = ASSETS / rel_target
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            dst.unlink()
        src.rename(dst)
        moved += 1
        print(f"Moved: {name} -> {rel_target}")
    return moved


def update_html_files():
    html_files = list(SITE.glob("*.html")) + list(SITE.glob("urunler/*.html"))
    updated = 0
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in PATH_REPLACEMENTS:
            text = text.replace(old, new)
        if text != original:
            path.write_text(text, encoding="utf-8")
            updated += 1
            print(f"Updated: {path.name}")
    return updated


if __name__ == "__main__":
    moved = move_assets()
    updated = update_html_files()
    print(f"Done: {moved} files moved, {updated} HTML files updated")
