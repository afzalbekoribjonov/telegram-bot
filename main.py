import telebot
import os

from config import BOT_TOKEN, SUPER_ADMIN_ID
from utils import get_language_buttons
from database import get_user_language, export_users_to_excel, add_user, init_db, get_all_admins
from texts import get_texts
from handlers import register_all_handlers

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    add_user(message.from_user)
    lang = get_user_language(user_id)
    texts = get_texts(lang)
    bot.send_message(
        chat_id=message.chat.id,
        text=texts.LANG_SELECT_TEXT,
        reply_markup=get_language_buttons()
    )


@bot.message_handler(commands=['user'])
def export_and_send_users(message):
    user_id = message.from_user.id
    admins_from_db = get_all_admins()
    admin_ids_from_db = [admin.telegram_id for admin in admins_from_db]

    allowed_admin_ids = admin_ids_from_db or [SUPER_ADMIN_ID]
    if SUPER_ADMIN_ID not in allowed_admin_ids:
        allowed_admin_ids.append(SUPER_ADMIN_ID)

    if user_id not in allowed_admin_ids:
        bot.send_message(message.chat.id, "Sizda bu buyruqqa ruxsat yo'q!")
        return

    file_path = export_users_to_excel()
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)
    os.remove(file_path)


if __name__ == '__main__':
    init_db()
    register_all_handlers(bot)
    print("Bot is starting...")
    bot.infinity_polling(skip_updates=True)
