import os
import telebot
from telebot.types import CallbackQuery, Message
from config import SUPER_ADMIN_ID
from database import (
    is_admin,
    add_admin,
    export_users_to_excel,
    get_user_language,
    set_price, get_all_admins, remove_admin
)
from texts import get_texts
from utils import get_admin_main_buttons, get_main_menu_buttons

admin_states = {}


def register_admin_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == "UMIDSHOX")
    def handle_admin_entry(message):
        user_id = message.from_user.id
        lang = get_user_language(user_id)
        texts = get_texts(lang)

        if not is_admin(user_id):
            if user_id == SUPER_ADMIN_ID:
                add_admin(user_id)
            else:
                bot.send_message(message.chat.id, texts.not_admin)
                return

        bot.send_message(
            chat_id=message.chat.id,
            text=texts.admin_panel,
            reply_markup=get_admin_main_buttons(lang)
        )

    def admin_check(call: CallbackQuery) -> bool:
        user_id = call.from_user.id
        lang = get_user_language(user_id)
        texts = get_texts(lang)

        if not is_admin(user_id):
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=texts.not_admin
                )
            except telebot.apihelper.ApiTelegramException as e:
                pass
            return False
        print(f"[{user_id}] admin_check: User IS an admin.")
        return True

    @bot.callback_query_handler(func=lambda call: call.data == "admin:export_users")
    def export_users_handler(call: CallbackQuery):
        bot.answer_callback_query(call.id)  # <--- CRUCIAL: Acknowledge the callback

        lang = get_user_language(call.from_user.id)
        texts = get_texts(lang)

        try:
            file_path = export_users_to_excel()
            with open(file_path, "rb") as f:
                bot.send_document(call.message.chat.id, f)
            os.remove(file_path)
        except Exception as e:
            bot.send_message(call.message.chat.id, texts.error)

    @bot.callback_query_handler(func=lambda call: call.data == "admin:back")
    def back_handler(call: CallbackQuery):
        bot.answer_callback_query(call.id)  # <--- CRUCIAL: Acknowledge the callback

        lang = get_user_language(call.from_user.id)
        texts = get_texts(lang)

        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=texts.main_menu_text,
                reply_markup=get_main_menu_buttons(lang)
            )
        except telebot.apihelper.ApiTelegramException as e:
            pass

    @bot.callback_query_handler(func=lambda call: call.data == "admin:set_price")
    def set_price_handler(call: CallbackQuery):
        bot.answer_callback_query(call.id)  # <--- CRUCIAL: Acknowledge the callback

        lang = get_user_language(call.from_user.id)
        texts = get_texts(lang)

        admin_states[call.from_user.id] = "waiting_price_uzs"
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=texts.enter_price_uzs,
            reply_markup=None  # Remove old inline keyboard
        )

    @bot.callback_query_handler(func=lambda call: call.data == "admin:add_admin")
    def add_admin_handler(call: CallbackQuery):
        bot.answer_callback_query(call.id)  # <--- CRUCIAL: Acknowledge the callback

        lang = get_user_language(call.from_user.id)
        texts = get_texts(lang)

        admin_states[call.from_user.id] = "waiting_admin_id"
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=texts.send_admin_id,
            reply_markup=None  # Remove old inline keyboard
        )

    @bot.callback_query_handler(func=lambda call: call.data == "admin:remove_admin")
    def remove_admin_handler(call: CallbackQuery):
        bot.answer_callback_query(call.id)  # <--- CRUCIAL: Acknowledge the callback

        lang = get_user_language(call.from_user.id)
        texts = get_texts(lang)

        admin_states[call.from_user.id] = "waiting_removing_admin_id"
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=texts.select_admin_to_remove,
            reply_markup=None  # Remove old inline keyboard
        )

    @bot.callback_query_handler(func=lambda call: call.data == "admin:admin_list")
    def admin_list_handler(call: CallbackQuery):
        bot.answer_callback_query(call.id)  # <--- CRUCIAL: Acknowledge the callback

        lang = get_user_language(call.from_user.id)
        texts = get_texts(lang)

        admins = get_all_admins()
        if admins:
            admin_list = "\n".join([f"👤 <code>{admin_id}</code>" for admin_id in admins if admin_id != bot.get_me().id])
            text = f"{texts.admin_list}\n{admin_list}"
        else:
            text = texts.no_admins_found

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode='HTML',
            reply_markup=get_admin_main_buttons(lang)
        )

    @bot.message_handler(func=lambda message: message.from_user.id in admin_states)
    def handle_admin_input(message: Message):
        user_id = message.from_user.id
        lang = get_user_language(user_id)
        texts = get_texts(lang)
        state = admin_states.get(user_id)

        if state == "waiting_price_uzs":
            if not message.text or not message.text.isdigit():
                bot.send_message(message.chat.id, texts.invalid_price)
                return
            admin_states[user_id] = {
                "step": "waiting_price_rub",
                "price_uzs": int(message.text)
            }
            bot.send_message(message.chat.id, texts.enter_price_rub)

        elif isinstance(state, dict) and state.get("step") == "waiting_price_rub":
            if not message.text or not message.text.isdigit():
                bot.send_message(message.chat.id, texts.invalid_price)
                return

            price_uzs = state["price_uzs"]
            price_rub = int(message.text)
            set_price("100", price_uzs, price_rub)

            bot.send_message(
                chat_id=message.chat.id,
                text=texts.success,
                reply_markup=get_admin_main_buttons(lang)  # Re-display admin buttons
            )
            del admin_states[user_id]

        elif state == "waiting_admin_id":
            if not message.text or not message.text.isdigit():
                bot.send_message(message.chat.id, texts.invalid_id)
                return
            new_admin_id = int(message.text)

            add_admin(new_admin_id)
            bot.send_message(
                chat_id=message.chat.id,
                text=texts.admin_added,
                reply_markup=get_admin_main_buttons(lang)  # Re-display admin buttons
            )
            del admin_states[user_id]

        elif state == "waiting_removing_admin_id":
            if not message.text or not message.text.isdigit():
                bot.send_message(message.chat.id, texts.invalid_id)
                return
            admin_id = int(message.text)

            # Assuming add_admin handles uniqueness or returns status
            remove_admin(admin_id)
            bot.send_message(
                chat_id=message.chat.id,
                text=texts.admin_removed_success,
                reply_markup=get_admin_main_buttons(lang)  # Re-display admin buttons
            )
            del admin_states[user_id]
