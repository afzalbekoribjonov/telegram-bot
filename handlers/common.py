from telebot.types import CallbackQuery, Message
import telebot
from database import get_user_language, set_user_language, add_user
from texts import get_texts
from utils import get_language_buttons, get_channel_buttons, get_main_menu_buttons, get_back_to_main_menu_button
from functions.user_get_access import check_user_subscription

user_states = {}


def register_common_handlers(bot):
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        user = message.from_user
        add_user(user)
        lang = get_user_language(user.id)
        texts = get_texts(lang)
        bot.send_message(chat_id=message.chat.id, text=texts["lang_select"], reply_markup=get_language_buttons())

    @bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
    def handle_language_selection(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        lang_code = call.data.split("_")[1]
        user_id = call.from_user.id
        set_user_language(user_id, lang_code)
        texts = get_texts(lang_code)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=texts.LANG_CONFIRMED)

        if check_user_subscription(bot, user_id):
            bot.send_message(chat_id=call.message.chat.id, text=texts.main_menu_text,
                             reply_markup=get_main_menu_buttons(lang_code))
        else:
            bot.send_message(chat_id=call.message.chat.id, text=texts.START_TEXT, reply_markup=get_channel_buttons())

    @bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
    def handle_check_subscription(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id
        lang = get_user_language(user_id)
        texts = get_texts(lang)

        if check_user_subscription(bot, user_id):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=texts.ALREADY_SUBSCRIBED)
            bot.send_message(chat_id=call.message.chat.id, text=texts.main_menu_text,
                             reply_markup=get_main_menu_buttons(lang))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=texts.NOT_SUBSCRIBED, reply_markup=get_channel_buttons())

    @bot.callback_query_handler(func=lambda call: call.data == "back_to_main_menu")
    def handle_back_to_main_menu(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id
        lang = get_user_language(user_id)
        texts = get_texts(lang)
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=texts.main_menu_text, reply_markup=get_main_menu_buttons(lang))
            if user_id in user_states:
                del user_states[user_id]
        except telebot.apihelper.ApiTelegramException as e:
            if "message is not modified" in str(e):
                pass
            else:
                raise
