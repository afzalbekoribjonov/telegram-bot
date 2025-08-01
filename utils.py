from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import REQUIRED_CHANNELS
from texts import get_texts

WEB_APP_URL = "https://likee-umidjon.netlify.app/"  # Sizning Netlify manzilingiz


# Til tanlash tugmalari
def get_language_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
        ]
    ])


# Kanalga obuna tugmalari
def get_channel_buttons(lang: str = 'uz') -> InlineKeyboardMarkup:
    t = get_texts(lang)
    markup = InlineKeyboardMarkup()
    for channel in REQUIRED_CHANNELS:
        markup.add(InlineKeyboardButton(text=channel['name'], url=channel['url']))
    markup.add(InlineKeyboardButton(f"✅ {t.check}", callback_data="check_subscription"))
    return markup


# Admin paneli menyusi
def get_admin_main_buttons(lang: str = 'uz') -> InlineKeyboardMarkup:
    t = get_texts(lang)
    buttons = [
        ("📊 " + t.set_price, "admin:set_price"),
        ("📤 " + t.export_users, "admin:export_users"),
        (t.admin_list, "admin:admin_list"),
        ("➕ " + t.add_admin, "admin:add_admin"),
        (t.remove_admin, "admin:remove_admin"),
        (t.back, "admin:back")
    ]
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(*[InlineKeyboardButton(text, callback_data=cb) for text, cb in buttons])
    return markup


# Foydalanuvchi asosiy menyusi
def get_main_menu_buttons(lang: str = 'uz') -> InlineKeyboardMarkup:
    t = get_texts(lang)
    buttons = [
        ("💎 " + t.buy, "main_menu:buy"),
        ("📈 " + t.calculate, "main_menu:calculate"),
        ("💰 " + t.withdraw, "main_menu:withdraw"),
        ("👤 " + t.my_cabinet, "main_menu:cabinet"),
        ("💵 " + t.view_prices, "main_menu:view_prices")
    ]
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(*[InlineKeyboardButton(text, callback_data=cb) for text, cb in buttons])
    return markup


# Asosiy menyuga qaytish tugmasi
def get_back_to_main_menu_button(lang: str = 'uz') -> InlineKeyboardMarkup:
    t = get_texts(lang)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 " + t.back_to_menu, callback_data="back_to_main_menu")]
    ])


def withdraw_button(lang: str = 'uz') -> InlineKeyboardMarkup:
    t = get_texts(lang)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=t.submit_application,
            web_app=WebAppInfo(url=WEB_APP_URL)  # <-- Endi bu to'g'ri ishlaydi
        )],
        [InlineKeyboardButton("🔙 " + t.back_to_menu, callback_data="back_to_main_menu")],
    ])


def get_card_buttons(lang):
    texts = get_texts(lang)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(texts.copy_humo_card, callback_data="copy:humo_card"))
    keyboard.add(InlineKeyboardButton(texts.copy_tbc_card, callback_data="copy:tbc_card"))
    return keyboard


def get_admin_action_buttons(order_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Qabul qilindi", callback_data=f"accept_payment:{order_id}"),
        InlineKeyboardButton("❌ Bekor qilindi", callback_data=f"decline_payment:{order_id}")
    )
    return keyboard
