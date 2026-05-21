"""Generate urunler.html, category pages, product detail pages, and SSS from catalog.json."""
import html
import json
from pathlib import Path

from seo_helpers import (
    FAQ_ITEMS,
    breadcrumb_schema,
    category_collection_schema,
    faq_schema,
    generate_robots,
    generate_sitemap,
    item_list_schema,
    local_business_schema,
    page_url,
    product_page_path,
    product_schema,
    products_overview_schema,
    seo_head_block,
    website_schema,
)

from _paths import CATALOG_PATH, SITE_ROOT

URUNLER_DESCRIPTION = (
    "GAP Kompresör ve GAP Tools ürün kataloğu: pistonlu ve vidalı kompresör, "
    "oto servis ekipmanları, lift, vinç, hava kurutucu ve filtre modelleri. "
    "Nova Borwerk — İstanbul Avcılar merkezli satış ve teknik destek."
)

SSS_DESCRIPTION = (
    "Kompresör bakımı, vidalı ve pistonlu kompresör seçimi, hava kurutucu, "
    "servis bölgeleri ve teklif süreci hakkında sık sorulan sorular. Nova Borwerk SSS."
)


def css_links(prefix: str) -> str:
    return (
        f'  <link rel="preload" href="{prefix}assets/css/site.css" as="style" />\n'
        f'  <link rel="stylesheet" href="{prefix}assets/css/site.css" />\n'
        f'  <link rel="stylesheet" href="{prefix}assets/css/urunler.css" />\n'
    )


def js_links(prefix: str, include_lightbox: bool = False) -> str:
    scripts = [f'  <script src="{prefix}assets/js/site.js" defer></script>']
    if include_lightbox:
        scripts.append(f'  <script src="{prefix}assets/js/lightbox.js" defer></script>')
    return "\n".join(scripts)


def nav_html(active: str = "", prefix: str = "") -> str:
    items = [
        (f"{prefix}index.html#hakkimizda", "Hakkımızda", "hakkimizda"),
        (f"{prefix}urunler.html", "Ürünler", "urunler"),
        (f"{prefix}index.html#hizmetler", "Hizmetler", "hizmetler"),
        (f"{prefix}index.html#kompresor", "Kompresör", "kompresor"),
        (f"{prefix}sss.html", "SSS", "sss"),
        (f"{prefix}index.html#belgeler", "Belgeler", "belgeler"),
        (f"{prefix}index.html#galeri", "Uygulamalar", "galeri"),
        (f"{prefix}index.html#marmara", "Hizmet Ağı", "marmara"),
        (f"{prefix}index.html#referanslar", "Referanslar", "referanslar"),
        (f"{prefix}index.html#iletisim", "İletişim", "iletisim"),
    ]
    return "\n".join(
        f'        <a href="{href}"{" class=\"active\"" if key == active else ""}>{label}</a>'
        for href, label, key in items
    )


def shell(
    title: str,
    description: str,
    body: str,
    active_nav: str = "",
    prefix: str = "",
    canonical_path: str = "",
    og_type: str = "website",
    og_image: str | None = None,
    json_ld: dict | list | None = None,
    include_lightbox: bool = False,
) -> str:
    seo = seo_head_block(
        title=title,
        description=description,
        canonical_path=canonical_path,
        prefix=prefix,
        og_type=og_type,
        og_image=og_image,
        json_ld=json_ld,
    )
    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
{seo}
{css_links(prefix)}
</head>
<body>
  <header class="topbar">
    <div class="container topbar-inner">
      <a href="{prefix}index.html#anasayfa" class="brand">
        <div class="brand-logo"><img src="{prefix}assets/branding/Logo.jpg" alt="Nova Borwerk Logo" /></div>
        <div>
          <strong><span>NOVA</span> BORWERK</strong>
          <small>Mobil Teknik Çözümler</small>
        </div>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Menüyü aç">Menü</button>
      <nav id="site-nav">
{nav_html(active_nav, prefix)}
      </nav>
    </div>
  </header>
  <main>
{body}
  </main>
  <div id="lightbox" class="lightbox" aria-hidden="true">
    <button class="lightbox-close" type="button" aria-label="Kapat">×</button>
    <button class="lightbox-nav prev" type="button" aria-label="Önceki">‹</button>
    <img src="" alt="" />
    <button class="lightbox-nav next" type="button" aria-label="Sonraki">›</button>
  </div>
  <a class="float-wa" href="https://wa.me/905367128257" target="_blank" rel="noopener">WhatsApp İletişim</a>
  <footer>
    <div class="container footer-inner">
      <div>
        <strong style="color:var(--text)"><span style="color:var(--gold)">NOVA</span> BORWERK</strong><br>
        Mobil Teknik Çözümler · Avcılar / İstanbul · Tüm Marmara Bölgesi Servis
      </div>
      <div>© 2026 Nova Borwerk. Tüm hakları saklıdır.</div>
    </div>
  </footer>
{js_links(prefix, include_lightbox=include_lightbox)}
</body>
</html>
"""


def render_faq_html() -> str:
    items = []
    for question, answer in FAQ_ITEMS:
        items.append(
            f"""
        <details class="faq-item">
          <summary>{html.escape(question)}</summary>
          <div class="faq-body"><p>{html.escape(answer)}</p></div>
        </details>"""
        )
    return f'<div class="faq-list">{"".join(items)}</div>'


def render_specs_table(specs: dict) -> str:
    rows = [
        f"<tr><th>{html.escape(label)}</th><td>{html.escape(value)}</td></tr>"
        for label, value in specs.items()
        if value
    ]
    if not rows:
        return ""
    return f'<table class="spec-table"><tbody>{"".join(rows)}</tbody></table>'


def render_product_item(product: dict, category_id: str, prefix: str = "../") -> str:
    detail_href = f"{category_id}/{product['id']}.html"
    features = "".join(f"<li>{html.escape(item)}</li>" for item in product["features"])
    features_html = f'<ul class="feature-list">{features}</ul>' if features else ""
    model_html = (
        f'<span class="product-model">{html.escape(product["model"])}</span>'
        if product.get("model")
        else ""
    )
    specs_html = render_specs_table(product.get("specs", {}))
    return f"""
      <article class="product-item">
        <a class="product-thumb-wrap" href="{html.escape(detail_href)}">
          <img src="{html.escape(prefix + product['thumb'])}" alt="{html.escape(product['title'])}" loading="lazy" />
        </a>
        <div class="product-body">
          <h3><a href="{html.escape(detail_href)}">{html.escape(product['title'])}</a></h3>
          {model_html}
          {features_html}
          {specs_html}
          <a class="detail-link" href="{html.escape(detail_href)}">Detaylı incele →</a>
        </div>
      </article>
    """


def product_description(category: dict, product: dict) -> str:
    model = product.get("model") or ""
    specs = product.get("specs", {})
    bits = [product["title"]]
    if model:
        bits.append(f"Model: {model}")
    for key in ("Güç", "Basınç", "Depo Hacmi", "Hava Emişi"):
        if specs.get(key):
            bits.append(f"{key}: {specs[key]}")
    bits.append(f"{category['name']} — teklif ve teknik destek için Nova Borwerk.")
    return " ".join(bits)


def render_product_detail(
    category: dict,
    product: dict,
    prefix: str = "../../",
) -> str:
    gallery = "|".join(prefix + image for image in product["images"])
    features = "".join(f"<li>{html.escape(item)}</li>" for item in product["features"])
    features_html = f'<ul class="feature-list">{features}</ul>' if features else ""
    model_html = (
        f'<span class="product-model">{html.escape(product["model"])}</span>'
        if product.get("model")
        else ""
    )
    specs_html = render_specs_table(product.get("specs", {}))
    thumbs = []
    for idx, image in enumerate(product["images"]):
        thumbs.append(
            f'<button type="button" data-gallery="{html.escape(gallery)}" data-index="{idx}" aria-label="Görsel {idx + 1}">'
            f'<img src="{html.escape(prefix + image)}" alt="" loading="lazy" /></button>'
        )
    main_image = prefix + product["images"][0]
    return f"""
    <section class="hero">
      <div class="container">
        <div class="breadcrumb">
          <a href="{prefix}urunler.html">Ürünler</a> /
          <a href="../{html.escape(category['id'])}.html">{html.escape(category['name'])}</a> /
          {html.escape(product.get('model') or product['title'])}
        </div>
        <div class="product-detail-grid">
          <div>
            <div class="product-detail-gallery">
              <button type="button" data-gallery="{html.escape(gallery)}" data-index="0" aria-label="Görseli büyüt" style="border:none;padding:0;background:#fff;width:100%;cursor:zoom-in;">
                <img src="{html.escape(main_image)}" alt="{html.escape(product['title'])}" />
              </button>
            </div>
            <div class="product-detail-thumbs">{''.join(thumbs)}</div>
          </div>
          <div class="product-detail-body">
            <div class="eyebrow">{html.escape(category['name'])}</div>
            <h1>{html.escape(product['title'])}</h1>
            {model_html}
            {features_html}
            {specs_html}
            <div class="cta-row">
              <a class="btn primary" href="{prefix}index.html#iletisim">Teklif / Bilgi Al</a>
              <a class="btn whatsapp" href="https://wa.me/905367128257" target="_blank" rel="noopener">WhatsApp'tan Yaz</a>
              <a class="btn secondary" href="../{html.escape(category['id'])}.html">Kategoriye Dön</a>
            </div>
          </div>
        </div>
      </div>
    </section>
    """


def generate_main_page(catalog: dict) -> None:
    cards = []
    for category in catalog["categories"]:
        if not category.get("products"):
            continue
        cover = category.get("cover") or category["products"][0]["thumb"]
        cards.append(
            f"""
        <a class="category-card" href="urunler/{html.escape(category['id'])}.html">
          <img src="{html.escape(cover)}" alt="{html.escape(category['name'])}" loading="lazy" />
          <div class="category-card-body">
            <h3>{html.escape(category['name'])}</h3>
            <p>{html.escape(category['description'])}</p>
            <span class="tag-count">{len(category['products'])} ürün</span>
          </div>
        </a>"""
        )

    body = f"""
    <section class="hero">
      <div class="container">
        <div class="section-head">
          <div class="eyebrow">GAP Kompresör & GAP Tools</div>
          <h1>Ürün <span class="hl">kategorileri</span></h1>
          <p>
            Kompresörlerden oto servis ekipmanlarına kadar tüm ürün gruplarımızı kategori kategori inceleyebilir,
            her model için ayrı teknik özellik sayfalarına ulaşabilirsiniz.
          </p>
          <div class="cta-row">
            <a class="btn primary" href="index.html#iletisim">Teklif / Bilgi Al</a>
            <a class="btn whatsapp" href="https://wa.me/905367128257" target="_blank" rel="noopener">WhatsApp'tan Yaz</a>
          </div>
        </div>
        <div class="category-grid">
          {''.join(cards)}
        </div>
      </div>
    </section>
    """
    (SITE_ROOT / "urunler.html").write_text(
        shell(
            "Ürünler",
            URUNLER_DESCRIPTION,
            body,
            active_nav="urunler",
            canonical_path="urunler.html",
            json_ld=[
                products_overview_schema(catalog),
                breadcrumb_schema([("Ana Sayfa", "index.html"), ("Ürünler", "urunler.html")]),
            ],
        ),
        encoding="utf-8",
    )


def generate_category_pages(catalog: dict) -> None:
    out_dir = SITE_ROOT / "urunler"
    out_dir.mkdir(exist_ok=True)

    for category in catalog["categories"]:
        if not category.get("products"):
            continue
        items = "".join(
            render_product_item(product, category["id"]) for product in category["products"]
        )
        body = f"""
    <section class="hero">
      <div class="container">
        <div class="breadcrumb"><a href="../urunler.html">Ürünler</a> / {html.escape(category['name'])}</div>
        <div class="section-head">
          <div class="eyebrow">Ürün kategorisi</div>
          <h1>{html.escape(category['name'])}</h1>
          <p>{html.escape(category['description'])}</p>
          <div class="cta-row">
            <a class="btn primary" href="../index.html#iletisim">Teklif / Bilgi Al</a>
            <a class="btn secondary" href="../urunler.html">Tüm Kategoriler</a>
          </div>
        </div>
        <div class="product-list">
          {items}
        </div>
      </div>
    </section>
        """
        cat_desc = (
            f"{category['description']} "
            f"{len(category['products'])} model listeleniyor. "
            "Teklif ve teknik bilgi için Nova Borwerk ile iletişime geçin."
        )
        cover = category.get("cover")
        og_image = page_url(cover) if cover else None
        json_ld = [
            category_collection_schema(category),
            item_list_schema(category),
            breadcrumb_schema([
                ("Ana Sayfa", "index.html"),
                ("Ürünler", "urunler.html"),
                (category["name"], f"urunler/{category['id']}.html"),
            ]),
        ]
        (out_dir / f"{category['id']}.html").write_text(
            shell(
                category["name"],
                cat_desc,
                body,
                active_nav="urunler",
                prefix="../",
                canonical_path=f"urunler/{category['id']}.html",
                og_image=og_image,
                json_ld=json_ld,
                include_lightbox=False,
            ),
            encoding="utf-8",
        )


def generate_product_pages(catalog: dict) -> int:
    count = 0
    for category in catalog["categories"]:
        if not category.get("products"):
            continue
        cat_dir = SITE_ROOT / "urunler" / category["id"]
        cat_dir.mkdir(parents=True, exist_ok=True)
        for product in category["products"]:
            body = render_product_detail(category, product)
            desc = product_description(category, product)
            og_image = page_url(product["images"][0]) if product.get("images") else None
            canonical = product_page_path(category["id"], product["id"])
            json_ld = [
                product_schema(category, product),
                breadcrumb_schema([
                    ("Ana Sayfa", "index.html"),
                    ("Ürünler", "urunler.html"),
                    (category["name"], f"urunler/{category['id']}.html"),
                    (product.get("model") or product["title"], canonical),
                ]),
            ]
            (cat_dir / f"{product['id']}.html").write_text(
                shell(
                    product["title"],
                    desc,
                    body,
                    active_nav="urunler",
                    prefix="../../",
                    canonical_path=canonical,
                    og_type="product",
                    og_image=og_image,
                    json_ld=json_ld,
                    include_lightbox=True,
                ),
                encoding="utf-8",
            )
            count += 1
    return count


def generate_sss_page() -> None:
    body = f"""
    <section class="hero">
      <div class="container">
        <div class="section-head">
          <div class="eyebrow">Bilgi merkezi</div>
          <h1>Sık Sorulan <span class="hl">Sorular</span></h1>
          <p>
            Kompresör bakımı, ürün seçimi, servis bölgeleri ve teklif süreci hakkında
            en çok sorulan soruların yanıtları.
          </p>
        </div>
        {render_faq_html()}
        <div class="cta-row" style="margin-top:28px;">
          <a class="btn primary" href="index.html#iletisim">İletişime Geç</a>
          <a class="btn secondary" href="urunler.html">Ürün Kataloğu</a>
        </div>
      </div>
    </section>
    """
    (SITE_ROOT / "sss.html").write_text(
        shell(
            "SSS — Sık Sorulan Sorular",
            SSS_DESCRIPTION,
            body,
            active_nav="sss",
            canonical_path="sss.html",
            json_ld=[
                faq_schema(),
                breadcrumb_schema([("Ana Sayfa", "index.html"), ("SSS", "sss.html")]),
            ],
        ),
        encoding="utf-8",
    )


def patch_index_faq_and_nav() -> None:
    index_path = SITE_ROOT / "index.html"
    text = index_path.read_text(encoding="utf-8")
    og = "https://novaborwerk.com/assets/branding/og-share.jpg"
    text = text.replace("https://novaborwerk.com/assets/branding/Logo.jpg", og)

    if 'href="sss.html"' not in text:
        text = text.replace(
            '<a href="#referanslar">Referanslar</a>',
            '<a href="sss.html">SSS</a>\n        <a href="#referanslar">Referanslar</a>',
        )

    if 'id="sss"' not in text:
        faq_section = f"""
    <section class="section" id="sss">
      <div class="container">
        <div class="section-head">
          <div class="eyebrow">SSS</div>
          <h2>Kompresör bakımı ve servis hakkında</h2>
          <p>Organik aramalarda en çok sorulan konuların kısa yanıtları. Tüm sorular için <a href="sss.html" style="color:var(--gold-2)">SSS sayfasına</a> bakın.</p>
        </div>
        {render_faq_html()}
      </div>
    </section>

"""
        text = text.replace('    <section class="section" id="iletisim">', faq_section + '    <section class="section" id="iletisim">')

    if '"@type": "FAQPage"' not in text:
        faq_ld = json.dumps(faq_schema(), ensure_ascii=False, indent=4)
        marker = '  <link rel="stylesheet" href="assets/css/site.css" />'
        if marker in text:
            text = text.replace(
                marker,
                f'  <script type="application/ld+json">\n{faq_ld}\n  </script>\n{marker}',
                1,
            )
        else:
            text = text.replace(
                "</head>",
                f'  <script type="application/ld+json">\n{faq_ld}\n  </script>\n</head>',
                1,
            )

    index_path.write_text(text, encoding="utf-8")


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    generate_main_page(catalog)
    generate_category_pages(catalog)
    product_count = generate_product_pages(catalog)
    generate_sss_page()
    patch_index_faq_and_nav()
    generate_robots(SITE_ROOT)
    generate_sitemap(SITE_ROOT, catalog)
    print(f"Site pages regenerated: {product_count} product detail pages")
    print("SEO: robots.txt, sitemap.xml, sss.html updated")


if __name__ == "__main__":
    main()
