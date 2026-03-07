import logging
from typing import Dict, Any

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardButton, InlineKeyboardMarkup,
    FSInputFile, CallbackQuery
)

from data import (
    foydalanuvchi_olish, foydalanuvchi_saqlash, matn_olish, menyu_olish,
    kategoriyalar_olish, savat_olish, foydalanuvchi_buyurtmalari,
    admin_tekshir, foydalanuvchi_tozalash, get_categories,
    get_category_products, get_product, savat_qoshish, buyurtma_yaratish,
    savat_tozalash, buyurtma_bekor_qilish, savat_miqdor_yangilash,
    savat_soni, savat_jami, narx_formatlash
)

from admin import admin_menyuni_korsat

logger = logging.getLogger(__name__)

rr = Router()


class RoyxatHolatlari(StatesGroup):
    telefon = State()
    manzil = State()


class BuyurtmaHolati(StatesGroup):
    izoh = State()


# ─── Yordamchi funksiyalar ───────────────────────────────────

def juftlik_bolish(elementlar, ustun=2):
    """Elementlarni 2 tadan qator qilib bo'lish."""
    return [elementlar[i:i + ustun] for i in range(0, len(elementlar), ustun)]


def holat_formatlash(holat: str) -> str:
    return menyu_olish("holat").get(holat, holat)


def buyurtma_xulosa_yaratish(buyurtma: Dict[str, Any]) -> str:
    holat_matni = holat_formatlash(buyurtma.get("status", ""))
    yaratilgan = (buyurtma.get("created_at") or "")[:10]
    jami = narx_formatlash(buyurtma.get("total", 0))
    izoh = buyurtma.get("izoh", "")
    matn = (
        f"🆔 Buyurtma #{buyurtma.get('id')}\n"
        f"💰 Jami: {jami} so'm\n"
        f"📊 Holat: {holat_matni}\n"
        f"📅 Sana: {yaratilgan}\n"
    )
    if izoh:
        matn += f"📝 Izoh: {izoh}\n"
    return matn


# ─── Menyular cache ─────────────────────────────────────────

Menyular = list(menyu_olish("asosiy").values())
MenyuSozlama = list(menyu_olish("foydalanuvchi_amallar").values())
Mahsulot = list({key: val["nomi"] for key, val in kategoriyalar_olish().items()}.values())


# ─── Asosiy menyu ────────────────────────────────────────────

async def foydalanuvchi_menyusi(message):
    menyu = menyu_olish("asosiy")
    tugmalar = [KeyboardButton(text=matn) for matn in menyu.values()]
    klaviatura = juftlik_bolish(tugmalar, 2)

    await message.answer(
        matn_olish("asosiy_menyu"),
        reply_markup=ReplyKeyboardMarkup(keyboard=klaviatura, resize_keyboard=True)
    )


# ─── /start buyrug'i ─────────────────────────────────────────

@rr.message(Command("start"))
async def boshlash_buyrugi(message: Message, state: FSMContext) -> None:
    await state.clear()

    foydalanuvchi_id = message.from_user.id
    foydalanuvchi = foydalanuvchi_olish(foydalanuvchi_id)

    if foydalanuvchi and foydalanuvchi.get("telefon") and foydalanuvchi.get("manzil"):
        if admin_tekshir(foydalanuvchi_id):
            await admin_menyuni_korsat(message)
        else:
            await foydalanuvchi_menyusi(message)
    else:
        await message.answer(
            matn_olish("boshlash"),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=matn_olish("telefon_url"), request_contact=True)]],
                resize_keyboard=True
            )
        )
        await state.set_state(RoyxatHolatlari.telefon)


# ─── Ro'yxatdan o'tish ───────────────────────────────────────

@rr.message(StateFilter(RoyxatHolatlari.telefon))
async def telefon_qabul(message: Message, state: FSMContext):
    if message.contact:
        await state.update_data(telefon=message.contact.phone_number)
        await message.answer(
            matn_olish("manzil_sorash"),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=matn_olish("manzil_url"), request_location=True)]],
                resize_keyboard=True
            )
        )
        await state.set_state(RoyxatHolatlari.manzil)
    else:
        await message.answer(matn_olish("telefon_xato"))


@rr.message(StateFilter(RoyxatHolatlari.manzil))
async def manzil_qabul(message: Message, state: FSMContext):
    foydalanuvchi_malumot = await state.get_data()
    telefon = foydalanuvchi_malumot.get("telefon")

    if message.location:
        manzil = f"{message.location.latitude}, {message.location.longitude}"
    elif message.text and len(message.text) > 10:
        manzil = message.text
    else:
        await message.answer(matn_olish("manzil_xato"))
        return

    saqlandi = foydalanuvchi_saqlash(
        foydalanuvchi_id=message.from_user.id,
        foydalanuvchi_nomi=message.from_user.username,
        toliq_ism=message.from_user.full_name,
        telefon=telefon,
        manzil=manzil
    )

    if saqlandi:
        await message.answer(matn_olish("royxat_muvaffaqiyat"))
        await state.clear()
        if admin_tekshir(message.from_user.id):
            await admin_menyuni_korsat(message)
        else:
            await foydalanuvchi_menyusi(message)
    else:
        await message.answer(matn_olish("royxat_xato"))


# ─── Asosiy menyu tugmalari ──────────────────────────────────

@rr.message(F.text.in_(Menyular))
async def menyu_buyruq(message: Message):
    matn = message.text
    orqaga = KeyboardButton(text=matn_olish("orqaga"))

    # 🍽 Menyu (Do'kon)
    if matn == Menyular[0]:
        kategoriyalar = kategoriyalar_olish()
        tugmalar = [KeyboardButton(text=kategoriya["nomi"]) for kategoriya in kategoriyalar.values()]
        klaviatura = juftlik_bolish(tugmalar, 2)
        klaviatura.append([orqaga])

        await message.answer(
            matn_olish("kategoriya_tanlash"),
            reply_markup=ReplyKeyboardMarkup(keyboard=klaviatura, resize_keyboard=True)
        )

    # 🛒 Savat
    elif matn == Menyular[1]:
        await savat_korsatish(message)

    # 📖 Buyurtmalarim
    elif matn == Menyular[2]:
        buyurtmalar = foydalanuvchi_buyurtmalari(message.from_user.id)
        if not buyurtmalar:
            await message.answer("📋 Sizda hali buyurtmalar yo'q")
            return

        buyurtmalar_matni = "📋 <b>Sizning buyurtmalaringiz:</b>\n\n"
        for buyurtma in buyurtmalar[-5:]:
            buyurtmalar_matni += buyurtma_xulosa_yaratish(buyurtma) + "\n"
        await message.answer(buyurtmalar_matni)

    # 📞 Aloqa
    elif matn == Menyular[3]:
        await message.answer(matn_olish("aloqa_malumot"))

    # ℹ️ Biz haqimizda
    elif matn == Menyular[4]:
        await message.answer(matn_olish("haqida_malumot"))

    # ⚙️ Sozlamalar
    elif matn == Menyular[5]:
        menyu = menyu_olish("foydalanuvchi_amallar")
        tugmalar = [KeyboardButton(text=matn_menyu) for matn_menyu in menyu.values()]
        klaviatura = juftlik_bolish(tugmalar, 1)
        klaviatura.append([orqaga])
        await message.answer(
            matn_olish("sozlamalar_menyu"),
            reply_markup=ReplyKeyboardMarkup(keyboard=klaviatura, resize_keyboard=True)
        )


# ─── Savat ko'rsatish ────────────────────────────────────────

async def savat_korsatish(message):
    savat = savat_olish(message.from_user.id)

    if not savat:
        await message.answer(matn_olish("savat_bosh"))
        return

    savat_matni = "🛒 <b>Savatingiz:</b>\n\n"
    jami = 0
    inline_tugmalar = []

    for idx, (kalit, mahsulot) in enumerate(savat.items(), 1):
        mahsulot_jami = mahsulot["price"] * mahsulot["quantity"]
        jami += mahsulot_jami
        savat_matni += (
            f"{idx}. <b>{mahsulot['name']}</b>\n"
            f"   💰 {narx_formatlash(mahsulot['price'])} × {mahsulot['quantity']} = "
            f"{narx_formatlash(mahsulot_jami)} so'm\n\n"
        )

        # +/- tugmalari
        kat = mahsulot["category"]
        prod = mahsulot["product_key"]
        inline_tugmalar.append([
            InlineKeyboardButton(text=f"➖", callback_data=f"cart_minus:{kat}:{prod}"),
            InlineKeyboardButton(text=f"{mahsulot['name']} ({mahsulot['quantity']})", callback_data="noop"),
            InlineKeyboardButton(text=f"➕", callback_data=f"cart_plus:{kat}:{prod}"),
        ])

    savat_matni += f"━━━━━━━━━━━━━━━\n💰 <b>Jami: {narx_formatlash(jami)} so'm</b>"

    inline_tugmalar.append([
        InlineKeyboardButton(text="💳 Buyurtma berish", callback_data="checkout"),
        InlineKeyboardButton(text="🗑 Tozalash", callback_data="clear_cart"),
    ])

    await message.answer(
        savat_matni,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_tugmalar)
    )


# ─── Savat +/- tugmalari ─────────────────────────────────────

@rr.callback_query(F.data.startswith("cart_plus:"))
async def savat_plus_callback(callback: CallbackQuery):
    _, kat, prod = callback.data.split(":")
    savat_qoshish(callback.from_user.id, kat, prod, 1)
    mahsulot = get_product(kat, prod)
    nomi = mahsulot["name"] if mahsulot else "Mahsulot"
    await callback.answer(f"➕ {nomi} +1")
    await _savat_yangilash(callback)


@rr.callback_query(F.data.startswith("cart_minus:"))
async def savat_minus_callback(callback: CallbackQuery):
    _, kat, prod = callback.data.split(":")
    savat_miqdor_yangilash(callback.from_user.id, kat, prod, -1)
    mahsulot = get_product(kat, prod)
    nomi = mahsulot["name"] if mahsulot else "Mahsulot"
    await callback.answer(f"➖ {nomi} -1")
    await _savat_yangilash(callback)


@rr.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    await callback.answer()


async def _savat_yangilash(callback: CallbackQuery):
    """Savat xabarini yangilash (inline edit)."""
    savat = savat_olish(callback.from_user.id)

    if not savat:
        await callback.message.edit_text(matn_olish("savat_bosh"))
        return

    savat_matni = "🛒 <b>Savatingiz:</b>\n\n"
    jami = 0
    inline_tugmalar = []

    for idx, (kalit, mahsulot) in enumerate(savat.items(), 1):
        mahsulot_jami = mahsulot["price"] * mahsulot["quantity"]
        jami += mahsulot_jami
        savat_matni += (
            f"{idx}. <b>{mahsulot['name']}</b>\n"
            f"   💰 {narx_formatlash(mahsulot['price'])} × {mahsulot['quantity']} = "
            f"{narx_formatlash(mahsulot_jami)} so'm\n\n"
        )

        kat = mahsulot["category"]
        prod = mahsulot["product_key"]
        inline_tugmalar.append([
            InlineKeyboardButton(text="➖", callback_data=f"cart_minus:{kat}:{prod}"),
            InlineKeyboardButton(text=f"{mahsulot['name']} ({mahsulot['quantity']})", callback_data="noop"),
            InlineKeyboardButton(text="➕", callback_data=f"cart_plus:{kat}:{prod}"),
        ])

    savat_matni += f"━━━━━━━━━━━━━━━\n💰 <b>Jami: {narx_formatlash(jami)} so'm</b>"

    inline_tugmalar.append([
        InlineKeyboardButton(text="💳 Buyurtma berish", callback_data="checkout"),
        InlineKeyboardButton(text="🗑 Tozalash", callback_data="clear_cart"),
    ])

    try:
        await callback.message.edit_text(
            savat_matni,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_tugmalar)
        )
    except Exception:
        pass  # Xabar o'zgarmagan bo'lishi mumkin


# ─── Buyurtma berish ─────────────────────────────────────────

@rr.callback_query(F.data == "checkout")
async def checkout_callback(callback: CallbackQuery, state: FSMContext):
    savat = savat_olish(callback.from_user.id)

    if not savat:
        await callback.answer(matn_olish("savat_bosh"), show_alert=True)
        return

    await callback.answer()
    await state.set_state(BuyurtmaHolati.izoh)
    await callback.message.answer(
        "📝 Buyurtmaga izoh qo'shmoqchimisiz?\n\n"
        "Izohingizni yozing yoki «⏭ O'tkazib yuborish» tugmasini bosing.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⏭ O'tkazib yuborish")]],
            resize_keyboard=True
        )
    )


@rr.message(StateFilter(BuyurtmaHolati.izoh))
async def buyurtma_izoh_qabul(message: Message, state: FSMContext):
    izoh = ""
    if message.text and message.text != "⏭ O'tkazib yuborish":
        izoh = message.text.strip()

    buyurtma = buyurtma_yaratish(message.from_user.id, izoh)

    if buyurtma:
        jami = narx_formatlash(buyurtma["total"])
        buyurtma_matni = (
            f"✅ <b>{matn_olish('buyurtma_qabul')}</b>\n\n"
            f"🆔 Buyurtma raqami: #{buyurtma['id']}\n"
            f"💰 Jami: {jami} so'm\n"
            f"📊 Holat: {holat_formatlash(buyurtma['status'])}\n"
        )
        if izoh:
            buyurtma_matni += f"📝 Izoh: {izoh}\n"
        buyurtma_matni += "\n🚗 Tez orada siz bilan bog'lanamiz!"

        await message.answer(buyurtma_matni)
        await state.clear()
        await foydalanuvchi_menyusi(message)
    else:
        await message.answer("❌ Buyurtma yaratishda xatolik!")
        await state.clear()


# ─── Eski savat tugmalari (reply keyboard uchun) ─────────────

@rr.message(F.text == "💳 Buyurtma berish")
async def buyurtma_berish_reply(message: Message, state: FSMContext):
    savat = savat_olish(message.from_user.id)

    if not savat:
        await message.answer(matn_olish("savat_bosh"))
        return

    await state.set_state(BuyurtmaHolati.izoh)
    await message.answer(
        "📝 Buyurtmaga izoh qo'shmoqchimisiz?\n\n"
        "Izohingizni yozing yoki «⏭ O'tkazib yuborish» tugmasini bosing.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⏭ O'tkazib yuborish")]],
            resize_keyboard=True
        )
    )


@rr.callback_query(F.data == "clear_cart")
async def savat_tozalash_inline(callback: CallbackQuery):
    savat_tozalash(callback.from_user.id)
    await callback.answer("✅ Savat tozalandi")
    await callback.message.edit_text("🛒 Savatingiz tozalandi!\n\n🍽 Menyudan taom tanlang.")


@rr.message(F.text == "🗑 Savatni tozalash")
async def savat_tozalash_buyruq(message: Message):
    savat_tozalash(message.from_user.id)
    await message.answer("✅ Savat tozalandi")
    await foydalanuvchi_menyusi(message)


# ─── Orqaga ──────────────────────────────────────────────────

@rr.message(F.text == matn_olish("orqaga"))
async def orqaga_buyruq(message: Message):
    await foydalanuvchi_menyusi(message)


# ─── Sozlamalar ──────────────────────────────────────────────

@rr.message(F.text.in_(MenyuSozlama))
async def menyu_sozlama(message: Message, state: FSMContext):
    matn = message.text

    # Qayta ro'yxatdan o'tish
    if matn == MenyuSozlama[0]:
        foydalanuvchi_tozalash(message.from_user.id)
        await state.clear()
        await message.answer(
            "♻️ Qayta ro'yxatdan o'tish boshlandi.\nIltimos, telefon raqamingizni yuboring.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
                resize_keyboard=True
            )
        )
        await state.set_state(RoyxatHolatlari.telefon)

    # Buyurtmani bekor qilish
    elif matn == MenyuSozlama[1]:
        buyurtmalar = foydalanuvchi_buyurtmalari(message.from_user.id)
        bekor_qilinadigan = [
            b for b in buyurtmalar
            if b["status"] not in {"cancelled", "completed"}
        ]

        if not bekor_qilinadigan:
            await message.answer("❌ Bekor qilinadigan buyurtmalar topilmadi.")
            return

        klaviatura_qatorlar = []
        for buyurtma in bekor_qilinadigan:
            holat_matni = holat_formatlash(buyurtma["status"])
            jami = narx_formatlash(buyurtma["total"])
            tugma_matni = f"#{buyurtma['id']} — {jami} so'm ({holat_matni})"
            klaviatura_qatorlar.append(
                [InlineKeyboardButton(text=tugma_matni, callback_data=f"cancel_order:{buyurtma['id']}")]
            )
        klaviatura_qatorlar.append(
            [InlineKeyboardButton(text="⬅️ Bekor qilish", callback_data="cancel_order_menu_close")]
        )

        await message.answer(
            "Bekor qilmoqchi bo'lgan buyurtmani tanlang:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=klaviatura_qatorlar)
        )


# ─── Kategoriya tanlash ──────────────────────────────────────

@rr.message(F.text.in_(Mahsulot))
async def mahsulot_korsatish(message: Message):
    kategoriyalar = get_categories()
    kategoriya_nomi = message.text

    kategoriya_kaliti = None
    for kalit, kategoriya in kategoriyalar.items():
        if kategoriya["name"] == kategoriya_nomi:
            kategoriya_kaliti = kalit
            break

    if not kategoriya_kaliti:
        await message.answer("❌ Kategoriya topilmadi")
        return

    mahsulotlar = get_category_products(kategoriya_kaliti)
    kategoriya = kategoriyalar[kategoriya_kaliti]

    mahsulotlar_matni = f"<b>{kategoriya_nomi}</b>\n\n"
    klaviatura_tugmalari = []

    for i, (kalit, mahsulot) in enumerate(mahsulotlar.items(), 1):
        narx = narx_formatlash(mahsulot["price"])
        mahsulotlar_matni += (
            f"{i}. <b>{mahsulot['name']}</b>\n"
            f"   📝 {mahsulot['description']}\n"
            f"   💰 {narx} so'm\n\n"
        )
        klaviatura_tugmalari.append(
            InlineKeyboardButton(
                text=f"{i}",
                callback_data=f"add_to_cart:{kategoriya_kaliti}:{kalit}"
            )
        )

    # Tugmalarni 2-3 tadan qatorga joylash
    inline_rows = juftlik_bolish(klaviatura_tugmalari, 4)
    inline_rows.append([InlineKeyboardButton(text="❌ Yopish", callback_data="cancel")])
    klaviatura = InlineKeyboardMarkup(inline_keyboard=inline_rows)

    try:
        rasm = FSInputFile(kategoriya["image"])
        await message.answer_photo(
            photo=rasm,
            caption=mahsulotlar_matni,
            reply_markup=klaviatura
        )
    except Exception:
        await message.answer(
            mahsulotlar_matni,
            reply_markup=klaviatura
        )


# ─── Savatga qo'shish ────────────────────────────────────────

@rr.callback_query(F.data.startswith("add_to_cart:"))
async def savatga_qoshish_callback(callback: CallbackQuery):
    try:
        _, kategoriya, mahsulot_kaliti = callback.data.split(":")

        if savat_qoshish(callback.from_user.id, kategoriya, mahsulot_kaliti):
            mahsulot = get_product(kategoriya, mahsulot_kaliti)
            soni = savat_soni(callback.from_user.id)
            await callback.answer(f"✅ {mahsulot['name']} savatga qo'shildi! (🛒 {soni})")
        else:
            await callback.answer("❌ Xatolik yuz berdi!")
    except Exception as e:
        logger.error(f"Callback xatolik: {e}")
        await callback.answer("❌ Xatolik yuz berdi!")


@rr.callback_query(F.data == "cancel")
async def bekor_qilish_callback(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("❌ Yopildi")


# ─── Buyurtma bekor qilish ───────────────────────────────────

@rr.callback_query(F.data.startswith("cancel_order:"))
async def buyurtma_bekor_callback(callback: CallbackQuery):
    try:
        _, buyurtma_id_str = callback.data.split(":")
        buyurtma_id = int(buyurtma_id_str)
    except (ValueError, IndexError):
        await callback.answer("❌ Buyurtma ma'lumotida xatolik.", show_alert=True)
        return

    if buyurtma_bekor_qilish(buyurtma_id, callback.from_user.id):
        await callback.answer("✅ Buyurtma bekor qilindi.", show_alert=True)
        await callback.message.edit_text(f"✅ Buyurtma #{buyurtma_id} bekor qilindi.")
    else:
        await callback.answer("❌ Bu buyurtmani bekor qilib bo'lmaydi.", show_alert=True)


@rr.callback_query(F.data == "cancel_order_menu_close")
async def buyurtma_bekor_menyu_yopish(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("❌ Amal bekor qilindi.")


# ─── Router registratsiya ────────────────────────────────────

def user_login(dp):
    dp.include_router(rr)