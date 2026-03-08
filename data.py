import json
import os
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)
foydalanuvchilar_fayli = 'users.json'
malumotlar_fayli = 'data.json'


def standart_kategoriyalar() -> Dict[str, Any]:
    return {
        "matnlar": {
            "boshlash": "🍽 <b>Karimqul Ota Choyhonasi</b>ga xush kelibsiz!\n\n"
                        "🏪 An'anaviy O'zbek taomlari va zamonaviy taomlar!\n\n"
                        "📋 Menyuni ko'rish uchun «🍽 Menyu» tugmasini bosing.",
            "telefon_sorash": "📱 Telefon raqamingizni yuboring:",
            "telefon_url": "📱 Telefon raqamni yuborish",
            "telefon_xato": "❌ Iltimos, telefon raqamingizni yuboring!",
            "manzil_sorash": "📍 Yetkazib berish manzilingizni kiriting:",
            "manzil_url": "📍 Manzilni yuborish",
            "manzil_xato": "❌ Iltimos, to'liq manzil kiriting!",
            "royxat_muvaffaqiyat": "✅ Ro'yxatga muvaffaqiyatli qo'shildingiz!\n\n🍽 Endi menyumizdan taom tanlashingiz mumkin!",
            "royxat_xato": "❌ Ro'yxatga qo'shilmadi!",
            "asosiy_menyu": "🏠 <b>Asosiy menyu</b>\n\n🍽 O'zingizga yoqqan bo'limni tanlang:",
            "kategoriya_tanlash": "📋 <b>Menyu — Karimqul Ota Choyhonasi</b>\n\nKategoriyani tanlang:",
            "savat_bosh": "🛒 Savatingiz bo'sh\n\n🍽 Menyudan taom tanlang!",
            "sozlamalar_menyu": "⚙️ Sozlamalar bo'limi:\n\nKerakli amalni tanlang.",
            "buyurtma_qabul": "✅ Buyurtmangiz qabul qilindi!",
            "admin_xush": "👨‍💼 Admin panelga xush kelibsiz!",
            "aloqa_malumot": "📞 <b>Biz bilan bog'lanish:</b>\n\n"
                             "📱 Telefon: +998 91 802 86 06\n"
                             "📷 Instagram: @Sae_byok\n"
                             "📍 Manzil: Guliston shahar, Sayxun ko'chasi 3A\n"
                             "🕐 Ish vaqti: 08:00 — 23:00",
            "haqida_malumot": "🏪 <b>Karimqul Ota Choyhonasi haqida:</b>\n\n"
                              "🍽 An'anaviy O'zbek milliy taomlari!\n\n"
                              "🌟 Bizning afzalliklarimiz:\n"
                              "• 🥩 Yangi va sifatli go'sht\n"
                              "• 👨‍🍳 Tajribali oshpazlar\n"
                              "• 🏡 Qulay va shinam muhit\n"
                              "• 💰 Hamyonbop narxlar\n\n"
                              "📋 11 ta kategoriyada 83 turdagi taomlar!\n\n"
                              "📷 Instagram: @_karimqulotachoyxonasi_",
            "orqaga": "⬅️ Orqaga",
            "parol": "123456789"
        },
        "menyu": {
            "asosiy": {
                "dokon": "🍽 Menyu",
                "savat": "🛒 Savat",
                "buyurtmalar": "📖 Buyurtmalarim",
                "aloqa": "📞 Aloqa",
                "haqida": "ℹ️ Biz haqimizda",
                "sozlamalar": "⚙️ Sozlamalar"
            },
            "admin": {
                "buyurtmalar": "📋 Buyurtmalar",
                "foydalanuvchilar": "👥 Foydalanuvchilar",
                "statistika": "📊 Statistika",
                "mahsulotlar": "🍔 Mahsulotlar",
                "sozlamalar": "⚙️ Admin sozlamalari"
            },
            "foydalanuvchi_amallar": {
                "qayta_royxat": "♻️ Qayta ro'yxatdan o'tish",
                "buyurtma_bekor": "❌ Buyurtmani bekor qilish"
            },
            "savat": {
                "tolov": "💳 Buyurtma berish",
                "tozalash": "🗑 Savatni tozalash"
            },
            "holat": {
                "pending": "⏳ kutilmoqda",
                "accepted": "✅ qabul qilindi",
                "processing": "🔄 tayyorlanmoqda",
                "completed": "✔️ yakunlangan",
                "cancelled": "❌ bekor qilingan"
            }
        },
        "kategoriyalar": {
            "birinchi_taom": {
                "nomi": "🍲 Birinchi taomlar", "rasm": "img/soups.webp",
                "mahsulotlar": {
                    "qatiqlosh": {"nomi": "Qatiqlosh", "tavsif": "Qatiqli sho'rva, guruch va go'sht bilan", "narx": 18000, "id": 1},
                    "mol_shurva": {"nomi": "Mol go'shiga sho'rva", "tavsif": "Mol go'shtidan an'anaviy sho'rva", "narx": 40000, "id": 2},
                    "mol_shurva_700": {"nomi": "Mol go'shiga sho'rva 700g", "tavsif": "Mol go'shtli sho'rva, kichik porsiya", "narx": 33000, "id": 3},
                    "tushonka": {"nomi": "Tushonka mol go'shiga", "tavsif": "Mol go'shtidan tayyorlangan tushonka", "narx": 45000, "id": 4},
                    "tushonka_700": {"nomi": "Tushonka mol go'shiga 700g", "tavsif": "Mol go'shtli tushonka, kichik porsiya", "narx": 35000, "id": 5},
                    "mastava": {"nomi": "Mastava Toshkent", "tavsif": "Toshkent uslubidagi mastava", "narx": 30000, "id": 6},
                    "ilik_shurva": {"nomi": "Ilik sho'rva mol go'shiga", "tavsif": "Mol go'shtidan ilik sho'rva", "narx": 60000, "id": 7},
                    "quy_shurva": {"nomi": "Qo'y go'shiga sho'rva", "tavsif": "Qo'y go'shtidan sho'rva", "narx": 45000, "id": 8},
                    "bulyon": {"nomi": "Bulyon", "tavsif": "Engil go'shtli bulyon", "narx": 4000, "id": 9},
                    "kuza_shurva": {"nomi": "Ko'za sho'rva mol go'shiga", "tavsif": "Sopol ko'zada mol go'shtli sho'rva", "narx": 50000, "id": 10},
                    "kuza_shurva_700": {"nomi": "Ko'za sho'rva 700g", "tavsif": "Sopol ko'zada sho'rva, kichik porsiya", "narx": 40000, "id": 11}
                }
            },
            "ikkinchi_taom": {
                "nomi": "🍖 Ikkinchi taomlar", "rasm": "img/main_dishes.webp",
                "mahsulotlar": {
                    "jiz": {"nomi": "Jiz mol go'shiga", "tavsif": "Mol go'shtidan jiz", "narx": 210000, "id": 12},
                    "osh": {"nomi": "Osh (Palov) 1×1", "tavsif": "An'anaviy O'zbek oshi", "narx": 300000, "id": 13},
                    "andijon_jiz": {"nomi": "Andijoncha jiz", "tavsif": "Andijon uslubida tayyorlangan jiz", "narx": 210000, "id": 14},
                    "qozon_kabob": {"nomi": "Qozon kabob qo'y go'shiga", "tavsif": "Qozonda qo'y go'shtli kabob", "narx": 210000, "id": 15},
                    "qizilcha": {"nomi": "Qizilcha (qo'zichoq go'shti)", "tavsif": "Qo'zichoq go'shtidan qizilcha", "narx": 210000, "id": 16},
                    "kareyka": {"nomi": "Kareyka qo'y go'shiga", "tavsif": "Qo'y go'shtidan kareyka", "narx": 230000, "id": 17},
                    "bifshteks": {"nomi": "Bifshteks", "tavsif": "Mol go'shtidan bifshteks", "narx": 30000, "id": 18},
                    "grechka": {"nomi": "Grechka", "tavsif": "Grechka bo'tqa, go'sht bilan", "narx": 30000, "id": 19}
                }
            },
            "shashliklar": {
                "nomi": "🔥 Shashliklar", "rasm": "img/shashlik.webp",
                "mahsulotlar": {
                    "zomin_kuzi": {"nomi": "Zomin ko'zi", "tavsif": "Maxsus zomin uslubidagi katta kabob", "narx": 61000, "id": 20},
                    "gizhduvan": {"nomi": "G'ijduvon", "tavsif": "An'anaviy G'ijduvon kabob", "narx": 21000, "id": 21},
                    "katta_gizhduvan": {"nomi": "Katta G'ijduvon", "tavsif": "Katta hajmdagi G'ijduvon kabob", "narx": 27000, "id": 22},
                    "parmuda_k": {"nomi": "Parmuda kabob", "tavsif": "An'anaviy parmuda kabob", "narx": 41000, "id": 23},
                    "napoleon": {"nomi": "Napoleon", "tavsif": "Napoleon uslubida kabob", "narx": 34000, "id": 24},
                    "kuskavoy": {"nomi": "Kuskavoy mol/qo'y go'shti", "tavsif": "Mol/qo'y go'shtidan kuskavoy", "narx": 34000, "id": 25},
                    "mol_qiymali": {"nomi": "Mol go'shti qiymali", "tavsif": "Mol go'shti qiymasidan kabob", "narx": 18000, "id": 26},
                    "kavkaz_tovuq": {"nomi": "Kavkaz tovuqi", "tavsif": "Kavkaz uslubida tovuq kabob", "narx": 36000, "id": 27},
                    "jigar": {"nomi": "Jigar", "tavsif": "Jigar kabob", "narx": 16000, "id": 28},
                    "dumba": {"nomi": "Dumba", "tavsif": "Qovurilgan dumba", "narx": 34000, "id": 29},
                    "tovuq_kabob": {"nomi": "Tovuq kabob", "tavsif": "Tovuq go'shtidan kabob", "narx": 13000, "id": 30},
                    "sabzavot_k": {"nomi": "Sabzavot kabob", "tavsif": "Pomidor va sabzavotli kabob", "narx": 12000, "id": 31}
                }
            },
            "tovuq": {
                "nomi": "🍗 Tovuq taomlar", "rasm": "img/chicken.webp",
                "mahsulotlar": {
                    "grill": {"nomi": "Grill tovuq (butun)", "tavsif": "Butun tovuq grilda tayyorlangan", "narx": 70000, "id": 32},
                    "kfs": {"nomi": "KFS", "tavsif": "Qovurilgan tovuq (KFS uslubida)", "narx": 85000, "id": 33}
                }
            },
            "baliq": {
                "nomi": "🐟 Baliq", "rasm": "img/fish.webp",
                "mahsulotlar": {
                    "dengiz": {"nomi": "Dengiz baliqi (kg)", "tavsif": "Dengiz baliqi, 1 kg", "narx": 90000, "id": 34},
                    "hovuz": {"nomi": "Hovuz baliqi (kg)", "tavsif": "Hovuz baliqi, 1 kg", "narx": 120000, "id": 35},
                    "sazan": {"nomi": "Sazan sousda", "tavsif": "Sousda pishirilgan sazan baliqi", "narx": 120000, "id": 36}
                }
            },
            "uyghur": {
                "nomi": "🍜 Uyg'ur oshxonasi", "rasm": "img/uyghur.webp",
                "mahsulotlar": {
                    "lagmon": {"nomi": "Lagmon", "tavsif": "Qo'lda tayyorlangan ugra, go'sht, sabzavotlar", "narx": 35000, "id": 37},
                    "qovurilgan_lagmon": {"nomi": "Qovurilgan lagmon", "tavsif": "Qovurilgan uslubda lagmon", "narx": 35000, "id": 38},
                    "ganfan": {"nomi": "Ganfan", "tavsif": "Guruch, go'sht va sabzavotlar", "narx": 35000, "id": 39},
                    "manti": {"nomi": "Manti (dona)", "tavsif": "Go'shtli manti, 1 dona", "narx": 8000, "id": 40},
                    "fure": {"nomi": "Fure go'sht", "tavsif": "Achchiq uslubda tayyorlangan go'sht", "narx": 70000, "id": 41},
                    "achchiq_gosht": {"nomi": "Achchiq go'sht", "tavsif": "Achchiq ziravorlar bilan go'sht", "narx": 70000, "id": 42},
                    "sunboro": {"nomi": "Sunboro", "tavsif": "Uyg'ur uslubida sunboro", "narx": 60000, "id": 43}
                }
            },
            "somsa": {
                "nomi": "🫓 Somsa va Non", "rasm": "img/breads.webp",
                "mahsulotlar": {
                    "gosht_somsa": {"nomi": "Go'shtli somsa", "tavsif": "An'anaviy tandir somsa, go'shtli", "narx": 10000, "id": 44},
                    "tomchi": {"nomi": "Tomchi somsa", "tavsif": "Tomchi shaklidagi maxsus somsa", "narx": 13000, "id": 45},
                    "parmuda_s": {"nomi": "Parmuda somsa", "tavsif": "Parmuda uslubidagi katta somsa", "narx": 34000, "id": 46},
                    "kartoshka_s": {"nomi": "Kartoshkali somsa", "tavsif": "Kartoshka somsasi", "narx": 6000, "id": 47},
                    "ismaloq_s": {"nomi": "Ismaloqli somsa", "tavsif": "Ismaloq somsasi", "narx": 6000, "id": 48},
                    "shirmoy": {"nomi": "Shirmoy non", "tavsif": "Tandirda shirmoy non", "narx": 7000, "id": 49},
                    "patir": {"nomi": "Patir non", "tavsif": "Tandirda patir non", "narx": 7000, "id": 50}
                }
            },
            "salatlar": {
                "nomi": "🥗 Salatlar", "rasm": "img/salads.webp",
                "mahsulotlar": {
                    "gloriya": {"nomi": "Gloriya", "tavsif": "Mayonezli salat, go'sht va sabzavotlar", "narx": 45000, "id": 51},
                    "kapriz": {"nomi": "Kapriz", "tavsif": "Mayonezli maxsus salat", "narx": 40000, "id": 52},
                    "erkak_kapriz": {"nomi": "Erkak kaprizlari", "tavsif": "Mayonezli salat, go'sht bilan", "narx": 40000, "id": 53},
                    "sultan": {"nomi": "Sultan", "tavsif": "Mayonezli sultan salati", "narx": 40000, "id": 54},
                    "firmeniy": {"nomi": "Firmenniy salat", "tavsif": "Choyhona maxsus salati", "narx": 50000, "id": 55},
                    "sezar": {"nomi": "Sezar", "tavsif": "Tovuq, parmezan, krutonlar, sous", "narx": 45000, "id": 56},
                    "bodring_gosht": {"nomi": "Bodring go'sht bilan", "tavsif": "Soyali sous, bodring va go'sht", "narx": 48000, "id": 57},
                    "xe": {"nomi": "Xe mol go'shtidan", "tavsif": "Koreyscha xe salati", "narx": 45000, "id": 58},
                    "bahor": {"nomi": "Bahor salati", "tavsif": "Yog'li yozgi salat, yangi sabzavotlar", "narx": 28000, "id": 59},
                    "grek": {"nomi": "Grek salati", "tavsif": "Pomidor, bodring, zaytun, feta pishloq", "narx": 40000, "id": 60},
                    "shakarob": {"nomi": "Shakarob", "tavsif": "Pomidor, piyoz, ko'katlar", "narx": 15000, "id": 61},
                    "achichuk": {"nomi": "Achichuk", "tavsif": "Pomidor, piyoz, qalampir", "narx": 15000, "id": 62},
                    "yangi_salat": {"nomi": "Yangi (svejiy) salat", "tavsif": "Yangi sabzavotlardan tayyorlangan", "narx": 20000, "id": 63},
                    "norin_kg": {"nomi": "Norin (kg)", "tavsif": "An'anaviy norin, 1 kilogramm", "narx": 100000, "id": 64},
                    "norin_p": {"nomi": "Norin (porsiya)", "tavsif": "An'anaviy norin, 1 porsiya", "narx": 35000, "id": 65}
                }
            },
            "shirinliklar": {
                "nomi": "🍰 Shirinliklar", "rasm": "img/desserts.webp",
                "mahsulotlar": {
                    "tort": {"nomi": "Tort", "tavsif": "Kunlik tayyorlangan tort bo'lagi", "narx": 15000, "id": 66},
                    "pirojniy": {"nomi": "Pirojniy", "tavsif": "Choyhona maxsus pirojniysi", "narx": 12000, "id": 67},
                    "muzqaymoq": {"nomi": "Muzqaymoq", "tavsif": "Vanilli muzqaymoq", "narx": 10000, "id": 68},
                    "halvo": {"nomi": "Halvo", "tavsif": "O'zbek holvasi", "narx": 8000, "id": 69}
                }
            },
            "issiq_ichimlik": {
                "nomi": "☕ Issiq ichimliklar", "rasm": "img/hot_drinks.webp",
                "mahsulotlar": {
                    "choy_limon_k": {"nomi": "Choy limon katta", "tavsif": "Limonli choy, katta choynak", "narx": 20000, "id": 70},
                    "choy_limon_ki": {"nomi": "Choy limon kichik", "tavsif": "Limonli choy, kichik choynak", "narx": 10000, "id": 71},
                    "qora_choy": {"nomi": "Qora choy", "tavsif": "An'anaviy qora choy", "narx": 4000, "id": 72},
                    "kok_choy": {"nomi": "Ko'k choy", "tavsif": "An'anaviy ko'k choy", "narx": 4000, "id": 73}
                }
            },
            "ichimliklar": {
                "nomi": "🥤 Sovuq ichimliklar", "rasm": "img/drinks.webp",
                "mahsulotlar": {
                    "pepsi": {"nomi": "Pepsi 0.25L", "tavsif": "Sovuq Pepsi ichimlik", "narx": 5000, "id": 74},
                    "fanta_025": {"nomi": "Fanta 0.25L", "tavsif": "Sovuq Fanta ichimlik", "narx": 5000, "id": 75},
                    "fanta_15": {"nomi": "Fanta 1.5L", "tavsif": "Katta hajmdagi Fanta", "narx": 17000, "id": 76},
                    "flash_k": {"nomi": "Flash (kichik)", "tavsif": "Energetik ichimlik, kichik", "narx": 9000, "id": 77},
                    "flash_ka": {"nomi": "Flash (katta)", "tavsif": "Energetik ichimlik, katta", "narx": 13000, "id": 78},
                    "adrenaline_k": {"nomi": "Adrenaline (kichik)", "tavsif": "Energetik ichimlik, kichik", "narx": 12000, "id": 79},
                    "adrenaline_ka": {"nomi": "Adrenaline (katta)", "tavsif": "Energetik ichimlik, katta", "narx": 15000, "id": 80},
                    "borjomi": {"nomi": "Borjomi", "tavsif": "Mineral suv Borjomi", "narx": 19000, "id": 81},
                    "chortoq": {"nomi": "Chortoq suvi", "tavsif": "Chortoq mineral suvi", "narx": 11000, "id": 82},
                    "suv_15": {"nomi": "Suv 1.5L", "tavsif": "Toza ichimlik suvi, katta", "narx": 7000, "id": 83}
                }
            }
        },
        "buyurtmalar": [],
        "savatlar": {},
        "keyingi_buyurtma_id": 1
    }


def malumot_yuklash(fayl: str) -> Dict[str, Any]:
    if 'users' in fayl.lower():
        boshlangich = {"foydalanuvchilar": [], "adminlar": []}
    else:
        boshlangich = standart_kategoriyalar()

    try:
        if not os.path.exists(fayl):
            with open(fayl, 'w', encoding='utf-8') as f:
                json.dump(boshlangich, f, ensure_ascii=False, indent=2)
            logger.info(f"Yangi fayl yaratildi: {fayl}")
            return boshlangich

        with open(fayl, 'r', encoding='utf-8') as f:
            malumot = json.load(f)

        if not malumot:
            malumot = boshlangich

        if 'users' in fayl.lower():
            malumot.setdefault('foydalanuvchilar', [])
            malumot.setdefault('adminlar', [])

        if 'data' in fayl.lower():
            standart = standart_kategoriyalar()
            for kalit in ['kategoriyalar', 'matnlar', 'menyu', 'buyurtmalar', 'savatlar', 'keyingi_buyurtma_id']:
                if kalit not in malumot:
                    logger.warning(f"{fayl} faylida '{kalit}' kaliti yo'q, qo'shilmoqda")
                    if kalit == 'buyurtmalar':
                        malumot[kalit] = []
                    elif kalit == 'keyingi_buyurtma_id':
                        malumot[kalit] = 1
                    else:
                        malumot[kalit] = standart.get(kalit, {})

        return malumot

    except json.JSONDecodeError as e:
        logger.error(f"JSON xatosi {fayl} faylini o'qishda: {e}")
        return boshlangich
    except Exception as e:
        logger.error(f"Ma'lumotlar bazasini yuklashda xatolik: {e}")
        return boshlangich


def malumot_saqlash(malumot: Dict[str, Any], fayl: str) -> bool:
    try:
        with open(fayl, 'w', encoding='utf-8') as f:
            json.dump(malumot, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Ma'lumotlar bazasini saqlashda xatolik: {e}")
        return False


def foydalanuvchi_olish(foydalanuvchi_id: int) -> Optional[Dict[str, Any]]:
    malumot = malumot_yuklash(foydalanuvchilar_fayli)
    return next((f for f in malumot.get("foydalanuvchilar", []) if f["id"] == foydalanuvchi_id), None)


def foydalanuvchi_saqlash(foydalanuvchi_id: int, foydalanuvchi_nomi: str, toliq_ism: str,
                          telefon: str = None, manzil: str = None) -> bool:
    malumot = malumot_yuklash(foydalanuvchilar_fayli)
    hozir = datetime.now().isoformat()

    foydalanuvchi = {
        "id": foydalanuvchi_id,
        "foydalanuvchi_nomi": foydalanuvchi_nomi,
        "toliq_ism": toliq_ism,
        "telefon": telefon,
        "manzil": manzil,
        "royxat_vaqti": hozir,
        "oxirgi_faollik": hozir
    }

    for idx, f in enumerate(malumot.get("foydalanuvchilar", [])):
        if f["id"] == foydalanuvchi_id:
            malumot["foydalanuvchilar"][idx] = foydalanuvchi
            return malumot_saqlash(malumot, foydalanuvchilar_fayli)

    malumot["foydalanuvchilar"].append(foydalanuvchi)
    return malumot_saqlash(malumot, foydalanuvchilar_fayli)


def foydalanuvchi_tozalash(user_id: int) -> bool:
    data = malumot_yuklash(foydalanuvchilar_fayli)
    user = next((u for u in data["foydalanuvchilar"] if u["id"] == user_id), None)

    if not user:
        user = {
            "id": user_id,
            "foydalanuvchi_nomi": None,
            "toliq_ism": None,
            "telefon": None,
            "manzil": None,
            "royxat_vaqti": datetime.now().isoformat(),
            "oxirgi_faollik": datetime.now().isoformat()
        }
        data["foydalanuvchilar"].append(user)

    user["telefon"] = None
    user["manzil"] = None
    return malumot_saqlash(data, foydalanuvchilar_fayli)


def admin_tekshir(foydalanuvchi_id: int) -> bool:
    malumot = malumot_yuklash(foydalanuvchilar_fayli)
    return foydalanuvchi_id in malumot.get("adminlar", [])


def admin_saqlash(user_id: int) -> bool:
    data = malumot_yuklash(foydalanuvchilar_fayli)
    if user_id not in data["adminlar"]:
        data["adminlar"].append(user_id)
        return malumot_saqlash(data, foydalanuvchilar_fayli)
    return True


def kategoriyalar_olish() -> Dict[str, Dict[str, Any]]:
    malumot = malumot_yuklash(malumotlar_fayli)
    return malumot.get("kategoriyalar", standart_kategoriyalar().get("kategoriyalar", {}))


def matn_olish(kalit: str) -> str:
    malumot = malumot_yuklash(malumotlar_fayli)
    return malumot.get("matnlar", {}).get(kalit, kalit)


def menyu_olish(menyu_turi: str) -> Dict[str, str]:
    malumot = malumot_yuklash(malumotlar_fayli)
    return malumot.get("menyu", {}).get(menyu_turi, {})


def savat_olish(foydalanuvchi_id: int) -> Dict[str, Any]:
    malumot = malumot_yuklash(malumotlar_fayli)
    return malumot.get("savatlar", {}).get(str(foydalanuvchi_id), {})


def savat_qoshish(foydalanuvchi_id: int, kategoriya: str, mahsulot_kaliti: str, miqdor: int = 1) -> bool:
    malumot = malumot_yuklash(malumotlar_fayli)
    savat_kaliti = str(foydalanuvchi_id)

    if savat_kaliti not in malumot["savatlar"]:
        malumot["savatlar"][savat_kaliti] = {}

    element_kaliti = f"{kategoriya}:{mahsulot_kaliti}"

    if element_kaliti in malumot["savatlar"][savat_kaliti]:
        malumot["savatlar"][savat_kaliti][element_kaliti]["quantity"] += miqdor
    else:
        kategoriyalar = malumot["kategoriyalar"][kategoriya]
        mahsulot = kategoriyalar["mahsulotlar"][mahsulot_kaliti]
        malumot["savatlar"][savat_kaliti][element_kaliti] = {
            "category": kategoriya,
            "product_key": mahsulot_kaliti,
            "name": mahsulot["nomi"],
            "price": mahsulot["narx"],
            "quantity": miqdor
        }

    return malumot_saqlash(malumot, malumotlar_fayli)


def savat_miqdor_yangilash(foydalanuvchi_id: int, kategoriya: str, mahsulot_kaliti: str, ozgartirish: int) -> bool:
    """Savatdagi mahsulot miqdorini +/- qilish. 0 bo'lsa o'chiriladi."""
    malumot = malumot_yuklash(malumotlar_fayli)
    savat_kaliti = str(foydalanuvchi_id)
    element_kaliti = f"{kategoriya}:{mahsulot_kaliti}"

    savat = malumot.get("savatlar", {}).get(savat_kaliti, {})
    if element_kaliti not in savat:
        return False

    yangi_miqdor = savat[element_kaliti]["quantity"] + ozgartirish
    if yangi_miqdor <= 0:
        del malumot["savatlar"][savat_kaliti][element_kaliti]
    else:
        malumot["savatlar"][savat_kaliti][element_kaliti]["quantity"] = yangi_miqdor

    return malumot_saqlash(malumot, malumotlar_fayli)


def savatdan_ochirish(foydalanuvchi_id: int, kategoriya: str, mahsulot_kaliti: str) -> bool:
    malumot = malumot_yuklash(malumotlar_fayli)
    savat_kaliti = str(foydalanuvchi_id)

    if savat_kaliti in malumot["savatlar"]:
        element_kaliti = f"{kategoriya}:{mahsulot_kaliti}"
        if element_kaliti in malumot["savatlar"][savat_kaliti]:
            del malumot["savatlar"][savat_kaliti][element_kaliti]
            return malumot_saqlash(malumot, malumotlar_fayli)
    return False


def savat_tozalash(foydalanuvchi_id: int) -> bool:
    malumot = malumot_yuklash(malumotlar_fayli)
    savat_kaliti = str(foydalanuvchi_id)

    if savat_kaliti in malumot["savatlar"]:
        malumot["savatlar"][savat_kaliti] = {}
        return malumot_saqlash(malumot, malumotlar_fayli)
    return False


def savat_jami(foydalanuvchi_id: int) -> int:
    savat = savat_olish(foydalanuvchi_id)
    return sum(el["price"] * el["quantity"] for el in savat.values())


def savat_soni(foydalanuvchi_id: int) -> int:
    """Savatdagi mahsulotlar umumiy soni."""
    savat = savat_olish(foydalanuvchi_id)
    return sum(el["quantity"] for el in savat.values())


def buyurtma_yaratish(foydalanuvchi_id: int, izoh: str = "") -> Optional[Dict[str, Any]]:
    malumot = malumot_yuklash(malumotlar_fayli)
    savat = savat_olish(foydalanuvchi_id)

    if not savat:
        return None

    buyurtma = {
        "id": malumot.get("keyingi_buyurtma_id", 1),
        "user_id": foydalanuvchi_id,
        "items": savat.copy(),
        "total": savat_jami(foydalanuvchi_id),
        "status": "pending",
        "izoh": izoh,
        "created_at": datetime.now().isoformat()
    }

    malumot["buyurtmalar"].append(buyurtma)
    malumot["keyingi_buyurtma_id"] = malumot.get("keyingi_buyurtma_id", 1) + 1

    if malumot_saqlash(malumot, malumotlar_fayli):
        savat_tozalash(foydalanuvchi_id)
        return buyurtma
    return None


def foydalanuvchi_buyurtmalari(foydalanuvchi_id: int) -> List[Dict[str, Any]]:
    malumot = malumot_yuklash(malumotlar_fayli)
    return [
        buyurtma for buyurtma in malumot.get("buyurtmalar", [])
        if buyurtma.get("user_id") == foydalanuvchi_id
    ]


def barcha_buyurtmalar() -> List[Dict[str, Any]]:
    malumot = malumot_yuklash(malumotlar_fayli)
    return malumot.get("buyurtmalar", [])


def buyurtma_olish(buyurtma_id: int) -> Optional[Dict[str, Any]]:
    malumot = malumot_yuklash(malumotlar_fayli)
    return next(
        (buyurtma for buyurtma in malumot.get("buyurtmalar", []) if buyurtma.get("id") == buyurtma_id),
        None
    )


def buyurtma_holat_yangilash(buyurtma_id: int, holat: str) -> bool:
    malumot = malumot_yuklash(malumotlar_fayli)

    for buyurtma in malumot.get("buyurtmalar", []):
        if buyurtma.get("id") == buyurtma_id:
            buyurtma["status"] = holat
            return malumot_saqlash(malumot, malumotlar_fayli)
    return False


def buyurtma_bekor_qilish(buyurtma_id: int, foydalanuvchi_id: int) -> bool:
    malumot = malumot_yuklash(malumotlar_fayli)
    buyurtmalar = malumot.get("buyurtmalar", [])

    for idx, buyurtma in enumerate(list(buyurtmalar)):
        if (buyurtma.get("id") == buyurtma_id and
                buyurtma.get("user_id") == foydalanuvchi_id):
            if buyurtma.get("status") == "completed":
                return False
            del malumot["buyurtmalar"][idx]
            return malumot_saqlash(malumot, malumotlar_fayli)

    return False


def get_categories() -> Dict[str, Dict[str, Any]]:
    malumot = malumot_yuklash(malumotlar_fayli)
    kategoriyalar = malumot.get("kategoriyalar", {})

    yangilangan = {}
    for key, kat in kategoriyalar.items():
        yangilangan[key] = {
            "name": kat.get("nomi", ""),
            "image": kat.get("rasm", ""),
            "products": {}
        }

        for prod_key, prod in kat.get("mahsulotlar", {}).items():
            yangilangan[key]["products"][prod_key] = {
                "name": prod.get("nomi", ""),
                "description": prod.get("tavsif", ""),
                "price": prod.get("narx", 0),
                "id": prod.get("id", 0)
            }

    return yangilangan


def get_category_products(category: str) -> Dict[str, Dict[str, Any]]:
    categories = get_categories()
    return categories.get(category, {}).get("products", {})


def get_product(category: str, product_key: str) -> Optional[Dict[str, Any]]:
    products = get_category_products(category)
    return products.get(product_key)


def _generate_product_key(name: str, existing_keys: List[str]) -> str:
    base = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
    base = base or "product"
    candidate = base
    counter = 1
    while candidate in existing_keys:
        candidate = f"{base}_{counter}"
        counter += 1
    return candidate


def _get_next_product_id(data: Dict[str, Any]) -> int:
    max_id = 0
    for category in data.get("kategoriyalar", {}).values():
        for product in category.get("mahsulotlar", {}).values():
            max_id = max(max_id, product.get("id", 0))
    return max_id + 1


def update_product_field(category_key: str, product_key: str, field: str, value: Any) -> bool:
    field_map = {"name": "nomi", "description": "tavsif", "price": "narx"}
    uzbek_field = field_map.get(field)
    if not uzbek_field:
        return False

    data = malumot_yuklash(malumotlar_fayli)
    category = data.get("kategoriyalar", {}).get(category_key)
    if not category:
        return False

    product = category.get("mahsulotlar", {}).get(product_key)
    if not product:
        return False

    product[uzbek_field] = value
    return malumot_saqlash(data, malumotlar_fayli)


def add_product(category_key: str, name: str, description: str, price: int) -> Optional[Dict[str, Any]]:
    data = malumot_yuklash(malumotlar_fayli)
    category = data.get("kategoriyalar", {}).get(category_key)
    if not category:
        return None

    mahsulotlar = category.setdefault("mahsulotlar", {})
    product_key = _generate_product_key(name, list(mahsulotlar.keys()))
    new_product = {
        "nomi": name,
        "tavsif": description,
        "narx": price,
        "id": _get_next_product_id(data)
    }
    mahsulotlar[product_key] = new_product

    if malumot_saqlash(data, malumotlar_fayli):
        return {"key": product_key, **new_product}
    return None


def delete_product(category_key: str, product_key: str) -> bool:
    data = malumot_yuklash(malumotlar_fayli)
    category = data.get("kategoriyalar", {}).get(category_key)
    if not category:
        return False

    mahsulotlar = category.get("mahsulotlar", {})
    if product_key not in mahsulotlar:
        return False

    del mahsulotlar[product_key]
    return malumot_saqlash(data, malumotlar_fayli)


def narx_formatlash(narx: int) -> str:
    """Narxni formatlash: 25000 -> '25 000'"""

    return f"{narx:,}".replace(",", " ")
