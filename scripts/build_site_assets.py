"""Build shared CSS, JS, and OG share image for Nova Borwerk site."""
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from _paths import SITE_ROOT
CSS_DIR = SITE_ROOT / "assets" / "css"
JS_DIR = SITE_ROOT / "assets" / "js"
BRANDING = SITE_ROOT / "assets" / "branding"

FAQ_CSS = """
.faq-list { display: grid; gap: 12px; max-width: 900px; }
.faq-item {
  border: 1px solid var(--line); border-radius: var(--radius-lg);
  background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.03));
  overflow: hidden;
}
.faq-item summary {
  cursor: pointer; padding: 18px 22px; font-weight: 800; color: var(--text);
  list-style: none; display: flex; justify-content: space-between; align-items: center; gap: 12px;
}
.faq-item summary::-webkit-details-marker { display: none; }
.faq-item summary::after { content: "+"; color: var(--gold); font-size: 1.2rem; }
.faq-item[open] summary::after { content: "−"; }
.faq-item .faq-body { padding: 0 22px 18px; color: var(--muted); }
.faq-item .faq-body p { margin: 0; }
"""

URUNLER_CSS = """
nav a.active { color: var(--gold); }
.breadcrumb { color: var(--muted); font-size: .95rem; margin-bottom: 18px; }
.breadcrumb a { color: var(--gold-2); }
.category-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.category-card {
  display: block; border: 1px solid var(--line);
  background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.03));
  box-shadow: var(--shadow); border-radius: var(--radius-lg); overflow: hidden; transition: .22s ease;
}
.category-card:hover { transform: translateY(-3px); border-color: rgba(245,197,66,.28); }
.category-card img { width: 100%; height: 150px; object-fit: cover; object-position: center top; background: #0b1430; display: block; }
.category-card-body { padding: 20px 22px 24px; }
.category-card-body h3 { margin: 0 0 10px; font-size: 1.15rem; }
.category-card-body p { margin: 0 0 14px; color: var(--muted); font-size: .96rem; }
.tag-count {
  display: inline-flex; align-items: center; padding: 8px 12px; border-radius: 999px;
  border: 1px solid rgba(245,197,66,.22); background: rgba(245,197,66,.08);
  color: var(--gold-2); font-size: .82rem; font-weight: 800;
}
.product-list { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.product-item {
  display: grid; grid-template-columns: 140px 1fr; gap: 16px; padding: 16px;
  border: 1px solid var(--line);
  background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.03));
  box-shadow: var(--shadow); border-radius: var(--radius-lg);
}
.product-item-link { color: inherit; display: contents; }
.product-thumb-wrap {
  border: none; padding: 0; background: #fff; border-radius: 14px; overflow: hidden; min-height: 140px;
}
.product-thumb-wrap img { width: 100%; height: 100%; min-height: 140px; object-fit: contain; display: block; background: #fff; }
.product-body h3 { margin: 0 0 8px; font-size: 1.02rem; line-height: 1.3; }
.product-body h3 a:hover { color: var(--gold); }
.product-model {
  display: inline-flex; margin-bottom: 10px; padding: 6px 10px; border-radius: 999px;
  background: rgba(245,197,66,.12); color: var(--gold-2); font-size: .82rem; font-weight: 800;
}
.feature-list { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 12px; padding: 0; list-style: none; }
.feature-list li {
  padding: 6px 10px; border-radius: 999px; border: 1px solid var(--line);
  background: rgba(255,255,255,.04); color: var(--text); font-size: .82rem; font-weight: 600;
}
.spec-table { width: 100%; border-collapse: collapse; font-size: .88rem; }
.spec-table th, .spec-table td { padding: 7px 9px; border-bottom: 1px solid var(--line); text-align: left; }
.spec-table th { color: var(--muted); font-weight: 700; width: 42%; }
.detail-link { display: inline-flex; margin-top: 8px; color: var(--gold-2); font-weight: 800; font-size: .88rem; }
.product-detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; align-items: start; }
.product-detail-gallery {
  background: #fff; border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--line);
}
.product-detail-gallery img { width: 100%; min-height: 320px; object-fit: contain; cursor: zoom-in; }
.product-detail-thumbs { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }
.product-detail-thumbs button {
  border: 1px solid var(--line); background: #fff; border-radius: 12px; padding: 0; overflow: hidden; width: 72px; height: 72px; cursor: pointer;
}
.product-detail-thumbs img { width: 100%; height: 100%; object-fit: contain; }
.product-detail-body h1 { margin: 0 0 12px; font-size: clamp(1.6rem, 3vw, 2.2rem); line-height: 1.15; }
.cta-row { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 24px; }
.lightbox {
  position: fixed; inset: 0; background: rgba(2, 5, 12, .92); display: none;
  align-items: center; justify-content: center; z-index: 100; padding: 24px;
}
.lightbox.open { display: flex; }
.lightbox img { max-width: min(96vw, 1200px); max-height: 92vh; object-fit: contain; border-radius: 12px; box-shadow: var(--shadow); background: #fff; }
.lightbox-close, .lightbox-nav {
  position: absolute; border: 1px solid var(--line); background: rgba(8, 16, 32, .88);
  color: var(--text); border-radius: 12px; min-height: 44px; min-width: 44px; font-size: 1.2rem; cursor: pointer;
}
.lightbox-close { top: 20px; right: 20px; }
.lightbox-nav.prev { left: 20px; top: 50%; transform: translateY(-50%); }
.lightbox-nav.next { right: 20px; top: 50%; transform: translateY(-50%); }
@media (max-width: 1100px) {
  .category-grid { grid-template-columns: 1fr 1fr; }
  .product-list { grid-template-columns: 1fr; }
  .product-detail-grid { grid-template-columns: 1fr; }
}
@media (max-width: 760px) {
  .category-grid { grid-template-columns: 1fr; }
  .product-item { grid-template-columns: 1fr; }
}
"""

MOBILE_NAV_JS = """document.addEventListener('DOMContentLoaded',()=>{const t=document.querySelector('.nav-toggle'),n=document.getElementById('site-nav');if(!t||!n)return;t.addEventListener('click',()=>{const o=n.classList.toggle('open');t.setAttribute('aria-expanded',o?'true':'false');t.setAttribute('aria-label',o?'Menüyü kapat':'Menüyü aç');});n.querySelectorAll('a').forEach(e=>{e.addEventListener('click',()=>{n.classList.remove('open');t.setAttribute('aria-expanded','false');t.setAttribute('aria-label','Menüyü aç');});});});"""

LIGHTBOX_JS = """document.addEventListener('DOMContentLoaded',()=>{const l=document.getElementById('lightbox');if(!l)return;const i=l.querySelector('img'),c=l.querySelector('.lightbox-close'),p=l.querySelector('.lightbox-nav.prev'),x=l.querySelector('.lightbox-nav.next');let g=[],d=0;function s(e){if(!g.length)return;d=(e+g.length)%g.length;i.src=g[d];i.alt='Ürün görseli '+(d+1);l.classList.add('open');}function o(){l.classList.remove('open');i.src='';}document.querySelectorAll('[data-gallery]').forEach(e=>{e.addEventListener('click',()=>{g=e.dataset.gallery.split('|').filter(Boolean);s(Number(e.dataset.index||0));});});c.addEventListener('click',o);p.addEventListener('click',()=>s(d-1));x.addEventListener('click',()=>s(d+1));l.addEventListener('click',e=>{e.target===l&&o();});document.addEventListener('keydown',e=>{if(!l.classList.contains('open'))return;if(e.key==='Escape')o();if(e.key==='ArrowLeft')s(d-1);if(e.key==='ArrowRight')s(d+1);});});"""


def minify_css(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", css)
    return css.strip()


def load_font(size: int, bold: bool = False):
    for path in (
        [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf"]
        if bold
        else [r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\segoeui.ttf"]
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def create_og_image() -> None:
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), (7, 11, 22))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(7 + 18 * t)
        g = int(11 + 28 * t)
        b = int(22 + 50 * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    draw.rectangle([(0, h - 8), (w, h)], fill=(245, 197, 66))
    logo_path = BRANDING / "Logo.jpg"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        logo.thumbnail((180, 180), Image.Resampling.LANCZOS)
        img.paste(logo, (80, 80), logo)

    title_font = load_font(56, bold=True)
    sub_font = load_font(28)
    tag_font = load_font(22, bold=True)
    draw.text((300, 110), "NOVA BORWERK", fill=(255, 217, 112), font=title_font)
    draw.text((300, 190), "Mobil Yerinde İşleme · Kompresör Servisi", fill=(238, 243, 255), font=sub_font)
    draw.text((300, 250), "Avcılar / İstanbul · Marmara Bölgesi", fill=(184, 194, 223), font=sub_font)
    draw.rounded_rectangle([(300, 320), (620, 380)], radius=20, fill=(245, 197, 66))
    draw.text((330, 338), "GAP Kompresör & Tools", fill=(21, 26, 40), font=tag_font)
    draw.text((80, h - 70), "novaborwerk.com", fill=(184, 194, 223), font=tag_font)

    out = BRANDING / "og-share.jpg"
    img.save(out, format="JPEG", quality=88, optimize=True)
    print(f"Created {out}")


def extract_site_css() -> None:
    index = SITE_ROOT / "index.html"
    text = index.read_text(encoding="utf-8")
    CSS_DIR.mkdir(parents=True, exist_ok=True)

    if "<style>" in text:
        start = text.index("<style>") + len("<style>")
        end = text.index("</style>")
        css = text[start:end] + FAQ_CSS
        (CSS_DIR / "site.css").write_text(minify_css(css), encoding="utf-8")
        link_block = (
            '  <link rel="preload" href="assets/css/site.css" as="style" />\n'
            '  <link rel="stylesheet" href="assets/css/site.css" />\n'
        )
        text = text[: start - len("<style>")] + link_block + text[end + len("</style>") :]
        index.write_text(text, encoding="utf-8")
        print("Updated index.html to use external CSS")
    elif not (CSS_DIR / "site.css").exists():
        raise FileNotFoundError("index.html has no <style> block and assets/css/site.css is missing")

    (CSS_DIR / "urunler.css").write_text(minify_css(URUNLER_CSS), encoding="utf-8")


def write_js() -> None:
    JS_DIR.mkdir(parents=True, exist_ok=True)
    (JS_DIR / "site.js").write_text(MOBILE_NAV_JS, encoding="utf-8")
    (JS_DIR / "lightbox.js").write_text(LIGHTBOX_JS, encoding="utf-8")


def patch_index_for_assets() -> None:
    index = SITE_ROOT / "index.html"
    text = index.read_text(encoding="utf-8")
    og = "https://novaborwerk.com/assets/branding/og-share.jpg"
    text = text.replace("https://novaborwerk.com/assets/branding/Logo.jpg", og)
    if 'src="assets/js/site.js"' not in text:
        text = re.sub(
            r"\s*<script>\s*document\.addEventListener\('DOMContentLoaded'.*?}\);\s*}\);\s*</script>\s*</body>",
            '\n  <script src="assets/js/site.js" defer></script>\n</body>',
            text,
            flags=re.S,
        )
    index.write_text(text, encoding="utf-8")


def main() -> None:
    extract_site_css()
    write_js()
    create_og_image()
    patch_index_for_assets()
    print("Site assets built.")


if __name__ == "__main__":
    main()
