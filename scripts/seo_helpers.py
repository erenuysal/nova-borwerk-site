"""SEO helpers: meta tags, JSON-LD, sitemap, robots.txt."""
import html
import json
from datetime import date
from pathlib import Path

SITE_URL = "https://novaborwerk.com"
SITE_NAME = "Nova Borwerk"
DEFAULT_OG_IMAGE = f"{SITE_URL}/assets/branding/og-share.jpg"

FAQ_ITEMS: list[tuple[str, str]] = [
    (
        "Pistonlu kompresör bakımı nasıl yapılır?",
        "Her kullanım sonrası depo altındaki kondens vanasını boşaltın. Haftalık yağ seviyesini kontrol edin; "
        "filtre tıkanıklığı varsa temizleyin veya değiştirin. 500–1000 saatte yağ değişimi, yılda bir emniyet "
        "supabı kontrolü önerilir. Nova Borwerk Marmara Bölgesi'nde yerinde bakım ve servis sunar.",
    ),
    (
        "Vidalı kompresör mü pistonlu kompresör mü tercih edilmeli?",
        "Sürekli ve yüksek hava tüketiminde vidalı kompresörler (GPV serisi) daha verimli ve sessizdir. "
        "Ara ara kullanım, küçük atölyeler ve düşük bütçede pistonlu GP modelleri yeterli olur.",
    ),
    (
        "Kompresör basıncı düşükse ne yapmalıyım?",
        "Hava kaçağı, kirli filtre, yanlış basınç ayarı veya aşınmış piston/sekman basıncı düşürür. "
        "Önce filtre ve kondens hattını kontrol edin; sorun devam ederse servis çağırın.",
    ),
    (
        "Hava kurutucu neden gerekli?",
        "Basınçlı hava hattındaki nem, boya hatlarında su damlası, pnömatik aletlerde korozyon ve "
        "filtre tıkanmasına yol açar. GPDK / GPAC kurutucular nem oranını düşürerek hat kalitesini korur.",
    ),
    (
        "Nova Borwerk hangi bölgelere servis veriyor?",
        "Merkez Avcılar / İstanbul olmak üzere İstanbul, Kocaeli, Bursa, Tekirdağ, Yalova, Sakarya, "
        "Balıkesir, Çanakkale, Edirne, Kırklareli ve Bilecik illerini kapsayan Marmara Bölgesi'ne mobil servis veriyoruz.",
    ),
    (
        "Kompresör yağı ne sıklıkla değiştirilmeli?",
        "Kullanım yoğunluğuna göre 500–1000 çalışma saatinde bir yağ değişimi önerilir. "
        "Yağ rengi koyulaştıysa veya emülsiyon oluştuysa vakit beklemeden değiştirin.",
    ),
    (
        "Ürün teklifi nasıl alabilirim?",
        "WhatsApp (+90 536 712 82 57), telefon veya novaborwerk@gmail.com üzerinden model adını "
        "ve kullanım amacınızı iletmeniz yeterli; teknik ekibimiz aynı gün dönüş yapar.",
    ),
    (
        "Seyyar borwerk (yerinde delik işleme) hizmeti veriyor musunuz?",
        "Evet. Kalıp, makine ve ağır ekipmanlarda mobil borwerk ile yerinde delik işleme, "
        "pim-burç revizyonu ve dolgu kaynağı hizmetleri sunuyoruz.",
    ),
]
PHONE = "+905367128257"
EMAIL = "novaborwerk@gmail.com"


def page_url(path: str) -> str:
    path = path.replace("\\", "/").lstrip("/")
    return f"{SITE_URL}/{path}" if path else f"{SITE_URL}/"


def seo_head_block(
    title: str,
    description: str,
    canonical_path: str,
    prefix: str = "",
    og_type: str = "website",
    og_image: str | None = None,
    json_ld: dict | list | None = None,
) -> str:
    full_title = title if "|" in title else f"{title} | {SITE_NAME}"
    url = page_url(canonical_path)
    image = og_image or DEFAULT_OG_IMAGE
    desc = html.escape(description.strip())
    esc_title = html.escape(full_title)

    lines = [
        f"  <title>{esc_title}</title>",
        f'  <meta name="description" content="{desc}" />',
        f'  <link rel="canonical" href="{html.escape(url)}" />',
        f'  <meta property="og:title" content="{esc_title}" />',
        f'  <meta property="og:description" content="{desc}" />',
        f'  <meta property="og:url" content="{html.escape(url)}" />',
        f'  <meta property="og:type" content="{og_type}" />',
        f'  <meta property="og:locale" content="tr_TR" />',
        f'  <meta property="og:site_name" content="{SITE_NAME}" />',
        f'  <meta property="og:image" content="{html.escape(image)}" />',
        f'  <meta name="twitter:card" content="summary_large_image" />',
        f'  <meta name="twitter:title" content="{esc_title}" />',
        f'  <meta name="twitter:description" content="{desc}" />',
        f'  <meta name="twitter:image" content="{html.escape(image)}" />',
        f'  <meta name="robots" content="index, follow, max-image-preview:large" />',
        f'  <link rel="icon" type="image/png" href="{prefix}assets/branding/favicon.png" />',
        f'  <link rel="apple-touch-icon" href="{prefix}assets/branding/favicon.png" />',
    ]

    if json_ld:
        payload = json_ld if isinstance(json_ld, list) else [json_ld]
        script = json.dumps(payload, ensure_ascii=False, indent=2)
        lines.append(f'  <script type="application/ld+json">\n{script}\n  </script>')

    return "\n".join(lines)


def local_business_schema() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": SITE_NAME,
        "url": page_url(""),
        "logo": DEFAULT_OG_IMAGE,
        "image": DEFAULT_OG_IMAGE,
        "description": "Seyyar borwerk, yerinde delik işleme, kompresör bakım ve Marmara Bölgesi mobil teknik servis.",
        "telephone": PHONE,
        "email": EMAIL,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Avcılar",
            "addressRegion": "İstanbul",
            "addressCountry": "TR",
        },
        "areaServed": {
            "@type": "AdministrativeArea",
            "name": "Marmara Bölgesi",
        },
        "priceRange": "$$",
        "sameAs": ["https://wa.me/905367128257"],
    }


def website_schema() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": page_url(""),
        "inLanguage": "tr-TR",
        "potentialAction": {
            "@type": "SearchAction",
            "target": page_url("urunler.html") + "?q={search_term_string}",
            "query-input": "required name=search_term_string",
        },
    }


def breadcrumb_schema(items: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": idx + 1,
                "name": name,
                "item": page_url(path),
            }
            for idx, (name, path) in enumerate(items)
        ],
    }


def product_page_path(category_id: str, product_id: str) -> str:
    return f"urunler/{category_id}/{product_id}.html"


def item_list_schema(category: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": category["name"],
        "description": category.get("description", ""),
        "numberOfItems": len(category.get("products", [])),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": idx + 1,
                "name": product["title"],
                "url": page_url(product_page_path(category["id"], product["id"])),
            }
            for idx, product in enumerate(category.get("products", []))
        ],
    }


def product_schema(category: dict, product: dict) -> dict:
    images = [page_url(image) for image in product.get("images", [])[:5]]
    if not images and product.get("thumb"):
        images = [page_url(product["thumb"])]
    schema: dict = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product["title"],
        "description": category.get("description", ""),
        "url": page_url(product_page_path(category["id"], product["id"])),
        "image": images,
        "brand": {"@type": "Brand", "name": "GAP"},
        "category": category["name"],
        "offers": {
            "@type": "Offer",
            "url": page_url(product_page_path(category["id"], product["id"])),
            "priceCurrency": "TRY",
            "availability": "https://schema.org/InStock",
            "seller": {"@type": "Organization", "name": SITE_NAME},
        },
    }
    if product.get("model"):
        schema["model"] = product["model"]
        schema["sku"] = product["model"]
    return schema


def faq_schema() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
            for question, answer in FAQ_ITEMS
        ],
    }


def category_collection_schema(category: dict) -> dict:
    cover = category.get("cover") or ""
    image = page_url(cover) if cover else DEFAULT_OG_IMAGE
    return {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": category["name"],
        "description": category.get("description", ""),
        "url": page_url(f"urunler/{category['id']}.html"),
        "image": image,
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": page_url("")},
    }


def products_overview_schema(catalog: dict) -> dict:
    categories = [c for c in catalog.get("categories", []) if c.get("products")]
    return {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Ürün Kategorileri",
        "description": "GAP Kompresör ve GAP Tools ürün kataloğu.",
        "url": page_url("urunler.html"),
        "hasPart": [
            {
                "@type": "CollectionPage",
                "name": cat["name"],
                "url": page_url(f"urunler/{cat['id']}.html"),
            }
            for cat in categories
        ],
    }


def generate_robots(site_root: Path) -> None:
    content = f"""User-agent: *
Allow: /

Sitemap: {page_url("sitemap.xml")}
"""
    (site_root / "robots.txt").write_text(content, encoding="utf-8")


def generate_sitemap(site_root: Path, catalog: dict) -> None:
    today = date.today().isoformat()
    urls = [
        ("", "weekly", "1.0"),
        ("sss.html", "monthly", "0.7"),
        ("urunler.html", "weekly", "0.9"),
    ]
    for category in catalog.get("categories", []):
        if not category.get("products"):
            continue
        urls.append((f"urunler/{category['id']}.html", "weekly", "0.8"))
        for product in category["products"]:
            urls.append((product_page_path(category["id"], product["id"]), "monthly", "0.7"))

    entries = []
    for path, freq, priority in urls:
        loc = page_url(path)
        entries.append(
            f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>"""
        )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(entries)}
</urlset>
"""
    (site_root / "sitemap.xml").write_text(xml, encoding="utf-8")
