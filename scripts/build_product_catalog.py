"""Extract product data and images from e-katalog.pdf into assets/urunler/catalog.json."""
import json
import re
import shutil
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

from _paths import PDF_PATH, SITE_ASSETS

CATEGORIES = [
    {
        "id": "pistonlu-hava-kompresorleri",
        "name": "Pistonlu Hava Kompresörleri",
        "description": "GP serisi yağlı pistonlu hava kompresörleri; farklı depo hacmi ve güç seçenekleriyle atölye ve sanayi kullanımına uygundur.",
        "cover_page": 4,
        "product_pages": list(range(5, 10)),
    },
    {
        "id": "sessiz-ve-yagsiz-hava-kompresorleri",
        "name": "Sessiz ve Yağsız Hava Kompresörleri",
        "description": "GPS serisi sessiz ve yağsız hava kompresörleri; temiz hava gerektiren uygulamalar için idealdir.",
        "cover_page": 10,
        "product_pages": list(range(11, 16)),
    },
    {
        "id": "yuksek-emisli-yagsiz-kompresorler",
        "name": "Yüksek Emişli Yağsız Kompresörler",
        "description": "GPY serisi yüksek emişli yağsız kompresörler; yüksek debi ve verimli çalışma sunar.",
        "cover_page": 16,
        "product_pages": list(range(17, 26)),
    },
    {
        "id": "vidali-hava-kompresorleri",
        "name": "Vidalı Hava Kompresörleri",
        "description": "GPV serisi vidalı, invertörlü ve depo üstü kompresör sistemleri.",
        "cover_page": 26,
        "product_pages": list(range(27, 49)),
    },
    {
        "id": "hava-kurutucu-ve-filtreler",
        "name": "Hava Kurutucu ve Filtreler",
        "description": "Hava kurutucular, su tutucu filtreler, kimyasal kurutucu ve aktif karbon kuleleri.",
        "cover_page": None,
        "custom_cover": True,
        "product_pages": [49, 50],
    },
    {
        "id": "arac-kaldirma-liftleri",
        "name": "Araç Kaldırma Liftleri",
        "description": "İki sütunlu liftler, makaslı liftler ve oto servis kaldırma sistemleri.",
        "cover_page": 52,
        "product_pages": list(range(53, 60)),
    },
    {
        "id": "oto-servis-ekipmanlari",
        "name": "Oto Servis Ekipmanları",
        "description": "Katlanır vinç, garaj krikosu, motor standı, şanzıman krikosu, pres ve servis aparatları.",
        "cover_page": 60,
        "product_pages": list(range(61, 68)),
    },
    {
        "id": "yaglama-ve-yikama",
        "name": "Yağlama Ekipmanları ve Yıkama Makineleri",
        "description": "Gres pompaları, yağ boşaltma üniteleri ve basınçlı yıkama makineleri.",
        "cover_page": 68,
        "product_pages": list(range(69, 74)),
    },
    {
        "id": "sarjli-ve-havali-el-aletleri",
        "name": "Şarjlı ve Havalı El Aletleri",
        "description": "Darbeli somun sökme, cırcır, zımpara, hava tabancası ve şarjlı el aletleri.",
        "cover_page": 74,
        "product_pages": list(range(75, 81)),
    },
    {
        "id": "vinc-ve-kaldırma-ekipmanlari",
        "name": "Vinç ve Kaldırma Ekipmanları",
        "description": "Elektrikli vinç, caraskal, hubzug ve transpalet modelleri.",
        "cover_page": 81,
        "product_pages": list(range(82, 84)),
    },
    {
        "id": "kaynak-ve-kaporta-cektirme",
        "name": "Kaynak ve Kaporta Çektirme Makineleri",
        "description": "İnvertörlü kaynak makineleri, kaporta çektirme üniteleri ve göçük düzeltme aparatları.",
        "cover_page": 84,
        "product_pages": list(range(85, 90)),
    },
    {
        "id": "takim-arabalari-ve-tezgahlari",
        "name": "Takım Arabaları ve Tezgahları",
        "description": "Çekmeceli takım arabaları ve endüstriyel çalışma tezgahları.",
        "cover_page": 90,
        "product_pages": list(range(91, 95)),
    },
]

GPF_FILTER_SPECS = {
    "GPF 1800": {
        "Bağlantı": "3/4\"",
        "Gövde": "Döküm",
        "Tip": "Su Tutucu Filtre",
        "Max. Basınç": "16 Bar",
    },
    "GPF 2600": {
        "Bağlantı": "1\"",
        "Gövde": "Döküm",
        "Tip": "Su Tutucu Filtre",
        "Max. Basınç": "16 Bar",
    },
    "GPF 3700": {
        "Bağlantı": "1-1/2\"",
        "Gövde": "Döküm",
        "Tip": "Su Tutucu Filtre",
        "Max. Basınç": "16 Bar",
    },
}

MANUAL_PAGE_PRODUCTS = {
    50: [
        {
            "title": "3/4\" Su Tutucu Filtre - GPF 1800",
            "model": "GPF 1800",
            "features": ["Yüksek Kalite", "Döküm Gövde", "Değişebilir İç Element"],
            "specs": GPF_FILTER_SPECS["GPF 1800"],
            "y0": 90,
            "y1": 280,
        },
        {
            "title": "1\" Su Tutucu Filtre - GPF 2600",
            "model": "GPF 2600",
            "features": ["Yüksek Kalite", "Döküm Gövde", "Değişebilir İç Element"],
            "specs": GPF_FILTER_SPECS["GPF 2600"],
            "y0": 280,
            "y1": 520,
        },
        {
            "title": "1-1/2\" Su Tutucu Filtre - GPF 3700",
            "model": "GPF 3700",
            "features": ["Yüksek Kalite", "Döküm Gövde", "Değişebilir İç Element"],
            "specs": GPF_FILTER_SPECS["GPF 3700"],
            "y0": 520,
            "y1": 820,
        },
    ],
    49: [
        {
            "title": "Alüminyum Gövdeli Kimyasal Hava Kurutucuları - GPDK 1800/2600/3700",
            "model": "GPDK",
            "features": [
                "Sağlam ve dayanıklı alüminyum gövde",
                "Geniş kurutma alanı",
                "Güçlü hava akımı",
                "Ayarlanabilir fan hızı ve ısı ayarı",
                "Patlama emniyetli tasarım",
                "Kullanımı kolay kontrol paneli",
            ],
            "specs": {
                "Bağlantı": "1\"",
                "Kapasite": "1800 / 2600 / 3700 Lt/dk",
                "Voltaj": "220 V/1 PH/50 Hz",
                "Basınç": "16 Bar",
                "Ölçüler": "394x388x784 mm (1800 model)",
                "Ağırlık": "35 kg (1800 model)",
            },
            "y0": 110,
            "y1": 430,
        },
        {
            "title": "Alüminyum Gövdeli Aktif Karbon Kuleleri - GPAC 1800/2600/3700",
            "model": "GPAC",
            "features": [
                "Yağ buharı ve koku giderimi",
                "Yüksek verimlilik (%99,9'a kadar)",
                "Kolay montaj ve kullanım",
                "Düşük bakım maliyeti",
                "Geniş uygulama alanı",
                "Çevre dostu aktif karbon dolgu",
            ],
            "specs": {
                "Bağlantı": "1\"",
                "Kapasite": "1200 / 2200 Lt/dk",
                "Basınç": "16 Bar",
                "Ölçüler": "220x1050 mm (1800 model)",
                "Ağırlık": "25 kg (1800 model)",
            },
            "y0": 430,
            "y1": 820,
        },
    ],
}

LIFT_SPECS = {
    "GPL 101": {
        "Kaldırma Kapasitesi": "4 Ton",
        "Kontrol": "Yarı Otomatik",
        "Max. Kaldırma Yüksekliği": "1800 mm",
        "Ara Mesafe": "2740 mm",
        "Dıştan Dışa Lift Ölçüsü": "3300 mm",
        "Sütun Yüksekliği": "2700 mm",
        "Sütun Genişliği": "330 mm",
        "Kısa Kol Ölçüsü": "760 - 1050 mm",
        "Uzun Kol Ölçüsü": "760 - 1200 mm",
        "Kaldırma Süresi": "50 sn",
        "İndirme Süresi": "30 sn",
        "Motor Gücü": "2.2 kW/3 Hp",
        "Voltaj": "380V/220V",
        "Ağırlık": "520 kg",
        "Ambalajlı Ölçüsü": "2840x500x710 mm",
    },
    "GPL 102": {
        "Kaldırma Kapasitesi": "4 Ton",
        "Kontrol": "Tam Otomatik",
        "Max. Kaldırma Yüksekliği": "1800 mm",
        "Ara Mesafe": "2740 mm",
        "Dıştan Dışa Lift Ölçüsü": "3300 mm",
        "Sütun Yüksekliği": "2700 mm",
        "Sütun Genişliği": "330 mm",
        "Kısa Kol Ölçüsü": "760 - 1050 mm",
        "Uzun Kol Ölçüsü": "760 - 1050-1240 mm",
        "Kaldırma Süresi": "50 sn",
        "İndirme Süresi": "30 sn",
        "Motor Gücü": "2.2 kW/3 Hp",
        "Voltaj": "380V/220V",
        "Ağırlık": "535 kg",
        "Ambalajlı Ölçüsü": "2840x500x710 mm",
    },
    "GPL 102U": {
        "Kaldırma Kapasitesi": "4 Ton",
        "Kontrol": "Tam Otomatik",
        "Max. Kaldırma Yüksekliği": "1800 mm",
        "Ara Mesafe": "2750 mm",
        "Dıştan Dışa Lift Ölçüsü": "3300 mm",
        "Sütun Yüksekliği": "3600 mm",
        "Sütun Genişliği": "330 mm",
        "Kısa Kol Ölçüsü": "760 - 1050 mm",
        "Uzun Kol Ölçüsü": "760 - 1050-1240 mm",
        "Kaldırma Süresi": "50 sn",
        "İndirme Süresi": "30 sn",
        "Motor Gücü": "2.2 kW/3 Hp",
        "Voltaj": "380V/220V",
        "Ağırlık": "575 kg",
        "Ambalajlı Ölçüsü": "280x7x45 cm",
    },
    "GPL 103": {
        "Kaldırma Kapasitesi": "5 Ton",
        "Kontrol": "Tam Otomatik",
        "Max. Kaldırma Yüksekliği": "1800 mm",
        "Ara Mesafe": "3190 mm",
        "Dıştan Dışa Lift Ölçüsü": "3800 mm",
        "Sütun Yüksekliği": "2700 mm",
        "Sütun Genişliği": "380 mm",
        "Kısa Kol Ölçüsü": "800 - 1100 - 1400 mm",
        "Uzun Kol Ölçüsü": "870 - 1200 - 1500 mm",
        "Kaldırma Süresi": "50 sn",
        "İndirme Süresi": "30 sn",
        "Motor Gücü": "2.2 kW/3 Hp",
        "Voltaj": "380V/220V",
        "Ağırlık": "650 kg",
        "Ambalajlı Ölçüsü": "2840x500x710 mm",
    },
    "GPL 103U": {
        "Kaldırma Kapasitesi": "5 Ton",
        "Kontrol": "Tam Otomatik",
        "Max. Kaldırma Yüksekliği": "1800 mm",
        "Ara Mesafe": "3200 mm",
        "Dıştan Dışa Lift Ölçüsü": "3760 mm",
        "Sütun Yüksekliği": "3920 mm",
        "Sütun Genişliği": "380 mm",
        "Kısa Kol Ölçüsü": "800 - 1100 - 1400 mm",
        "Uzun Kol Ölçüsü": "870 - 1200 - 1500 mm",
        "Kaldırma Süresi": "50 sn",
        "İndirme Süresi": "30 sn",
        "Motor Gücü": "2.2 kW/3 Hp",
        "Voltaj": "380V/220V",
        "Ağırlık": "700 kg",
        "Ambalajlı Ölçüsü": "3340x520x720 mm",
    },
    "GPML 102": {
        "Kaldırma Kapasitesi": "3 Ton",
        "Kontrol": "Tam Otomatik",
        "Max. Kaldırma Yüksekliği": "1000 mm",
        "Ara Mesafe": "840 mm",
        "Dıştan Dışa Lift Ölçüsü": "1980 mm",
        "Tabla Uzunluğu": "1400 mm",
        "Tabla Genişliği": "600 mm",
        "Motor Gücü": "2.2 kW/3 Hp",
        "Voltaj": "380V/220V",
        "Ağırlık": "505 kg",
    },
    "GPML 101": {
        "Kaldırma Kapasitesi": "3.5 Ton",
        "Kontrol": "Tam Otomatik",
        "Max. Kaldırma Yüksekliği": "1800 mm",
        "Ara Mesafe": "800 mm",
        "Dıştan Dışa Lift Ölçüsü": "2000 mm",
        "Tabla Uzunluğu": "1400 mm",
        "Tabla Genişliği": "600 mm",
        "Motor Gücü": "2.2 kW/3 Hp",
        "Voltaj": "380V/220V",
        "Ağırlık": "763 kg",
    },
}

LIFT_FEATURES = [
    "Güçlendirilmiş Gövde",
    "Yükseltici Takozlar",
    "Zincir, Halat ve Kilit",
    "Elektrik Panosu",
]

MANUAL_PAGE_PRODUCTS.update(
    {
        53: [
            {
                "title": "4 Ton İki Sütunlu Elektro Hidrolik Lift (Yarı Otomatik) - GPL 101",
                "model": "GPL 101",
                "features": LIFT_FEATURES + ["2 Kademeli Kol", "Kilit Açma Kolu"],
                "specs": LIFT_SPECS["GPL 101"],
                "y0": 80,
                "y1": 780,
            }
        ],
        54: [
            {
                "title": "4 Ton İki Sütunlu Elektro Hidrolik Lift (Tam Otomatik) - GPL 102",
                "model": "GPL 102",
                "features": LIFT_FEATURES + ["3 Kademeli Kol"],
                "specs": LIFT_SPECS["GPL 102"],
                "y0": 80,
                "y1": 780,
            }
        ],
        55: [
            {
                "title": "4 Ton İki Sütunlu Üstten Bağlantılı Tam Otomatik Hidrolik Lift - GPL 102U",
                "model": "GPL 102U",
                "features": LIFT_FEATURES + ["3 Kademeli Kol"],
                "specs": LIFT_SPECS["GPL 102U"],
                "y0": 80,
                "y1": 780,
            }
        ],
        56: [
            {
                "title": "5 Ton İki Sütunlu Elektro Hidrolik Lift (Tam Otomatik) - GPL 103",
                "model": "GPL 103",
                "features": LIFT_FEATURES + ["3 Kademeli Kol"],
                "specs": LIFT_SPECS["GPL 103"],
                "y0": 80,
                "y1": 780,
            }
        ],
        57: [
            {
                "title": "5 Ton İki Sütunlu Üsten Bağlantılı Tam Otomatik Hidrolik Lift - GPL 103U",
                "model": "GPL 103U",
                "features": LIFT_FEATURES + ["3 Kademeli Kol"],
                "specs": LIFT_SPECS["GPL 103U"],
                "y0": 80,
                "y1": 780,
            }
        ],
        58: [
            {
                "title": "3 Ton 1 Metre Makaslı Lift - GPML 102",
                "model": "GPML 102",
                "features": ["Yükseltici Takozlar", "Araç Kaldırma Rampası", "Kilit Sistemi"],
                "specs": LIFT_SPECS["GPML 102"],
                "y0": 80,
                "y1": 780,
            }
        ],
        59: [
            {
                "title": "3.5 Ton 2 Metre Makaslı Lift - GPML 101",
                "model": "GPML 101",
                "features": ["Yükseltici Takozlar", "Araç Kaldırma Rampası", "Kilit Sistemi"],
                "specs": LIFT_SPECS["GPML 101"],
                "y0": 80,
                "y1": 780,
            }
        ],
        82: [
            {
                "title": "250-500 kg Elektrikli Vinç - GP250-500",
                "model": "GP250-500",
                "features": ["%100 bakır sargı", "10/20 metre halat boyu seçeneği"],
                "specs": {
                    "Kaldırma Kapasitesi": "250-500 kg",
                    "Motor Gücü": "1020 W",
                    "Voltaj": "220 V/50 Hz",
                    "Halat Boyu": "20-10 m",
                    "Halat Kalınlığı": "4 mm",
                    "Ağırlık": "15 kg",
                    "Ölçüler": "44x32x26 cm",
                },
                "y0": 130,
                "y1": 250,
            },
            {
                "title": "400-800 kg Elektrikli Vinç - GP400-800",
                "model": "GP400-800",
                "features": ["%100 bakır sargı", "10/20 metre halat boyu seçeneği"],
                "specs": {
                    "Kaldırma Kapasitesi": "400-800 kg",
                    "Motor Gücü": "1450 W",
                    "Voltaj": "220 V/50 Hz",
                    "Halat Boyu": "20-10 m",
                    "Ağırlık": "22 kg",
                },
                "y0": 250,
                "y1": 340,
            },
            {
                "title": "1.5 Ton Zincirli Caraskal - GPH15T",
                "model": "GPH15T",
                "features": ["Kompakt tasarım", "Kolay taşıma"],
                "specs": {
                    "Kaldırma Kapasitesi": "1.5 Ton",
                    "Kaldırma Yüksekliği": "1.5 m",
                    "Zincir Kalınlığı": "8 mm",
                    "Ağırlık": "12 kg",
                    "Ölçüler": "51x18x14 cm",
                },
                "y0": 340,
                "y1": 430,
            },
            {
                "title": "3 Ton Zincirli Caraskal - GPH3T",
                "model": "GPH3T",
                "features": ["Kompakt tasarım", "Kolay taşıma"],
                "specs": {
                    "Kaldırma Kapasitesi": "3 Ton",
                    "Kaldırma Yüksekliği": "1.5 m",
                    "Zincir Kalınlığı": "10 mm",
                    "Ağırlık": "18 kg",
                },
                "y0": 430,
                "y1": 500,
            },
            {
                "title": "1 Ton 3 m Hubzug - GPC1T3M",
                "model": "GPC1T3M",
                "features": ["Zincirli hubzug", "Kolay montaj"],
                "specs": {
                    "Kaldırma Kapasitesi": "1 Ton",
                    "Kaldırma Yüksekliği": "3 m",
                    "Zincir Kalınlığı": "6 mm",
                    "Ağırlık": "10 kg",
                    "Ölçüler": "26x16x16 cm",
                },
                "y0": 500,
                "y1": 580,
            },
            {
                "title": "1 Ton 5 m Hubzug - GPC1T5M",
                "model": "GPC1T5M",
                "features": ["Zincirli hubzug", "Kolay montaj"],
                "specs": {
                    "Kaldırma Kapasitesi": "1 Ton",
                    "Kaldırma Yüksekliği": "5 m",
                    "Zincir Kalınlığı": "6 mm",
                    "Ağırlık": "12.5 kg",
                    "Ölçüler": "28x17x16 cm",
                },
                "y0": 580,
                "y1": 650,
            },
            {
                "title": "2 Ton 3 m Hubzug - GPC2T3M",
                "model": "GPC2T3M",
                "features": ["Zincirli hubzug", "Kolay montaj"],
                "specs": {
                    "Kaldırma Kapasitesi": "2 Ton",
                    "Kaldırma Yüksekliği": "3 m",
                    "Zincir Kalınlığı": "6 mm",
                    "Ağırlık": "13 kg",
                    "Ölçüler": "28x17x16 cm",
                },
                "y0": 650,
                "y1": 720,
            },
            {
                "title": "2 Ton 5 m Hubzug - GPC2T5M",
                "model": "GPC2T5M",
                "features": ["Zincirli hubzug", "Kolay montaj"],
                "specs": {
                    "Kaldırma Kapasitesi": "2 Ton",
                    "Kaldırma Yüksekliği": "5 m",
                    "Zincir Kalınlığı": "6 mm",
                    "Ağırlık": "18 kg",
                    "Ölçüler": "34x22x19 cm",
                },
                "y0": 720,
                "y1": 800,
            },
        ],
        61: [
            {
                "title": "İki Ton Katlanır Vinç - GPT 101",
                "model": "GPT 101",
                "features": ["Katlanabilir tip", "Profesyonel kullanım", "360° dönen tekerlekler"],
                "specs": {
                    "Kaldırma Kapasitesi": "2 Ton",
                    "Kaldırma Aralığı": "25-2000 mm",
                    "Maksimum Yükseklik": "1750 mm",
                    "Ağırlık": "70 kg",
                },
                "y0": 90,
                "y1": 420,
            },
            {
                "title": "Üç Ton Alçak Şase Garaj Krikosu - GPT 102",
                "model": "GPT 102",
                "features": [
                    "3 Ton kaldırma kapasitesi",
                    "Profesyonel kullanım",
                    "Çift piston",
                    "360° dönen tekerlekler",
                    "Alçak şase",
                ],
                "specs": {
                    "Kaldırma Kapasitesi": "3 Ton",
                    "Minimum Yükseklik": "75 mm",
                    "Maksimum Yükseklik": "505 mm",
                },
                "y0": 420,
                "y1": 780,
            },
        ],
        62: [
            {
                "title": "0.5 Ton Dikey Şanzıman Krikosu - GPT 103",
                "model": "GPT 103",
                "features": ["0.5 ton kapasite", "Kaldırma mandalı", "360° dönen tekerlekler"],
                "specs": {
                    "Kaldırma Kapasitesi": "0.5 Ton",
                    "Minimum Yükseklik": "1130 mm",
                    "Maksimum Yükseklik": "1940 mm",
                },
                "y0": 90,
                "y1": 300,
            },
            {
                "title": "450 Kg Motor Standı - GPT 104",
                "model": "GPT 104",
                "features": [
                    "Motor bağlama aparatı",
                    "360° dönen tekerlekler",
                    "Sabit kriko tablası",
                    "Profesyonel kullanım",
                ],
                "specs": {
                    "Kaldırma Kapasitesi": "450 kg",
                    "Çalışma Yüksekliği": "880 mm",
                    "Tip": "Motor Standı",
                },
                "y0": 300,
                "y1": 520,
            },
            {
                "title": "650 Kg Motor Standı - GPT 105",
                "model": "GPT 105",
                "features": [
                    "Motor bağlama aparatı",
                    "360° dönen tekerlekler",
                    "Sabit kriko tablası",
                    "Profesyonel kullanım",
                ],
                "specs": {
                    "Kaldırma Kapasitesi": "650 kg",
                    "Çalışma Yüksekliği": "880 mm",
                    "Tip": "Motor Standı",
                },
                "y0": 520,
                "y1": 780,
            },
        ],
        83: [
            {
                "title": "2.5 Ton Transpalet - GP 25110K",
                "model": "GP 25110K",
                "features": ["Kemik teker", "Döküm pompa"],
                "specs": {
                    "Kaldırma Kapasitesi": "2500 kg",
                    "Minimum Çatal Yüksekliği": "85 mm",
                    "Maksimum Çatal Yüksekliği": "200 mm",
                    "Çatal Genişliği": "550 mm",
                    "Çatal Boyu": "1150 mm",
                    "Ağırlık": "64 kg",
                },
                "y0": 90,
                "y1": 420,
            },
            {
                "title": "2.5 Ton Transpalet - GP 25110P",
                "model": "GP 25110P",
                "features": ["Polyester teker", "Döküm pompa"],
                "specs": {
                    "Kaldırma Kapasitesi": "2500 kg",
                    "Minimum Çatal Yüksekliği": "85 mm",
                    "Maksimum Çatal Yüksekliği": "200 mm",
                    "Çatal Genişliği": "550 mm",
                    "Çatal Boyu": "1150 mm",
                    "Ağırlık": "70 kg",
                },
                "y0": 420,
                "y1": 780,
            },
        ],
    }
)

PRODUCT_OVERRIDES = {
    "GP 5KVA": {
        "features": [
            "Otomobil kapı, çamurluk ve kaporta göçüklerini düzeltmek için tasarlanmış portatif makine",
            "Yüksek transformatör gücü",
            "5 kademeli akım ayarı",
            "2 m. pense ve şase kablosu dahil",
        ],
        "specs": {
            "Şebeke Gerilimi": "1 Faz, 220 V 50 Hz",
            "Açık Devre Gerilimi": "8,5 V",
            "Gerekli Şebeke Sigortası": "1x40 A (C Tipi)",
            "Maximum Giriş Gücü": "5 kVA",
            "Çektirme Kapasitesi": "0,60 ila 0,80 mm",
            "İzolasyon Sınıfı": "H",
            "Koruma Sınıfı": "IP 21 sn",
            "Boyutlar": "24x35x31 cm",
            "Ağırlık": "26 kg",
        },
    },
    "GP 10KVA": {
        "features": [
            "Otomobil, otobüs ve kamyon kaporta göçüklerini düzeltmek için profesyonel tip makine",
            "Yüksek transformatör gücü",
            "2 kademe kaba ve ince akım ayarı",
            "2 m. pense ve şase kablosu dahil",
        ],
        "specs": {
            "Şebeke Gerilimi": "1 Faz, 220 V 50 Hz",
            "Açık Devre Gerilimi": "7,7 V",
            "Gerekli Şebeke Sigortası": "1x40 A (C Tipi)",
            "Maximum Giriş Gücü": "10 kVA",
            "Çektirme Kapasitesi": "0,80 ila 1,00 mm",
            "Tek Taraflı Punta Kapasitesi": "0,60+0,60 mm",
            "İzolasyon Sınıfı": "H",
            "Koruma Sınıfı": "IP 21 sn",
            "Boyutlar": "51x53x92 cm",
            "Ağırlık": "52 kg",
        },
    },
    "GP 12KVA": {
        "features": [
            "Profesyonel tip kaporta çektirme makinesi",
            "Yüksek transformatör gücü",
            "2 kademe kaba ve ince akım ayarı",
            "2 m. pense ve şase kablosu dahil",
        ],
        "specs": {
            "Şebeke Gerilimi": "1 Faz, 220 V 50 Hz",
            "Açık Devre Gerilimi": "8,9 V",
            "Gerekli Şebeke Sigortası": "1x63 A (C Tipi)",
            "Maximum Giriş Gücü": "12 kVA",
            "Çektirme Kapasitesi": "0,80 ila 1,20 mm",
            "Tek Taraflı Punta Kapasitesi": "0,80+0,80 mm",
            "İzolasyon Sınıfı": "H",
            "Koruma Sınıfı": "IP 21 sn",
            "Boyutlar": "51x53x92 cm",
            "Ağırlık": "60 kg",
        },
    },
    "GP 10MAX": {
        "features": [
            "10 kVA elektronik akım ve zaman kontrollü profesyonel kaporta çektirme makinesi",
            "Dijital ayar ile minimum iz bırakma",
            "Yüksek transformatör gücü",
            "2 m. pense ve şase kablosu dahil",
        ],
        "specs": {
            "Şebeke Gerilimi": "1 Faz, 220 V 50 Hz",
            "Açık Devre Gerilimi": "7,7 V",
            "Gerekli Şebeke Sigortası": "1x25 A (C Tipi)",
            "Maximum Giriş Gücü": "10 kVA",
            "Çektirme Kapasitesi": "0,30 ila 1,30 mm",
            "İzolasyon Sınıfı": "H",
            "Koruma Sınıfı": "IP 21 sn",
            "Boyutlar": "47x50x100 cm",
            "Ağırlık": "35 kg",
        },
    },
    "GP 12PRO": {
        "features": [
            "12 kVA elektronik akım ve zaman kontrollü profesyonel kaporta çektirme seti",
            "Normal ve sinerjik çalışma modları",
            "Manuel ve otomatik çalışma seçeneği",
            "7 özel program: üçgen pul, zigzag teli, pul puntalama, şiş alma vb.",
            "Çektirme aparatı, pul, tel, kablo ve aslan pençesi aksesuarları dahil",
        ],
        "specs": {
            "Şebeke Gerilimi": "1 Faz, 220 V 50 Hz",
            "Açık Devre Gerilimi": "7,7 V",
            "Gerekli Şebeke Sigortası": "1x32 A (C Tipi)",
            "Maximum Giriş Gücü": "12 kVA",
            "Çektirme Kapasitesi": "0,30 ila 1,60 mm",
            "İzolasyon Sınıfı": "H",
            "Koruma Sınıfı": "IP 21 sn",
            "Boyutlar": "47x50x100 cm",
            "Ağırlık": "40 kg",
        },
    },
    "GP 12A1": {
        "specs": {
            "Kazan Hacmi": "12 Lt",
            "Basınç Oranı": "50:1",
            "Gres Çıkışı": "0.85 lt/dk",
            "Hava Basıncı": "6-8 Bar",
            "Hortum Uzunluğu": "4 m",
        },
        "features": ["Z Mafsallı Tabanca", "1/4 Regülatör", "4 M Hortum", "Metal Gres Sıyırıcı"],
    },
    "GP 35A1": {
        "specs": {
            "Kazan Hacmi": "35 Lt",
            "Basınç Oranı": "50:1",
            "Gres Çıkışı": "0.85 lt/dk",
            "Hava Basıncı": "6-8 Bar",
            "Hortum Uzunluğu": "4 m",
        },
        "features": ["Z Mafsallı Tabanca", "1/4 Regülatör", "4 M Hortum", "Metal Gres Sıyırıcı"],
    },
    "GP 12A2": {
        "specs": {
            "Kazan Hacmi": "12 Lt",
            "Basınç Oranı": "60:1",
            "Gres Çıkışı": "0.85 lt/dk",
            "Hava Basıncı": "6-8 Bar",
            "Hortum Uzunluğu": "4 m",
        },
        "features": ["Z Mafsallı Tabanca", "1/4 Regülatör", "4 M Hortum", "Metal Gres Sıyırıcı"],
    },
    "GP 35A2": {
        "specs": {
            "Kazan Hacmi": "35 Lt",
            "Basınç Oranı": "60:1",
            "Gres Çıkışı": "0.85 lt/dk",
            "Hava Basıncı": "6-8 Bar",
            "Hortum Uzunluğu": "4 m",
        },
        "features": ["Z Mafsallı Tabanca", "1/4 Regülatör", "4 M Hortum", "Metal Gres Sıyırıcı"],
    },
    "GPT 102": {
        "specs": {
            "Kaldırma Kapasitesi": "3 Ton",
            "Minimum Yükseklik": "75 mm",
            "Maksimum Yükseklik": "505 mm",
        },
        "features": [
            "3 Ton kaldırma kapasitesi",
            "Profesyonel kullanım",
            "Çift piston",
            "360° dönen tekerlekler",
            "Alçak şase",
            "Plastik yüzey",
        ],
    },
    "GPT 119": {
        "specs": {"Taşıma Kapasitesi": "500 kg", "Ağırlık": "15 kg", "Ölçüler": "805x370x205 mm"},
        "features": ["Motor askı aparatı", "2 adet cep", "Yumuşak yastık"],
    },
    "GPT 116": {
        "features": [
            "H tipi çelik çerçeve",
            "Kimyasal yıkama sonrası boyalı, pas önleyici yüzey",
            "Geniş hidrolik silindir ünitesi",
            "Kolay pompalama için sap dahil",
        ],
        "specs": {"Kapasite": "10 Ton", "Tip": "Manuel Hidrolik Pres"},
    },
    "GPT 117": {
        "features": [
            "Yüksek kaliteli çelikten imal",
            "H tipi çerçeve",
            "Yağ ve grese dayanıklı boya",
            "Geniş hidrolik silindir, pompalama sapı dahil",
        ],
        "specs": {"Kapasite": "15 Ton", "Tip": "Manuel Hidrolik Pres"},
    },
    "GPT 118": {
        "features": [
            "H tipi çelik çerçeve",
            "Uzun ömürlü pas önleyici boya",
            "Düşük yağ basıncı ile geniş silindir",
            "Kolay pompalama sapı",
        ],
        "specs": {"Kapasite": "30 Ton", "Tip": "Manuel Hidrolik Pres"},
    },
    "GPT 201": {
        "specs": {
            "En": "450 mm",
            "Genişlik": "600 mm",
            "Yükseklik": "900 mm",
            "Taşıma Kapasitesi": "240 kg",
        },
        "features": ["Elektrostatik toz boyalı", "Geniş üst çalışma bölümü"],
    },
    "GPT 202": {
        "specs": {
            "En": "450 mm",
            "Genişlik": "600 mm",
            "Yükseklik": "900 mm",
            "Taşıma Kapasitesi": "240 kg",
        },
        "features": ["Elektrostatik toz boyalı", "Geniş üst çalışma bölümü", "1 çekmece"],
    },
    "GPT 203": {
        "specs": {
            "En": "450 mm",
            "Genişlik": "600 mm",
            "Yükseklik": "900 mm",
            "Taşıma Kapasitesi": "240 kg",
        },
        "features": ["Elektrostatik toz boyalı", "Kilit sistemi", "2 çekmece"],
    },
    "GPT 204": {
        "specs": {
            "En": "450 mm",
            "Genişlik": "600 mm",
            "Yükseklik": "900 mm",
            "Taşıma Kapasitesi": "240 kg",
        },
        "features": ["Elektrostatik toz boyalı", "Kilit sistemi", "5 çekmece"],
    },
    "GPT 205": {
        "specs": {
            "En": "1500 mm",
            "Genişlik": "650 mm",
            "Yükseklik": "900 mm",
            "Pano Ölçüsü": "850 mm",
            "Taşıma Kapasitesi": "250 kg",
        },
        "features": ["Led lamba", "1 adet priz", "Avadanlık", "6 çekmece", "30 adet kanca"],
    },
    "GPT 206": {
        "specs": {
            "En": "2000 mm",
            "Derinlik": "650 mm",
            "Yükseklik": "900 mm",
            "Pano Ölçüsü": "850 mm",
            "Taşıma Kapasitesi": "350 kg",
        },
        "features": ["Led lamba", "2 adet priz", "Avadanlık", "Kilit sistemi", "30 adet kanca"],
    },
    "GPT 207": {
        "specs": {
            "En": "2000 mm",
            "Genişlik": "650 mm",
            "Yükseklik": "900 mm",
            "Pano Ölçüsü": "850 mm",
            "Taşıma Kapasitesi": "250 kg",
        },
        "features": ["Led lamba", "1 adet priz", "Avadanlık", "Dolaplı tezgah", "30 adet kanca"],
    },
    "GP 850": {
        "specs": {
            "Kare Ölçüsü": "1/2 inç",
            "Tork Gücü": "850 Nm",
            "Yüksüz Hız": "2300/1900/1450 rpm",
            "Voltaj": "21 V",
            "Akü": "4.0 Ah/Li-ion",
            "Ağırlık": "1.88 kg",
            "Koli Adeti": "4 Adet",
        },
    },
    "GP 1300": {
        "specs": {
            "Kare Ölçüsü": "1/2 inç",
            "Tork Gücü": "1300 Nm",
            "Yüksüz Hız": "1800/1200/900 rpm",
            "Voltaj": "21 V",
            "Akü": "4.0 Ah/Li-ion",
            "Ağırlık": "2.81 kg",
            "Koli Adeti": "4 Adet",
        },
    },
    "GP 25110P": {
        "specs": {
            "Kaldırma Kapasitesi": "2500 kg",
            "Minimum Çatal Yüksekliği": "85 mm",
            "Maksimum Çatal Yüksekliği": "200 mm",
            "Çatal Genişliği": "550 mm",
            "Çatal Boyu": "1150 mm",
            "Ağırlık": "70 kg",
        },
        "features": ["Polyester teker", "Döküm pompa"],
    },
    "GP 165I": {
        "specs": {
            "Voltaj": "220 V (AC)",
            "Açık Devre Gerilimi": "70 V (DC)",
            "Maximum Çıkış Akımı": "160 A",
            "Tavsiye Edilen Şebeke Sigortası": "C Tipi 25 A",
            "Eritilebilecek Elektrod Tipleri": "Rutil/Bazik",
            "Elektrod Çapı": "2.50 - 3.25 - 4.00 (max)",
            "Çalışma Verimi": "%20'te 160 A",
            "Koruma Sınıfı": "IP21S",
            "Ağırlık": "3.5 kg",
            "Ölçüler": "12 x 32 x 19,5 cm",
        },
    },
    "GP 200I": {
        "specs": {
            "Voltaj": "220 V (AC)",
            "Açık Devre Gerilimi": "70 V (DC)",
            "Maximum Çıkış Akımı": "190 A",
            "Tavsiye Edilen Şebeke Sigortası": "C Tipi 40 A",
            "Eritilebilecek Elektrod Tipleri": "Rutil/Bazik/Selülozik",
            "Elektrod Çapı": "2.50 - 3.25 - 4.00",
            "Çalışma Verimi": "%20'te 190 A",
            "Koruma Sınıfı": "IP21S",
            "Ağırlık": "4 kg",
            "Ölçüler": "12 x 35 x 19,5 cm",
        },
    },
    "GPT 101": {
        "title": "İki Ton Katlanır Vinç - GPT 101",
        "specs": {
            "Kaldırma Kapasitesi": "2 Ton",
            "Kaldırma Aralığı": "25-2000 mm",
            "Maksimum Yükseklik": "1750 mm",
            "Ağırlık": "70 kg",
        },
        "features": ["Katlanabilir tip", "Profesyonel kullanım", "360° dönen tekerlekler"],
    },
    "GPT 110": {
        "specs": {
            "Kapasite": "10 Ton",
            "Hareket Mesafesi": "125 mm",
            "Ağırlık": "28 kg",
            "Ambalajlı Ölçüsü": "730x310x175 mm",
        },
        "features": ["Profesyonel kullanım", "Uzatma pistonları", "Aparatlar dahil"],
    },
}

SKIP_LINES = {
    "www.gapkompresor.com",
    "www.gaptools.net",
    "fiyat sorunuz",
    "oil",
    "kapatise",
    "ambalajlı",
    "amb",
}
SKIP_LINE_RE = re.compile(
    r"^(\d{1,3}|profesyoneller|best solutions|gapkompresor|gaptools)$",
    re.I,
)
MODEL_RE = re.compile(
    r"\b(GP\s?\d+[\w-]*|GPS\s?\d+[\w]*|GPY\s?\d+[\w]*|GPV\s?\d+[\w]*|GPHK\s?\d+|GPDK[\s\d/]*|GPAC[\s\d/]*|GPF\s?\d+|GPHT\s?\d+|GPT\s?\d+|GPL[\s]?\d+[\w]*|GPML\s?\d+|GPLF\s?\d+|GPM\s?\d+|GPLS\s?\d+|GPMT\s?\d+|GPC\w+|GPH\w+|GP250-500|GP400-800|GP\s?25\d+\w*)\b",
    re.I,
)
INVALID_TITLE_RE = re.compile(
    r"^(•|kadar|normal mod|sinerjik|manuel çalışma|otomatik çalışma|makin)",
    re.I,
)
TITLE_HINTS = (
    "kompresör",
    "kompresor",
    "lift",
    "makinesi",
    "makina",
    "tabanca",
    "pompa",
    "vinç",
    "vinc",
    "pres",
    "kriko",
    "stand",
    "filtre",
    "kurutucu",
    "tank",
    "transpalet",
    "kaynak",
    "çektirme",
    "cektirme",
    "arabas",
    "tezgah",
    "somun",
    "zımpara",
    "zimpara",
    "fener",
    "hortum",
    "aparat",
    "pençe",
    "pence",
    "kolu",
    "gerdirme",
    "sütunlu",
    "ton ",
    "caraskal",
    "hubzug",
    "yıkama",
    "yikama",
    "gres",
)
SPEC_LABELS = [
    "Depo Hacmi",
    "Güç",
    "Hava Emişi",
    "Basınç",
    "Devir",
    "Voltaj",
    "Piston Çapı",
    "Ağırlık",
    "Ölçüler",
    "Kapasite",
    "Kaldırma Kapasitesi",
    "Motor Gücü",
    "Tork Gücü",
    "Kare Ölçüsü",
    "Hava Girişi",
    "Hava Basıncı",
    "Koli Adeti",
    "Maksimum Basınç",
    "Test Basıncı",
    "Sac Kalınlığı",
    "Çalışma Basıncı",
    "Boyutlar",
    "Kazan Hacmi",
    "Kontrol",
    "Max. Kaldırma Yüksekliği",
    "Ara Mesafe",
    "Dıştan Dışa Lift Ölçüsü",
    "Sütun Yüksekliği",
    "Sütun Genişliği",
    "Kısa Kol Ölçüsü",
    "Uzun Kol Ölçüsü",
    "Kaldırma Süresi",
    "İndirme Süresi",
    "Ambalajlı Ölçüsü",
    "Tabla Uzunluğu",
    "Tabla Genişliği",
    "Minimum Çatal Yüksekliği",
    "Maksimum Çatal Yüksekliği",
    "Çatal Genişliği",
    "Çatal Boyu",
    "Şebeke Gerilimi",
    "Açık Devre Gerilimi",
    "Gerekli Şebeke Sigortası",
    "Maximum Giriş Gücü",
    "Çektirme Kapasitesi",
    "Tek Taraflı Punta Kapasitesi",
    "İzolasyon Sınıfı",
    "Koruma Sınıfı",
    "Basınç Oranı",
    "Gres Çıkışı",
    "Akış",
    "Hortum Uzunluğu",
    "Taşıma Kapasitesi",
    "En",
    "Genişlik",
    "Yükseklik",
    "Pano Ölçüsü",
    "Yüksüz Hız",
    "Akü",
    "Zımpara Ölçüsü",
    "Civata Kapasitesi",
    "Maximum Çıkış Akımı",
    "Tavsiye Edilen Şebeke Sigortası",
    "Eritilebilecek Elektrod Tipleri",
    "Elektrod Çapı",
    "Çalışma Verimi",
    "Halat Boyu",
    "Halat Kalınlığı",
    "Zincir Kalınlığı",
    "Kaldırma Yüksekliği",
    "Minimum Yükseklik",
    "Maksimum Yükseklik",
    "Kaldırma Aralığı",
    "Sıkıştırma Aralığı",
    "Hareket Mesafesi",
    "Tip",
    "Bağlantı",
    "Gövde",
    "Max. Basınç",
]


WELDING_SPEC_KEYS = {
    "Açık Devre Gerilimi",
    "Maximum Çıkış Akımı",
    "Tavsiye Edilen Şebeke Sigortası",
    "Eritilebilecek Elektrod Tipleri",
    "Elektrod Çapı",
    "Çalışma Verimi",
    "Şebeke Gerilimi",
    "Gerekli Şebeke Sigortası",
    "Maximum Giriş Gücü",
    "Çektirme Kapasitesi",
    "Tek Taraflı Punta Kapasitesi",
    "İzolasyon Sınıfı",
    "Koruma Sınıfı",
}


def sanitize_product_specs(product: dict) -> dict:
    title = product.get("title", "").lower()
    if "kompresör" not in title and "kompresor" not in title:
        return product
    specs = dict(product.get("specs") or {})
    for key in WELDING_SPEC_KEYS:
        specs.pop(key, None)
    product["specs"] = specs
    return product


def normalize_spec_value(value: str) -> str:
    value = value.strip()
    if len(value) > 2 and value[0] == "w" and value[1].isdigit():
        return value[1:]
    return value


def slugify(value: str) -> str:
    value = value.lower()
    value = (
        value.replace("ı", "i")
        .replace("ğ", "g")
        .replace("ü", "u")
        .replace("ş", "s")
        .replace("ö", "o")
        .replace("ç", "c")
        .replace("İ", "i")
    )
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:80] or "urun"


def clean_lines(text: str) -> list[str]:
    lines = []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line or line == ":":
            continue
        low = line.lower()
        if low in SKIP_LINES:
            continue
        if SKIP_LINE_RE.match(line):
            continue
        if re.fullmatch(r"\d+", line):
            continue
        lines.append(line)
    return lines


def is_title_line(line: str) -> bool:
    low = line.lower()
    if len(line) < 12:
        return False
    if " - " in line and any(h in low for h in TITLE_HINTS):
        return True
    if MODEL_RE.search(line) and any(h in low for h in TITLE_HINTS):
        return True
    if any(h in low for h in TITLE_HINTS) and len(line) > 18:
        return True
    if "su tutucu filtre" in low or "kimyasal hava kurutucu" in low:
        return True
    if "aktif karbon" in low and "kule" in low:
        return True
    return False


def extract_model(title: str, lines: list[str]) -> str:
    for source in [title, *lines[:8]]:
        match = MODEL_RE.search(source)
        if match:
            model = re.sub(r"\s+", " ", match.group(1)).upper()
            if model.startswith("GP ") and len(model) > 6:
                return model
            return model
    return ""


def expand_colon_blocks(lines: list[str]) -> list[str]:
    expanded = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line == ":":
            i += 1
            continue
        if i + 1 < len(lines) and lines[i + 1].strip() == ":":
            label = line.rstrip(":").strip()
            value = ""
            j = i + 2
            while j < len(lines) and lines[j].strip() == ":":
                j += 1
            if j < len(lines):
                value = lines[j].strip()
            if label and value and value != ":":
                expanded.append(f"{label}: {value}")
                i = j + 1
                continue
        expanded.append(line)
        i += 1
    return expanded


def parse_inline_specs(lines: list[str]) -> dict[str, str]:
    specs = {}
    labels = {label.lower(): label for label in SPEC_LABELS}
    for line in lines:
        if ":" not in line:
            continue
        left, right = line.split(":", 1)
        label_key = left.strip().lower()
        value = right.strip()
        if label_key in labels and value and not is_title_line(value):
            specs[labels[label_key]] = normalize_spec_value(value)
    return specs


def parse_specs(lines: list[str]) -> dict[str, str]:
    specs = parse_inline_specs(lines)
    normalized = expand_colon_blocks([line for line in lines if line.strip() and line.strip() != ":"])
    labels = {label.lower(): label for label in SPEC_LABELS}
    i = 0
    while i < len(normalized):
        token = normalized[i]
        low = token.lower()
        if low in labels:
            label = labels[low]
            value = ""
            if i + 1 < len(normalized):
                nxt = normalized[i + 1]
                if nxt.lower() not in labels and not is_title_line(nxt):
                    value = nxt
                    i += 1
            if value and not re.search(r"\d", value) and label in {"Ölçüler", "Ağırlık", "Depo Hacmi", "Güç", "Basınç"}:
                value = ""
            if value:
                specs[label] = normalize_spec_value(value)
        i += 1
    return specs


def normalize_model_key(model: str) -> str:
    model = re.sub(r"\s+", " ", model.upper()).strip()
    return model.replace("İ", "I")


def apply_product_overrides(product: dict) -> dict:
    model = normalize_model_key(product.get("model") or "")
    if not model:
        return product
    override = PRODUCT_OVERRIDES.get(model)
    if not override:
        for key, data in PRODUCT_OVERRIDES.items():
            norm_key = normalize_model_key(key)
            if norm_key == model or norm_key in model or model in norm_key:
                override = data
                break
    if not override:
        return sanitize_product_specs(product)
    if override.get("title"):
        product["title"] = override["title"]
    if override.get("features"):
        product["features"] = override["features"]
    if override.get("specs"):
        merged = dict(product.get("specs") or {})
        merged.update(override["specs"])
        product["specs"] = merged
    return sanitize_product_specs(product)


def parse_features(lines: list[str], specs: dict[str, str]) -> list[str]:
    spec_values = {v.lower() for v in specs.values() if v}
    spec_labels = {k.lower() for k in specs}
    features = []
    for line in lines:
        low = line.lower()
        if is_title_line(line):
            continue
        if low in spec_labels or low in spec_values:
            continue
        if low in {label.lower() for label in SPEC_LABELS}:
            continue
        if line in specs.values():
            continue
        if re.fullmatch(r"[\d\.]+", line):
            continue
        if re.search(r"\d", line) and any(unit in low for unit in (" lt", " dk", " mm", " kg", " cm", " db", " bar", " hp", " kw", " nm", " rpm", " r/dk")):
            continue
        if len(line) < 4 or len(line) > 90:
            continue
        if INVALID_TITLE_RE.match(line):
            continue
        cleaned = re.sub(r"^[\u2022\u00b7•\-\s]+", "", line).strip()
        if cleaned not in features:
            features.append(cleaned)
    return features[:8]


def is_valid_product(product: dict) -> bool:
    title = product["title"].strip()
    low = title.lower()
    if INVALID_TITLE_RE.match(title):
        return False
    if title in {label for label in SPEC_LABELS}:
        return False
    if len(title) < 8:
        return False
    if title[0].islower():
        return False
    if title.endswith(".") and not product.get("model"):
        return False
    if low in {"ağırlık", "ölçüler", "ambalajlı", "kapatise"}:
        return False
    if any(fragment in low for fragment in ("sahiptir", "çerçeveye", "kadar çıkış", "makinelerin kapı")):
        return False
    if any(k in low for k in ("filtre", "kurutucu", "karbon")) and (product["model"] or product["features"]):
        return True
    if len(product["specs"]) >= 3:
        return True
    if product["model"] and any(h in low for h in TITLE_HINTS):
        return True
    if len(product.get("features") or []) >= 4 and product["model"]:
        return True
    return False


def dedupe_products(products: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    order = []
    for product in products:
        base = re.sub(r"\s*-\s*gp[a-z0-9\s]+", "", product["title"], flags=re.I).strip().lower()
        base = re.sub(r"\s+", " ", base)
        if base not in grouped:
            grouped[base] = product
            order.append(base)
            continue
        current = grouped[base]
        current_score = len(current["specs"]) + (1 if current["model"] else 0)
        new_score = len(product["specs"]) + (1 if product["model"] else 0)
        if new_score > current_score:
            grouped[base] = product
    return [grouped[key] for key in order]


def page_lines_with_position(page):
    rows = []
    data = page.get_text("dict")
    for block in data["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            text = "".join(span["text"] for span in line["spans"]).strip()
            if not text:
                continue
            rows.append({"text": text, "y0": line["bbox"][1], "y1": line["bbox"][3]})
    rows.sort(key=lambda row: (row["y0"], row["text"]))
    return rows


def find_title_anchors(rows):
    anchors = []
    for idx, row in enumerate(rows):
        text = row["text"].strip()
        if is_title_line(text) or MODEL_RE.fullmatch(text):
            title = text
            model = extract_model(text, [text])
            if text.endswith("-") and idx + 1 < len(rows):
                nxt = rows[idx + 1]["text"].strip()
                if MODEL_RE.fullmatch(nxt):
                    title = f"{text.rstrip(' -').strip()} - {nxt}"
                    model = extract_model(title, [title, nxt])
            elif MODEL_RE.fullmatch(text) and idx + 1 < len(rows):
                nxt = rows[idx + 1]["text"].strip()
                if is_title_line(nxt):
                    title = f"{nxt.rstrip(' -').strip()} - {text}"
                    model = extract_model(title, [title, nxt])
            anchors.append({"title": title.rstrip(" -").strip(), "model": model, "y": row["y0"]})
    deduped = []
    seen_y = []
    for anchor in anchors:
        if any(abs(anchor["y"] - y) < 8 for y in seen_y):
            continue
        seen_y.append(anchor["y"])
        deduped.append(anchor)
    deduped.sort(key=lambda item: item["y"])
    return deduped


def lines_for_band(rows, y0: float, y1: float):
    texts = []
    for row in rows:
        if y0 <= row["y0"] < y1:
            texts.append(row["text"])
    return clean_lines("\n".join(texts))


def product_images_for_band(page, y0: float, y1: float):
    rects = []
    for img in page.get_images(full=True):
        xref = img[0]
        for rect in page.get_image_rects(xref):
            if rect.width < 90 or rect.height < 70:
                continue
            if rect.width > 260 or rect.height > 220:
                continue
            cy = (rect.y0 + rect.y1) / 2
            if y0 <= cy <= y1:
                rects.append(rect)
    if not rects:
        return []
    rects.sort(key=lambda r: (r.x0 + r.x1) / 2)
    return rects


def save_rect_as_webp(page, rect, out_path: Path, max_width: int):
    clip = fitz.Rect(rect)
    clip.x0 = max(0, clip.x0 - 4)
    clip.y0 = max(0, clip.y0 - 4)
    clip.x1 = min(page.rect.width, clip.x1 + 4)
    clip.y1 = min(page.rect.height, clip.y1 + 4)
    if clip.width < 20 or clip.height < 20:
        return False
    zoom = max(2.0, max_width / max(clip.width, 1))
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    if img.width < 2 or img.height < 2:
        return False
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, max(1, int(img.height * ratio))), Image.Resampling.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="WEBP", quality=82, method=6)
    return True


def save_product_images(page, y0: float, y1: float, asset_dir: Path, product_id: str):
    images = []
    image_rects = product_images_for_band(page, y0, y1)
    for img_idx, rect in enumerate(image_rects[:3]):
        filename = f"{product_id}-{img_idx + 1}.webp"
        if save_rect_as_webp(page, rect, asset_dir / filename, max_width=480 if img_idx else 320):
            images.append(f"assets/urunler/{asset_dir.name}/{filename}")
    if not images:
        filename = f"{product_id}-page.webp"
        if save_rect_as_webp(
            page,
            fitz.Rect(40, y0 + 20, page.rect.width - 40, max(y0 + 120, y1 - 10)),
            asset_dir / filename,
            max_width=420,
        ):
            images.append(f"assets/urunler/{asset_dir.name}/{filename}")
    return images


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


def clip_product_thumb(page, y0: float, y1: float, max_width: int = 180):
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


def save_custom_category_cover(doc, category: dict, out_path: Path):
    w, h = 612, 792
    img = Image.new("RGB", (w, h), (12, 16, 24))
    draw = ImageDraw.Draw(img)
    for i in range(-h, w + h, 34):
        draw.polygon([(i, 0), (i + 70, 0), (i + 70 + h, h), (i + h, h)], fill=(18, 24, 36))

    title_font = load_font(34, bold=True)
    sub_font = load_font(15)
    brand_font = load_font(22, bold=True)
    title = category["name"].upper()
    title_x, title_y = int(w * 0.34), 72
    draw.text((title_x, title_y), title, fill="white", font=title_font)
    bbox = draw.textbbox((title_x, title_y), title, font=title_font)
    draw.line([(title_x, bbox[3] + 8), (title_x + 290, bbox[3] + 8)], fill=(210, 32, 39), width=5)
    draw.text((title_x, bbox[3] + 24), "Profesyoneller için en iyi çözümler", fill=(220, 220, 220), font=sub_font)
    draw.text((title_x, bbox[3] + 46), "Best Solutions for Professionals", fill=(180, 180, 180), font=sub_font)

    if category["id"] == "hava-kurutucu-ve-filtreler":
        page49 = doc[48]
        page50 = doc[49]
        thumbs = [
            clip_product_thumb(page49, 110, 430, 200),
            clip_product_thumb(page49, 430, 820, 200),
            clip_product_thumb(page50, 100, 820, 200),
        ]
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
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(out_path, format="WEBP", quality=86, method=6)


def save_cover(page, out_path: Path):
    clip = fitz.Rect(0, 70, page.rect.width, page.rect.height - 70)
    pix = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), clip=clip, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="WEBP", quality=84, method=6)


def parse_manual_page_products(page, page_num: int, category_id: str, asset_dir: Path, product_counter: int):
    products = []
    for item in MANUAL_PAGE_PRODUCTS.get(page_num, []):
        product_counter += 1
        slug = slugify(item["model"] or item["title"])
        product_id = f"{category_id}-{product_counter:03d}-{slug}"
        images = save_product_images(page, item["y0"], item["y1"], asset_dir, product_id)
        if not images:
            continue
        product = apply_product_overrides(
            {
                "id": product_id,
                "title": item["title"],
                "model": item.get("model", ""),
                "features": item.get("features", []),
                "specs": item.get("specs", {}),
                "images": images,
                "thumb": images[0],
            }
        )
        products.append(product)
    return products, product_counter


def parse_page_products(page, page_num: int, category_id: str, asset_dir: Path, product_counter: int):
    if page_num in MANUAL_PAGE_PRODUCTS:
        return parse_manual_page_products(page, page_num, category_id, asset_dir, product_counter)

    rows = page_lines_with_position(page)
    anchors = find_title_anchors(rows)
    if not anchors:
        body_lines = clean_lines("\n".join(row["text"] for row in rows if row["y0"] > 70))
        specs = parse_specs(body_lines)
        features = parse_features(body_lines, specs)
        if len(specs) >= 4 or len(features) >= 4:
            product_counter += 1
            slug = slugify(category_id)
            product_id = f"{category_id}-{product_counter:03d}-{slug}"
            images = save_product_images(page, 80, page.rect.height - 40, asset_dir, product_id)
            if images:
                title = category_id.replace("-", " ").title()
                for line in body_lines:
                    if is_title_line(line):
                        title = line.rstrip(" -").strip()
                        break
                product = apply_product_overrides(
                    {
                        "id": product_id,
                        "title": title,
                        "model": extract_model(title, body_lines),
                        "features": features,
                        "specs": specs,
                        "images": images,
                        "thumb": images[0],
                    }
                )
                if is_valid_product(product):
                    return [product], product_counter
        return [], product_counter

    page_height = page.rect.height
    products = []

    for idx, anchor in enumerate(anchors):
        y0 = anchor["y"] - 5
        y1 = anchors[idx + 1]["y"] - 5 if idx + 1 < len(anchors) else page_height - 40
        body_lines = lines_for_band(rows, y0 + 18, y1)
        body_lines = [line for line in body_lines if line != anchor["title"]]
        specs = parse_specs(body_lines)
        features = parse_features(body_lines, specs)
        model = anchor["model"] or extract_model(anchor["title"], body_lines)

        product_counter += 1
        slug = slugify(model or anchor["title"])
        product_id = f"{category_id}-{product_counter:03d}-{slug}"
        images = save_product_images(page, y0 + 20, y1 - 10, asset_dir, product_id)
        if not images:
            continue

        title = anchor["title"]
        if model and model.upper() not in title.upper():
            title = f"{title.rstrip(' -')} - {model}"

        product = apply_product_overrides(
            {
                "id": product_id,
                "title": title,
                "model": model,
                "features": features,
                "specs": specs,
                "images": images,
                "thumb": images[0],
            }
        )
        products.append(product)

    products = dedupe_products([p for p in products if is_valid_product(p)])
    return products, product_counter


def build_catalog():
    if SITE_ASSETS.exists():
        shutil.rmtree(SITE_ASSETS)
    SITE_ASSETS.mkdir(parents=True)

    doc = fitz.open(PDF_PATH)
    catalog = {"categories": []}
    total_products = 0

    for category in CATEGORIES:
        cat_dir = SITE_ASSETS / category["id"]
        cat_dir.mkdir(parents=True, exist_ok=True)
        cover = None
        cover_file = f"{category['id']}-cover.webp"
        if category.get("custom_cover"):
            save_custom_category_cover(doc, category, cat_dir / cover_file)
            cover = f"assets/urunler/{category['id']}/{cover_file}"
        elif category.get("cover_page"):
            page = doc[category["cover_page"] - 1]
            save_cover(page, cat_dir / cover_file)
            cover = f"assets/urunler/{category['id']}/{cover_file}"

        products = []
        counter = 0
        for page_num in category["product_pages"]:
            page = doc[page_num - 1]
            parsed, counter = parse_page_products(
                page, page_num, category["id"], cat_dir, counter
            )
            products.extend(parsed)

        total_products += len(products)
        catalog["categories"].append(
            {
                "id": category["id"],
                "name": category["name"],
                "description": category["description"],
                "cover": cover,
                "products": products,
            }
        )

    doc.close()
    catalog_path = SITE_ASSETS / "catalog.json"
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Catalog built: {len(catalog['categories'])} categories, {total_products} products")
    return catalog


if __name__ == "__main__":
    build_catalog()
