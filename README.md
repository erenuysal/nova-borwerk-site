# Nova Borwerk — Web Sitesi

Statik kurumsal site: mobil borwerk hizmetleri, kompresör servisi ve GAP ürün kataloğu.  
Canlı adres: **https://novaborwerk.com**

---

## Klasör yapısı

```
.
├── index.html              # Ana sayfa
├── urunler.html            # Ürün kategorileri listesi
├── sss.html                # Sık sorulan sorular
├── seyyar-borwerk.html     # Seyyar borwerk tanıtım (eski sayfa)
├── robots.txt              # Arama motoru yönergeleri
├── sitemap.xml             # 147 URL (Google Search Console'a ekleyin)
│
├── assets/
│   ├── branding/           # Logo, favicon, OG paylaşım görseli (1200×630)
│   ├── css/                # site.css + urunler.css (sıkıştırılmış)
│   ├── js/                 # site.js (menü) + lightbox.js (ürün galerisi)
│   ├── galeri/             # Uygulama fotoğrafları
│   ├── kompresor/          # Kompresör servis görselleri
│   ├── referanslar/        # Müşteri logoları
│   ├── belgeler/           # Sertifika / belge görselleri
│   ├── harita/             # Marmara hizmet alanı SVG haritası
│   └── urunler/
│       ├── catalog.json    # 132 ürün — tek veri kaynağı
│       ├── image_sources_manifest.json  # İnternetten indirilen görsel kaynakları
│       └── {kategori-id}/  # Ürün WebP görselleri + kapak
│
├── urunler/
│   ├── {kategori-id}.html           # 12 kategori sayfası
│   └── {kategori-id}/{urun-id}.html # 132 ürün detay sayfası
│
├── scripts/                # Site oluşturma araçları (Python)
├── source/
│   └── e-katalog.pdf       # Kaynak katalog PDF (gitignore — bkz. aşağı)
├── build.py                # Tek komutla site yenileme
└── requirements.txt        # Python bağımlılıkları
```

---

## GitHub'a yükleme

```bash
git init
git add .
git commit -m "Nova Borwerk site"
git remote add origin https://github.com/KULLANICI/nova-borwerk.git
git push -u origin main
```

### GitHub Pages

1. Repo → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / **/ (root)**
4. Site birkaç dakika içinde `https://KULLANICI.github.io/nova-borwerk/` adresinde yayınlanır

Özel alan adı için DNS'te CNAME: `novaborwerk.com`

### PDF dosyası (~25 MB)

`source/e-katalog.pdf` `.gitignore`'da. Seçenekler:

- **Git LFS:** `git lfs track "source/*.pdf"`
- **Manuel:** PDF'yi repoya eklemeden yerelde tutun; sadece site dosyalarını push edin

---

## Siteyi yeniden oluşturma

```powershell
pip install -r requirements.txt
python build.py
```

Tam katalog yeniden çıkarımı (PDF'den):

```powershell
python scripts/build_product_catalog.py
python build.py
```

Ürün görsellerini GAP sitelerinden güncelleme:

```powershell
python scripts/fetch_product_images.py
python build.py
```

---

## Script'ler (`scripts/`)

| Dosya | Ne işe yarar |
|-------|----------------|
| `build_product_catalog.py` | PDF katalogdan ürün verisi + görseller → `catalog.json` |
| `generate_urunler_site.py` | HTML sayfaları, sitemap, robots, SSS |
| `build_site_assets.py` | CSS/JS çıkarımı, OG görseli |
| `fetch_product_images.py` | gapkompresor.com / gaptools.net'ten ürün fotoğrafları |
| `create_marmara_map.py` | Marmara haritası SVG üretir |
| `audit_site.py` | Kırık asset linklerini tarar |
| `seo_helpers.py` | Meta etiket, JSON-LD, sitemap yardımcıları |
| `_paths.py` | Ortak dosya yolları |
| `legacy/` | Eski tek seferlik script'ler (artık gerekmez) |

Detay: [`scripts/README.md`](scripts/README.md)

---

## SEO kontrol listesi

- [ ] Google Search Console → sitemap: `https://novaborwerk.com/sitemap.xml`
- [ ] OG görsel: `assets/branding/og-share.jpg`
- [ ] Ürün sayfaları: `/urunler/{kategori}/{urun-id}.html`

---

© 2026 Nova Borwerk
