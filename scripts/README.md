# Build script'leri

Tüm script'ler `scripts/_paths.py` üzerinden repo kökünü bulur.  
Çalıştırırken repo kökünden:

```powershell
python scripts/audit_site.py
```

## Aktif script'ler

### `build_product_catalog.py`
PDF katalog (`source/e-katalog.pdf`) sayfalarından ürün başlıkları, özellikler, teknik tablolar ve WebP görselleri çıkarır. Çıktı: `assets/urunler/catalog.json` ve kategori klasörleri.

### `generate_urunler_site.py`
`catalog.json` okuyarak şunları üretir:
- `urunler.html` + 12 kategori sayfası
- 132 ürün detay sayfası (`urunler/{kategori}/{id}.html`)
- `sss.html`, `sitemap.xml`, `robots.txt`
- Ana sayfadaki SSS bölümü ve JSON-LD güncellemesi

### `build_site_assets.py`
Ana sayfadaki inline CSS'yi `assets/css/site.css`'e taşır, `urunler.css` ve JS dosyalarını yazar, `og-share.jpg` (1200×630) üretir.

### `fetch_product_images.py`
Resmi GAP sitelerinden model eşleştirerek yüksek kaliteli ürün görselleri indirir.

```powershell
python scripts/fetch_product_images.py --dry-run
python scripts/fetch_product_images.py --categories pistonlu-hava-kompresorleri
```

### `create_marmara_map.py`
Natural Earth verisi + Shapely ile `assets/harita/marmara-siyah.svg` oluşturur.

### `audit_site.py`
Tüm HTML dosyalarındaki `src` / `href` referanslarını kontrol eder. `BROKEN_REFS 0` hedeflenir.

### `seo_helpers.py`
Canonical, Open Graph, Twitter Card, JSON-LD ve sitemap üretim yardımcıları. Doğrudan çalıştırılmaz; `generate_urunler_site.py` kullanır.

## `legacy/` klasörü

Eski geliştirme aşaması script'leri. Silinmiş klasörlere (`sayfalar/`, `e-katalog-yedek.pdf`) referans verir; yeniden çalıştırmayın.
