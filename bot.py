import asyncio
import os
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from dotenv import load_dotenv


# =========================================================
# SOZLAMALAR
# =========================================================

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "").strip()
DIRECTOR_ID = int(os.getenv("DIRECTOR_ID", "0") or 0)

DATA_DIR = os.getenv("DATA_DIR", ".")
os.makedirs(DATA_DIR, exist_ok=True)
DB_NAME = os.path.join(DATA_DIR, "parfum.db")

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN .env faylida topilmadi!")

if DIRECTOR_ID == 0:
    raise ValueError("❌ DIRECTOR_ID .env faylida topilmadi!")

bot = Bot(token=TOKEN)
dp = Dispatcher()


# =========================================================
# VAQT
# =========================================================

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today():
    return datetime.now().strftime("%Y-%m-%d")


# =========================================================
# DATABASE
# =========================================================

def db_connect():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():

    conn = db_connect()
    cur = conn.cursor()

    # -----------------------------------------------------
    # DO'KONLAR
    # -----------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            role TEXT NOT NULL,
            shop_id INTEGER,
            created_at TEXT NOT NULL,

            FOREIGN KEY(shop_id)
            REFERENCES shops(id)
            ON DELETE SET NULL
        )
    """)

    try:
        cur.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
    except sqlite3.OperationalError:
        pass # Eski bazada username bo'lmasa qo'shamiz
    columns = [
        row[1]
        for row in cur.execute(
            "PRAGMA table_info(users)"
        ).fetchall()
    ]

    if "username" not in columns:

        cur.execute("""
            ALTER TABLE users
            ADD COLUMN username TEXT
        """)

    # -----------------------------------------------------
    # SOTUVCHI SO'ROVLARI
    # -----------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pending_sellers (
            telegram_id INTEGER PRIMARY KEY,

            name TEXT NOT NULL,

            username TEXT,

            requested_at TEXT NOT NULL,

            status TEXT NOT NULL DEFAULT 'pending'
        )
    """)

    # -----------------------------------------------------
    # MAHSULOTLAR
    # -----------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT UNIQUE NOT NULL,

            category TEXT NOT NULL,

            volume INTEGER,

            variant TEXT,

            created_at TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # QOLDIQ
    # -----------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            shop_id INTEGER NOT NULL,

            product_id INTEGER NOT NULL,

            quantity INTEGER NOT NULL DEFAULT 0,

            updated_at TEXT NOT NULL,

            UNIQUE(shop_id, product_id),

            FOREIGN KEY(shop_id)
            REFERENCES shops(id)
            ON DELETE CASCADE,

            FOREIGN KEY(product_id)
            REFERENCES products(id)
  ON DELETE CASCADE
        )
    """)

    # -----------------------------------------------------
    # HARAKATLAR
    # -----------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movements (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            shop_id INTEGER NOT NULL,

            product_id INTEGER NOT NULL,

            movement_type TEXT NOT NULL,

            quantity INTEGER NOT NULL,

            seller_id INTEGER,

            note TEXT,

            created_at TEXT NOT NULL,

            FOREIGN KEY(shop_id)
            REFERENCES shops(id),

            FOREIGN KEY(product_id)
            REFERENCES products(id)
        )
    """)

    # -----------------------------------------------------
    # ISH KUNLARI
    # -----------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS work_days (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            shop_id INTEGER NOT NULL,

            work_date TEXT NOT NULL,

            status TEXT NOT NULL DEFAULT 'open',

            created_at TEXT NOT NULL,

            UNIQUE(shop_id, work_date),

            FOREIGN KEY(shop_id)
            REFERENCES shops(id)
            ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# MENULAR
# =========================================================

def director_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🏪 Дўкон қўшиш"),
                KeyboardButton(text="👤 Сотувчи қўшиш")
            ],
            [
                KeyboardButton(text="🏪 Дўконлар"),
                KeyboardButton(text="👥 Сотувчилар")
            ],
            [
                KeyboardButton(text="📦 Маҳсулотлар"),
                KeyboardButton(text="📥 Кирим")
            ],
            [
                KeyboardButton(text="🛒 Сотув"),
                KeyboardButton(text="📤 Списание")
            ],
            [
                KeyboardButton(text="📊 Ҳисобот")
            ],
            [
                KeyboardButton(
                    text="🤖 Ҳисобчи AI",
                    web_app=WebAppInfo(
                        url="https://example.com"
                    )
                )
            ]
        ],
        resize_keyboard=True
    )


def seller_menu():

    return ReplyKeyboardMarkup(
        keyboard=[

            [
                KeyboardButton(text="📤 Сотув"),
                KeyboardButton(text="📥 Кирим")
            ],

            [
                KeyboardButton(text="📦 Остаток"),
                KeyboardButton(text="🗑 Списание")
            ],

            [
                KeyboardButton(text="📊 Ҳисобот")
            ]

        ],
        resize_keyboard=True
    )


def cancel_menu():

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="❌ Бекор қилиш")
            ]
        ],
        resize_keyboard=True
    )


# =========================================================
# STATES
# =========================================================

class AddShop(StatesGroup):

    name = State()


class SellerRequest(StatesGroup):

    seller_number = State()
    shop_number = State()


# =========================================================
# YORDAMCHI FUNKSIYALAR
# =========================================================

def is_director(message: types.Message):

    return message.from_user.id == DIRECTOR_ID


def get_user(telegram_id):

    conn = db_connect()

    row = conn.execute("""
        SELECT
            telegram_id,
            name,
            username,
            role,
            shop_id
        FROM users
        WHERE telegram_id = ?
    """, (telegram_id,)).fetchone()

    conn.close()

    return row


def get_shop(shop_id):

    conn = db_connect()

    row = conn.execute("""
        SELECT id, name
        FROM shops
        WHERE id = ?
    """, (shop_id,)).fetchone()

    conn.close()

    return row


def get_shops():

    conn = db_connect()

    rows = conn.execute("""
        SELECT id, name
        FROM shops
        ORDER BY id
    """).fetchall()

    conn.close()

    return rows
def get_pending_sellers():

    conn = db_connect()

    rows = conn.execute("""
        SELECT
            telegram_id,
            name,
            username,
            requested_at
        FROM pending_sellers
        WHERE status = 'pending'
        ORDER BY requested_at
    """).fetchall()

    conn.close()

    return rows


def get_pending_seller(telegram_id):

    conn = db_connect()

    row = conn.execute("""
        SELECT
            telegram_id,
            name,
            username,
            requested_at
        FROM pending_sellers
        WHERE telegram_id = ?
        AND status = 'pending'
    """, (telegram_id,)).fetchone()

    conn.close()

    return row


# =========================================================
# SOTUVCHI SO'ROVINI SAQLASH
# =========================================================

def save_seller_request(user):

    conn = db_connect()

    conn.execute("""
        INSERT INTO pending_sellers
        (
            telegram_id,
            name,
            username,
            requested_at,
            status
        )

        VALUES (?, ?, ?, ?, 'pending')

        ON CONFLICT(telegram_id)
        DO UPDATE SET

            name = excluded.name,

            username = excluded.username,

            requested_at = excluded.requested_at,

            status = 'pending'
    """, (
        user.id,
        user.full_name,
        user.username,
        now()
    ))

    conn.commit()
    conn.close()


# =========================================================
# DIREKTORGA XABAR
# =========================================================

async def notify_director(user):

    username = (
        f"@{user.username}"
        if user.username
        else "username йўқ"
    )

    try:

        await bot.send_message(
            DIRECTOR_ID,

            "🔔 ЯНГИ СОТУВЧИ СЎРОВИ!\n\n"

            f"👤 Исм: {user.full_name}\n"
            f"🔗 Username: {username}\n"
            f"🆔 Telegram ID: {user.id}\n"
            f"📅 Сана: {now()}\n\n"

            "👤 «Сотувчи қўшиш» тугмасини босиб "
            "доступ беринг."
        )

    except Exception:
        pass


# =========================================================
# START
# =========================================================

@dp.message(CommandStart())
async def start(
    message: types.Message,
    state: FSMContext
):

    await state.clear()

    user = message.from_user

    # -----------------------------------------------------
    # DIREKTOR
    # -----------------------------------------------------

    if user.id == DIRECTOR_ID:

        conn = db_connect()

        conn.execute("""
            INSERT INTO users
            (
                telegram_id,
                name,
                username,
                role,
                shop_id,
                created_at
            )

            VALUES (?, ?, ?, 'director', NULL, ?)

            ON CONFLICT(telegram_id)
            DO UPDATE SET

                name = excluded.name,

                username = excluded.username,

                role = 'director',

                shop_id = NULL
        """, (
            user.id,
            user.full_name,
            user.username,
            now()
        ))

        conn.commit()
        conn.close()

        await message.answer(

            "👑 Хуш келибсиз!\n\n"

            "🏢 SHAik Perfume\n"
            "Бошқарув панели тайёр.",

            reply_markup=director_menu()
        )

        return

    # -----------------------------------------------------
    # OLDI SOTUVCHI
    # -----------------------------------------------------

    existing = get_user(user.id)

    if existing:

        telegram_id, name, username, role, shop_id = existing

        if role == "seller":

            shop = get_shop(shop_id)

            if not shop:

                await message.answer(
                    "⚠️ Сизга дўкон бириктирилмаган."
                )

                return

            await message.answer(

                f"👋 Салом, {user.first_name}!\n\n"
  f"🏪 Дўкон: {shop[1]}\n"

                f"📅 Сана: "
                f"{datetime.now().strftime('%d.%m.%Y')}\n\n"

                "Керакли бўлимни танланг:",

                reply_markup=seller_menu()
            )

            return

    # -----------------------------------------------------
    # YANGI SOTUVCHI
    # -----------------------------------------------------

    save_seller_request(user)

    await notify_director(user)

    await message.answer(

        "⏳ Сўровингиз қабул қилинди.\n\n"

        f"👤 Исм: {user.full_name}\n"

        f"📅 Сана: "
        f"{datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"

        "Директор сизни тасдиқлашини кутинг.\n"

        "Доступ берилгандан кейин ботдан "
        "фойдаланишингиз мумкин."
    )


# =========================================================
# CANCEL
# =========================================================

@dp.message(F.text == "❌ Бекор қилиш")
async def cancel(
    message: types.Message,
    state: FSMContext
):

    await state.clear()

    if is_director(message):

        await message.answer(
            "❌ Амал бекор қилинди.",
            reply_markup=director_menu()
        )

    else:

        await message.answer(
            "❌ Амал бекор қилинди.",
            reply_markup=seller_menu()
        )


# =========================================================
# DO'KON QO'SHISH
# =========================================================

@dp.message(F.text == "🏪 Дўкон қўшиш")
async def add_shop_start(
    message: types.Message,
    state: FSMContext
):

    if not is_director(message):
        return

    await message.answer(

        "🏪 Дўкон номини ёзинг.\n\n"

        "Масалан:\n"
        "1-дўкон Блок 96",

        reply_markup=cancel_menu()
    )

    await state.set_state(
        AddShop.name
    )


@dp.message(AddShop.name)
async def add_shop_finish(
    message: types.Message,
    state: FSMContext
):

    if not is_director(message):

        await state.clear()
        return

    name = (
        message.text or ""
    ).strip()

    if len(name) < 2:

        await message.answer(
            "❌ Дўкон номи жуда қисқа."
        )

        return

    conn = db_connect()

    try:

        conn.execute("""
            INSERT INTO shops
            (
                name,
                created_at
            )

            VALUES (?, ?)
        """, (
            name,
            now()
        ))

        conn.commit()

    except sqlite3.IntegrityError:

        conn.close()

        await message.answer(
            "⚠️ Бу номдаги дўкон аллақачон бор."
        )

        return

    conn.close()

    await state.clear()

    await message.answer(

        "✅ Дўкон қўшилди!\n\n"

        f"🏪 {name}",

        reply_markup=director_menu()
    )


# =========================================================
# DO'KONLAR
# =========================================================

@dp.message(F.text == "🏪 Дўконлар")
async def shops_list(
    message: types.Message
):

    if not is_director(message):
        return

    shops = get_shops()

    if not shops:

        await message.answer(
            "🏪 Ҳали дўконлар қўшилмаган."
        )

        return

    text = "🏪 ДЎКОНЛАР:\n\n"

    for shop_id, name in shops:

        text += (
            f"{shop_id}. {name}\n"
        )

    await message.answer(text)


# =========================================================
# SOTUVCHI QO'SHISH
# =========================================================

@dp.message(F.text == "👤 Сотувчи қўшиш")
async def seller_add_start(
    message: types.Message,
    state: FSMContext
):

    if not is_director(message):
        return

    pending = get_pending_sellers()

    if not pending:

        await message.answer(

            "👥 Ҳозирча доступ кутayotgan "
            "сотувчилар йўқ.\n\n"

            "Сотувчи аввал ботга /start "
            "босиши керак.",

            reply_markup=director_menu()
        )

        return

    text = (
        "👤 ДОСТУП КУТАЁТГАН СОТУВЧИЛАР:\n\n"
    )
    for number, seller in enumerate(
        pending,
        start=1
    ):

        telegram_id = seller[0]
        name = seller[1]
        username = seller[2]
        requested_at = seller[3]

        username_text = (
            f"@{username}"
            if username
            else "username йўқ"
        )

        text += (

            f"{number}. 👤 {name}\n"

            f"   🔗 {username_text}\n"

            f"   🆔 {telegram_id}\n"

            f"   📅 {requested_at}\n\n"
        )

    text += (
        "Сотувчи рақамини юборинг.\n"
        "Масалан: 1"
    )

    await message.answer(
        text,
        reply_markup=cancel_menu()
    )

    await state.set_state(
        SellerRequest.seller_number
    )


# =========================================================
# SOTUVCHINI TANLASH
# =========================================================

@dp.message(SellerRequest.seller_number)
async def seller_selected(
    message: types.Message,
    state: FSMContext
):

    if not is_director(message):
        return

    text = (
        message.text or ""
    ).strip()

    if not text.isdigit():

        await message.answer(
            "❌ Сотувчи рақамини рақам билан "
            "юборинг.\n\nМасалан: 1"
        )

        return

    number = int(text)

    pending = get_pending_sellers()

    if number < 1 or number > len(pending):

        await message.answer(
            "❌ Бундай рақамда сотувчи йўқ."
        )

        return

    seller = pending[number - 1]

    seller_id = seller[0]

    await state.update_data(
        seller_id=seller_id
    )

    shops = get_shops()

    if not shops:

        await state.clear()

        await message.answer(

            "⚠️ Аввал камида битта "
            "дўкон қўшинг.",

            reply_markup=director_menu()
        )

        return

    shop_text = (

        f"👤 Сотувчи: {seller[1]}\n"

        f"🆔 ID: {seller_id}\n\n"

        "🏪 Қайси дўконга "
        "бириктирамиз?\n\n"
    )

    for shop_id, shop_name in shops:

        shop_text += (
            f"{shop_id}. {shop_name}\n"
        )

    shop_text += (
        "\nДўкон рақамини юборинг."
    )

    await message.answer(
        shop_text,
        reply_markup=cancel_menu()
    )

    await state.set_state(
        SellerRequest.shop_number
    )


# =========================================================
# DO'KONNI TANLASH VA TASDIQLASH
# =========================================================

@dp.message(SellerRequest.shop_number)
async def seller_shop_selected(
    message: types.Message,
    state: FSMContext
):

    if not is_director(message):
        return

    text = (
        message.text or ""
    ).strip()

    if not text.isdigit():

        await message.answer(
            "❌ Дўкон рақамини рақам билан "
            "юборинг.\n\nМасалан: 1"
        )

        return

    shop_id = int(text)

    shop = get_shop(shop_id)

    if not shop:

        await message.answer(
            "❌ Бундай дўкон йўқ."
        )

        return

    data = await state.get_data()

    seller_id = data.get(
        "seller_id"
    )

    if not seller_id:

        await state.clear()

        await message.answer(
            "⚠️ Сотувчи танлаш жараёни "
            "бузилди. Қайтадан бошланг."
        )

        return

    seller = get_pending_seller(
        seller_id
    )

    if not seller:

        await state.clear()

        await message.answer(
            "⚠️ Бу сотувчи сўрови "
            "топилмади."
        )

        return

    conn = db_connect()

    # -----------------------------------------------------
    # SOTUVCHINI TASDIQLAYMIZ
    # -----------------------------------------------------

    conn.execute("""
        INSERT INTO users
        (
            telegram_id,
            name,
            username,
            role,
            shop_id,
            created_at
        )

        VALUES (?, ?, ?, 'seller', ?, ?)

        ON CONFLICT(telegram_id)
        DO UPDATE SET

            name = excluded.name,

            username = excluded.username,
  role = 'seller',

            shop_id = excluded.shop_id
    """, (
        seller[0],
        seller[1],
        seller[2],
        shop_id,
        now()
    ))

    # -----------------------------------------------------
    # SO'ROVNI YOPAMIZ
    # -----------------------------------------------------

    conn.execute("""
        UPDATE pending_sellers

        SET status = 'approved'

        WHERE telegram_id = ?
    """, (
        seller_id,
    ))

    conn.commit()
    conn.close()

    await state.clear()

    # -----------------------------------------------------
    # DIREKTORGA
    # -----------------------------------------------------

    await message.answer(

        "✅ ДОСТУП БЕРИЛДИ!\n\n"

        f"👤 {seller[1]}\n"

        f"🆔 {seller[0]}\n"

        f"🏪 Дўкон: {shop[1]}\n"

        f"📅 {now()}\n\n"

        "Сотувчи энди ботдан "
        "фойдаланиши мумкин.",

        reply_markup=director_menu()
    )

    # -----------------------------------------------------
    # SOTUVCHIGA XABAR
    # -----------------------------------------------------

    try:

        await bot.send_message(

            seller_id,

            "✅ Сизга доступ берилди!\n\n"

            f"🏪 Дўкон: {shop[1]}\n"

            f"📅 {now()}\n\n"

            "Ботга /start босинг."
        )

    except Exception:

        pass


# =========================================================
# SOTUVCHILAR
# =========================================================

@dp.message(F.text == "👥 Сотувчилар")
async def sellers_list(
    message: types.Message
):

    if not is_director(message):
        return

    conn = db_connect()

    sellers = conn.execute("""
        SELECT
            users.telegram_id,
            users.name,
            users.username,
            shops.name

        FROM users

        LEFT JOIN shops
        ON users.shop_id = shops.id

        WHERE users.role = 'seller'

        ORDER BY users.name
    """).fetchall()

    conn.close()

    if not sellers:

        await message.answer(
            "👥 Ҳали сотувчилар қўшилмаган."
        )

        return

    text = "👥 СОТУВЧИЛАР:\n\n"

    for seller in sellers:

        telegram_id = seller[0]
        name = seller[1]
        username = seller[2]
        shop_name = seller[3]

        username_text = (
            f"@{username}"
            if username
            else "username йўқ"
        )

        text += (

            f"👤 {name}\n"

            f"🔗 {username_text}\n"

            f"🆔 {telegram_id}\n"

            f"🏪 {shop_name or '—'}\n\n"
        )

    await message.answer(text)


# =========================================================
# KEYINGI MODULLAR
# =========================================================
# 📦 МАҲСУЛОТЛАР МОДУЛИ
# ============================================================

PRODUCTS = {

    # ========================================================
    # 🌸 SHAIK
    # ========================================================
    "🌸 Shaik": [
        "🌸 Shaik 10ml",
        "🌸 Shaik 20ml",
        "🌸 Shaik 20ml KOP",
        "🌸 Shaik 25ml/Tester",
        "🌸 Shaik 50ml",
        "🌸 Shaik 50ml New Design",
        "🌸 Shaik 50ml 888 Don't Stop",
        "🌸 Shaik 50ml Распродажа",
        "🌸 Shaik 100ml New Design",
        "🌸 Shaik Niche 50ml",
        "🌸 Shaik Niche 110ml",
        "🌸 Shaik Rich 50ml",
        "🌸 Shaik Body Splash",
        "🌸 Shaik Roller Bal Maclo 10ml",
        "🌸 Shaik Автопарфюм Deluxe 8ml",
    ],

    # ========================================================
    # 🌿 CLIVE & KEIRA
    # ========================================================
    "🌿 Клив": [
        "🌿 Clive & Keira 30ml",
        "🌿 Clive & Keira 30ml Скидка",
        "🌿 Clive & Keira 60ml",

        # МОЛЕКУЛА АЛОҲИДА
        "🌿 Clive & Keira 30ml MOL02",
    ],

    # ========================================================
    # 🌿 SEVAVEREK
    # ========================================================
    "🌿 Sevaverek": [
        "🌿 Sevaverek 30ml",
        "🌿 Sevaverek 50ml",

    ],

    # ========================================================
    # 💨 ДИФФУЗОР
    # ========================================================
    "💨 Диффузор": [
        "💨 Диффузор Shaik New 100ml",
    ],

    # ========================================================
    # 🎁 НАБОР
    # ========================================================
    "🎁 Набор": [
        "🎁 Набор Shaik 15ml (1×6)",
        "🎁 Набор Shaik 4 in 1",
    ],

    # ========================================================
    # 🧴 ДЕЗОДОРАНТ
    # ========================================================
    "🧴 Дезодорант": [
        "🧴 Дезодорант Shaik 200ml New",
    ],

    # ========================================================
    # 🚗 АВТО ПАРФЮМ
    # ========================================================
    "🚗 Авто парфюм": [
        "🚗 Shaik Автопарфюм Deluxe 8ml",
    ],
}


# ============================================================
# 📦 МАҲСУЛОТЛАР МЕНЮСИ
# ============================================================

@dp.message(F.text == "📦 Маҳсулотлар")
async def products_message(message: types.Message):

    if not is_director(message):
        return

    keyboard = [
        [
            types.InlineKeyboardButton(
                text="🌸 Shaik",
                callback_data="cat:🌸 Shaik"
            ),
            types.InlineKeyboardButton(
                text="🌿 Клив",
                callback_data="cat:🌿 Клив"
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="🍃 Sevaverek",
                callback_data="cat:🍃 Sevaverek"
            ),
            types.InlineKeyboardButton(
                text="⚪️ Диффузор",
                callback_data="cat:⚪️ Диффузор"
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="🎁 Набор",
                callback_data="cat:🎁 Набор"
            ),
            types.InlineKeyboardButton(
                text="🧴 Дезодорант",
                callback_data="cat:🧴 Дезодорант"
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="🚗 Автопарфюм",
                callback_data="cat:🚗 Автопарфюм"
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="🔙 Орқага",
                callback_data="products_back"
            ),
        ],
    ]

    await message.answer(
        "📦 <b>Маҳсулотлар</b>\n\n"
        "Керакли категорияни танланг:",
        parse_mode="HTML",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=keyboard
        )
    )


# ============================================================
# 🗂 КАТЕГОРИЯ ИЧИДАГИ ТОВАРЛАР
# ============================================================
CATEGORY_MAP = {
    "🌸 Shaik": "🌸 Shaik",
    "🌿 Clive & Keira": "🌿 Клив",
    "🍃 Sevaverek": "🍃 Sevaverek",
    "⚪️ Диффузор": "⚪️ Диффузор",
    "🎁 Набор": "🎁 Набор",
    "🧴 Дезодорант": "🧴 Дезодорант",
    "🚗 Автопарфюм": "🚗 Автопарфюм",
}


async def show_products_category(message: types.Message, category: str):

    products = PRODUCTS.get(category, [])

    if not products:
        await message.answer(
            "❌ Бу категорияда маҳсулот топилмади."
        )
        return

    keyboard = []

    for i, product in enumerate(products):
        keyboard.append([
            types.InlineKeyboardButton(
                text=f"🌸 {product}",
                callback_data=f"product:{category}:{i}"
            )
        ])

    keyboard.append([
        types.InlineKeyboardButton(
            text="🔙 Категорияларга",
            callback_data="products_back"
        )
    ])

    await message.answer(
        f"📦 <b>{category}</b>\n\n"
        "Керакли маҳсулотни танланг:",
        parse_mode="HTML",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=keyboard
        )
    )


@dp.message(F.text.in_(CATEGORY_MAP.keys()))
async def category_handler(message: types.Message):

    if not is_director(message):
        return

    category = CATEGORY_MAP[message.text]

    await show_products_category(
        message,
        category
    )
@dp.callback_query(F.data.startswith("cat:"))
async def category_callback(callback: types.CallbackQuery):

    if not is_director(callback.message):
        await callback.answer()
        return

    category = callback.data.replace("cat:", "", 1)

    await callback.answer()

    await show_products_category(
        callback.message,
        category
    )
@dp.callback_query(F.data == "products_back")
async def products_back_callback(callback: types.CallbackQuery):

    if not is_director(callback.message):
        await callback.answer()
        return

    await callback.answer()

    keyboard = [
        [
            types.InlineKeyboardButton(
                text="🌸 Shaik",
                callback_data="cat:🌸 Shaik"
            ),
            types.InlineKeyboardButton(
                text="🌿 Клив",
                callback_data="cat:🌿 Клив"
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="🍃 Sevaverek",
                callback_data="cat:🍃 Sevaverek"
            ),
            types.InlineKeyboardButton(
                text="⚪️ Диффузор",
                callback_data="cat:⚪️ Диффузор"
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="🎁 Набор",
                callback_data="cat:🎁 Набор"
            ),
            types.InlineKeyboardButton(
                text="🧴 Дезодорант",
                callback_data="cat:🧴 Дезодорант"
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="🚗 Автопарфюм",
                callback_data="cat:🚗 Автопарфюм"
            ),
        ],
    ]

    await callback.message.edit_text(
        "📦 <b>Маҳсулотлар</b>\n\n"
        "Керакли категорияни танланг:",
        parse_mode="HTML",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=keyboard
        )
    )
# ============================================================
# 🧴 SW
# ============================================================

@dp.message(F.text == "🧴 SW")
async def sw_products(message: types.Message):

    if not is_director(message):
        return

    await show_products_category(message, "🧴 SW")


# ============================================================
# 🌸 SHAIK
# ============================================================

@dp.message(F.text == "🌸 Shaik")
async def shaik_products(message: types.Message):

    if not is_director(message):
        return

    await show_products_category(message, "🌸 Shaik")


# ============================================================
# 🌿 CLIVE & KEIRA
# ============================================================

@dp.message(F.text == "🌿 Клив")
async def clive_products(message: types.Message):

    if not is_director(message):
        return

    await show_products_category(message, "🌿 Клив")


# ============================================================
# 🌿 SEVAVEREK
# ============================================================

@dp.message(F.text == "🌿 Sevaverek")
async def sevaverek_products(message: types.Message):

    if not is_director(message):
        return

    await show_products_category(message, "🌿 Sevaverek")


# ============================================================
# 💨 ДИФФУЗОР
# ============================================================

@dp.message(F.text == "💨 Диффузор")
async def diffuser_products(message: types.Message):

    if not is_director(message):
        return

    await show_products_category(message, "💨 Диффузор")


# ============================================================
# 🎁 НАБОР
# ============================================================

@dp.message(F.text == "🎁 Набор")
async def set_products(message: types.Message):

    if not is_director(message):
        return

    await show_products_category(message, "🎁 Набор")


# ============================================================
# 🧴 ДЕЗОДОРАНТ
# ============================================================

@dp.message(F.text == "🧴 Дезодорант")
async def deodorant_products(message: types.Message):

    if not is_director(message):
        return

    await show_products_category(message, "🧴 Дезодорант")


# ============================================================
# 🚗 АВТО ПАРФЮМ
# ============================================================

@dp.message(F.text == "🚗 Авто парфюм")
async def auto_products(message: types.Message):

    if not is_director(message):
        return

    await show_products_category(message, "🚗 Авто парфюм")


# ============================================================
# 🔙 КАТЕГОРИЯЛАРГА ҚАЙТИШ
# ============================================================

@dp.message(F.text == "⬅️ Категорияларга")
async def back_to_categories(message: types.Message):
 if not is_director(message):
        return

 await products_message(message)

@dp.message(F.text == "📥 Кирим")
async def income_message(
    message: types.Message
):

    await message.answer(
        "📥 Кирим модули кейинги босқичда "
        "уланади."
    )


@dp.message(F.text == "📤 Сотув")
async def sale_message(
    message: types.Message
):

    await message.answer(
        "📤 Сотув модули кейинги босқичда "
        "уланади."
    )


@dp.message(F.text == "🗑 Списание")
async def writeoff_message(
    message: types.Message
):

    await message.answer(
        "🗑 Списание модули кейинги босқичда "
        "уланади."
    )


@dp.message(F.text == "📊 Ҳисобот")
async def report_message(
    message: types.Message
):

    await message.answer(
        "📊 Ҳисобот модули кейинги босқичда "
        "уланади.\n\n"
        "Сана бўйича ҳисобот ҳам қўшилади."
    )


@dp.message(F.text == "📦 Остаток")
async def stock_message(
    message: types.Message
):
  await message.answer(
        "📦 Остаток модули кейинги босқичда "
        "уланади."
    )


# =========================================================
# FALLBACK
# =========================================================

@dp.message()
async def fallback(
    message: types.Message
):

    if is_director(message):

        await message.answer(
            "Менюдан керакли бўлимни танланг.",
            reply_markup=director_menu()
        )

    else:

        await message.answer(
            "⏳ Сизга ҳали доступ берилмаган.\n\n"
            "Директор тасдиғини кутинг."
        )


# =========================================================
# MAIN
# =========================================================

async def main():

    init_db()

    print(
        "Shaik Perfume bot ишга тушди..."
    )

    await dp.start_polling(bot)


if __name__== "__main__":

    asyncio.run(main())
