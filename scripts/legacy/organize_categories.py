import shutil
from pathlib import Path

BASE = Path(r"C:\Users\hmzis\Desktop\eren dosya")
SOURCE_PAGES = BASE / "sayfalar"
LOCAL_CATEGORIES = BASE / "urun-kategoriler"
SITE_ROOT = BASE / "nova-borwerk-site-main"
SITE_ASSETS = SITE_ROOT / "assets" / "urunler"

CATEGORIES = [
    {
        "id": "kapak-genel",
        "name": "Kapak ve Genel",
        "description": "Katalog kapak sayfası, ödeme bilgileri ve firma tanıtımı.",
        "pages": [1, 2, 3],
        "show_on_site": False,
    },
    {
        "id": "pistonlu-hava-kompresorleri",
        "name": "Pistonlu Hava Kompresörleri",
        "description": "GP serisi yağlı pistonlu hava kompresörleri ve teknik özellikleri.",
        "pages": list(range(4, 10)),
        "show_on_site": True,
    },
    {
        "id": "sessiz-ve-yagsiz-hava-kompresorleri",
        "name": "Sessiz ve Yağsız Hava Kompresörleri",
        "description": "GPS serisi sessiz ve yağsız hava kompresör modelleri.",
        "pages": list(range(10, 16)),
        "show_on_site": True,
    },
    {
        "id": "yuksek-emisli-yagsiz-kompresorler",
        "name": "Yüksek Emişli Yağsız Kompresörler",
        "description": "GPY serisi yüksek emişli yağsız kompresör çözümleri.",
        "pages": list(range(16, 26)),
        "show_on_site": True,
    },
    {
        "id": "vidali-hava-kompresorleri",
        "name": "Vidalı Hava Kompresörleri",
        "description": "GPV serisi vidalı, invertörlü ve depo üstü kompresör sistemleri.",
        "pages": list(range(26, 49)),
        "show_on_site": True,
    },
    {
        "id": "hava-kurutucu-ve-filtreler",
        "name": "Hava Kurutucu ve Filtreler",
        "description": "Hava kurutucular, su tutucu filtreler, kimyasal kurutucu ve aktif karbon kuleleri.",
        "pages": list(range(49, 52)),
        "show_on_site": True,
    },
    {
        "id": "arac-kaldirma-liftleri",
        "name": "Araç Kaldırma Liftleri",
        "description": "İki sütunlu liftler, makaslı liftler ve oto servis kaldırma sistemleri.",
        "pages": list(range(52, 60)),
        "show_on_site": True,
    },
    {
        "id": "oto-servis-ekipmanlari",
        "name": "Oto Servis Ekipmanları",
        "description": "Vinç, kriko, motor standı, şanzıman krikosu, pres ve servis aparatları.",
        "pages": list(range(60, 68)),
        "show_on_site": True,
    },
    {
        "id": "yaglama-ve-yikama",
        "name": "Yağlama Ekipmanları ve Yıkama Makineleri",
        "description": "Gres pompaları, yağ boşaltma üniteleri ve basınçlı yıkama makineleri.",
        "pages": list(range(68, 74)),
        "show_on_site": True,
    },
    {
        "id": "sarjli-ve-havali-el-aletleri",
        "name": "Şarjlı ve Havalı El Aletleri",
        "description": "Darbeli somun sökme, cırcır, zımpara, hava tabancası ve şarjlı el aletleri.",
        "pages": list(range(74, 81)),
        "show_on_site": True,
    },
    {
        "id": "vinc-ve-kaldırma-ekipmanlari",
        "name": "Vinç ve Kaldırma Ekipmanları",
        "description": "Elektrikli vinç, caraskal, hubzug ve transpalet modelleri.",
        "pages": list(range(81, 84)),
        "show_on_site": True,
    },
    {
        "id": "kaynak-ve-kaporta-cektirme",
        "name": "Kaynak ve Kaporta Çektirme Makineleri",
        "description": "İnvertörlü kaynak makineleri, kaporta çektirme üniteleri ve göçük düzeltme aparatları.",
        "pages": list(range(84, 90)),
        "show_on_site": True,
    },
    {
        "id": "takim-arabalari-ve-tezgahlari",
        "name": "Takım Arabaları ve Tezgahları",
        "description": "Çekmeceli takım arabaları ve endüstriyel çalışma tezgahları.",
        "pages": list(range(90, 95)),
        "show_on_site": True,
    },
    {
        "id": "kurumsal-ve-servis",
        "name": "Kurumsal ve Servis Bilgileri",
        "description": "Servis listesi, fabrika görselleri ve katalog ek sayfaları.",
        "pages": list(range(95, 101)),
        "show_on_site": False,
    },
]


def copy_category_pages(category, target_root):
    target_dir = target_root / category["id"]
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    for page_num in category["pages"]:
        src = SOURCE_PAGES / f"{page_num}.png"
        if not src.exists():
            print(f"Missing: {src}")
            continue
        dst_name = f"sayfa-{page_num:03d}.png"
        shutil.copy2(src, target_dir / dst_name)
        copied.append(page_num)
    return copied


def main():
    if not SOURCE_PAGES.exists():
        raise SystemExit(f"Source folder not found: {SOURCE_PAGES}")

    for root in (LOCAL_CATEGORIES, SITE_ASSETS):
        if root.exists():
            shutil.rmtree(root)
        root.mkdir(parents=True, exist_ok=True)

    summary = []
    for category in CATEGORIES:
        local_count = len(copy_category_pages(category, LOCAL_CATEGORIES))
        site_count = len(copy_category_pages(category, SITE_ASSETS))
        summary.append((category["name"], local_count, site_count))

    print("Category organization complete")
    for name, local_count, site_count in summary:
        print(f"  {name}: {local_count} pages")


if __name__ == "__main__":
    main()
