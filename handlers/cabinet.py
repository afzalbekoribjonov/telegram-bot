from telebot.types import CallbackQuery
from database import get_user_language, get_user_balance, get_user_type
from texts import get_texts
from utils import get_back_to_main_menu_button, withdraw_button


def register_cabinet_handlers(bot):

    @bot.callback_query_handler(func=lambda call: call.data == "main_menu:cabinet")
    def handle_my_cabinet(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id
        lang = get_user_language(user_id)
        texts = get_texts(lang)

        balance = get_user_balance(user_id)
        user_type = get_user_type(user_id)

        full_name = f"{call.from_user.first_name or ''} {call.from_user.last_name or ''}".strip()
        username = f"@{call.from_user.username}" if call.from_user.username else "–"

        text = texts.my_cabinet_text.format(
            user_id=user_id,
            full_name=full_name,
            username=username,
            balance=balance,
            user_type=user_type
        )

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                              reply_markup=get_back_to_main_menu_button(lang), parse_mode="HTML")

    @bot.callback_query_handler(func=lambda call: call.data == "main_menu:withdraw")
    def handle_withdraw(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id
        lang = get_user_language(user_id)
        texts = get_texts(lang)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=texts.withdraw_intro_text, reply_markup=withdraw_button(lang), parse_mode="HTML")

