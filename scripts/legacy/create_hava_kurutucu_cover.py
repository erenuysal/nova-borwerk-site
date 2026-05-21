"""Create catalog-style category cover for Hava Kurutucu ve Filtreler (no PDF divider page)."""
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

BASE = Path(r"C:\Users\hmzis\Desktop\eren dosya")
PDF_PATH = BASE / "e-katalog.pdf"
if not PDF_PATH.exists():
    PDF_PATH = BASE / "e-katalog-yedek.pdf"

OUT = (
    BASE
    / "nova-borwerk-site-main"
    / "assets"
    / "urunler"
    / "hava-kurutucu-ve-filtreler"
    / "hava-kurutucu-ve-filtreler-cover.webp"
)


def load_font(size: int, bold: bool = False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def clip_product_thumb(doc, page_num: int, y0: float, y1: float, max_width: int = 180):
    page = doc[page_num - 1]
    best = None
    best_area = 0
    for img in page.get_images(full=True):
        for rect in page.get_image_rects(img[0]):
            if rect.width < 80 or rect.height < 60:
                continue
            cy = (rect.y0 + rect.y1) / 2
            if y0 <= cy <= y1 and rect.width * rect.height > best_area:
                best = rect
                best_area = rect.width * rect.height
    if not best:
        return None
    clip = fitz.Rect(best)
    zoom = max(2.0, max_width / max(clip.width, 1))
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def create_cover():
    w, h = 612, 792
    img = Image.new("RGB", (w, h), (12, 16, 24))
    draw = ImageDraw.Draw(img)

    for i in range(-h, w + h, 34):
        draw.polygon([(i, 0), (i + 70, 0), (i + 70 + h, h), (i + h, h)], fill=(18, 24, 36))

    title_font = load_font(34, bold=True)
    sub_font = load_font(15)
    brand_font = load_font(22, bold=True)

    title = "HAVA KURUTUCU VE FİLTRELER"
    title_x, title_y = int(w * 0.34), 72
    draw.text((title_x, title_y), title, fill="white", font=title_font)
    bbox = draw.textbbox((title_x, title_y), title, font=title_font)
    draw.line([(title_x, bbox[3] + 8), (title_x + 290, bbox[3] + 8)], fill=(210, 32, 39), width=5)

    draw.text((title_x, bbox[3] + 24), "Profesyoneller için en iyi çözümler", fill=(220, 220, 220), font=sub_font)
    draw.text((title_x, bbox[3] + 46), "Best Solutions for Professionals", fill=(180, 180, 180), font=sub_font)

    doc = fitz.open(PDF_PATH)
    thumbs = [
        clip_product_thumb(doc, 49, 110, 430, 200),
        clip_product_thumb(doc, 49, 430, 820, 200),
        clip_product_thumb(doc, 50, 100, 820, 200),
    ]
    doc.close()

    x = 36
    y = 250
    for thumb in [t for t in thumbs if t]:
        tw, th = thumb.size
        nh = 220
        nw = max(1, int(tw * nh / th))
        thumb = thumb.resize((nw, nh), Image.Resampling.LANCZOS)
        img.paste(thumb, (x, y))
        x += nw + 16

    draw.text((36, h - 72), "GAP® KOMPRESÖR", fill="white", font=brand_font)
    draw.line([(36, h - 44), (220, h - 44)], fill=(210, 32, 39), width=3)

    out_img = img.resize((980, int(980 * h / w)), Image.Resampling.LANCZOS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(OUT, format="WEBP", quality=86, method=6)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    create_cover()
