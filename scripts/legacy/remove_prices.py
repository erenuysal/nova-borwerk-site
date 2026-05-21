import fitz
import re
import shutil
from pathlib import Path

OUTPUT_PDF = Path(r"C:\Users\hmzis\Desktop\eren dosya\e-katalog.pdf")
SOURCE_PDF = Path(r"C:\Users\hmzis\Desktop\eren dosya\e-katalog-yedek.pdf")

PRICE_RE = re.compile(r"^[\d.,]+\s*\$$")

# Decorative ribbon images used on compressor pages.
PRICE_IMAGE_XREFS = {6429, 6433, 6437, 6439, 6441, 10415, 10417, 10421, 10423, 10425}


def get_prices(page):
    prices = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                if PRICE_RE.match(text):
                    prices.append(fitz.Rect(span["bbox"]))
    return prices


def get_price_image_rects(page, price_rect):
    rects = []
    search = price_rect + (-55, -40, 25, 20)
    for img in page.get_images(full=True):
        xref = img[0]
        for rect in page.get_image_rects(xref):
            if rect.width > 180 or rect.height > 120:
                continue
            if xref in PRICE_IMAGE_XREFS or (
                rect.intersects(search) and rect.x0 > 400 and rect.y1 <= price_rect.y1 + 15
            ):
                if rect.intersects(search):
                    rects.append(rect)
    return rects


def build_redaction_rect(page, price_rect):
    rects = [price_rect]
    rects.extend(get_price_image_rects(page, price_rect))

    merged = fitz.Rect(price_rect)
    for rect in rects:
        merged |= rect

    # Cover only the ribbon + short arrow above it, not nearby specs/detail images.
    merged.x0 = min(merged.x0 - 8, 430)
    merged.x1 = max(merged.x1 + 5, 572)
    merged.y0 = merged.y0 - 28
    merged.y1 = merged.y1 + 5

    page_rect = page.rect
    merged &= page_rect
    return merged


def remove_prices(input_path, output_path):
    doc = fitz.open(input_path)
    total_redactions = 0
    pages_with_prices = 0

    for page in doc:
        prices = get_prices(page)
        if not prices:
            continue

        pages_with_prices += 1
        for price_rect in prices:
            redact_rect = build_redaction_rect(page, price_rect)
            page.add_redact_annot(redact_rect, fill=(1, 1, 1))
            total_redactions += 1

        page.apply_redactions()

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    return pages_with_prices, total_redactions


def verify_no_prices(pdf_path):
    doc = fitz.open(pdf_path)
    remaining = []
    for i, page in enumerate(doc):
        text = page.get_text()
        for match in PRICE_RE.finditer(text):
            remaining.append((i + 1, match.group()))
    doc.close()
    return remaining


if __name__ == "__main__":
    pages, redactions = remove_prices(SOURCE_PDF, OUTPUT_PDF)
    remaining = verify_no_prices(OUTPUT_PDF)

    print(f"Saved: {OUTPUT_PDF}")
    print(f"Pages with prices removed: {pages}")
    print(f"Price tags removed: {redactions}")
    print(f"Remaining price text matches: {len(remaining)}")
    if remaining[:10]:
        print("Sample remaining:", remaining[:10])
