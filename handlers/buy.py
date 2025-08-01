from telebot.types import CallbackQuery, Message, ReplyKeyboardRemove
from database import get_user_language, get_all_prices, get_all_admins
from texts import get_texts
from utils import get_back_to_main_menu_button, get_admin_action_buttons
from config import SUPER_ADMIN_ID
from .common import user_states


def register_buy_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data == "main_menu:buy")
    def handle_buy_start(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id
        lang = get_user_language(user_id)
        texts = get_texts(lang)
        prices = get_all_prices()

        base_price_uzs = 0
        base_price_rub = 0
        if prices:
            for name, price_uzs, price_rub in prices:
                if name == "100":
                    base_price_uzs = price_uzs
                    base_price_rub = price_rub
                    break

        buy_text = texts.buy_intro_text.format(
            base_price_uzs=f"{base_price_uzs:,}",
            base_price_rub=f"{base_price_rub:,}"
        )

        user_states[user_id] = {"state": "waiting_buy_number"}

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=buy_text,
            reply_markup=get_back_to_main_menu_button(lang),
            parse_mode="HTML"
        )

    @bot.message_handler(
        func=lambda message: isinstance(user_states.get(message.from_user.id), dict) and
                             user_states.get(message.from_user.id, {}).get("state") == "waiting_buy_number")
    def process_buy_number(message: Message):
        user_id = message.from_user.id
        lang = get_user_language(user_id)
        texts = get_texts(lang)

        if not message.text or not message.text.isdigit():
            bot.send_message(message.chat.id, texts.invalid_number_for_buy_text, parse_mode='HTML')
            return

        diamond_count = int(message.text)
        if diamond_count < 100:
            bot.send_message(message.chat.id, texts.minimum_buy_text, parse_mode='HTML')
            return

        prices = get_all_prices()
        base_price_uzs = 0
        base_price_rub = 0
        if prices:
            for name, price_uzs, price_rub in prices:
                if name == "100":
                    base_price_uzs = price_uzs
                    base_price_rub = price_rub
                    break

        if not (base_price_uzs and base_price_rub):
            bot.send_message(message.chat.id, texts.no_price_found)
            return

        calculated_uzs = int((diamond_count / 100.0) * base_price_uzs)
        calculated_rub = int((diamond_count / 100.0) * base_price_rub)

        payment_text = texts.payment_info_text.format(
            diamond_count=diamond_count,
            calculated_uzs=calculated_uzs,
            calculated_rub=calculated_rub
        )
        bot.send_message(
            chat_id=message.chat.id,
            text=payment_text,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML"
        )

        bot.send_message(
            chat_id=message.chat.id,
            text=texts.card_details_text,
            reply_markup=get_back_to_main_menu_button(lang),
            parse_mode="HTML"
        )

        user_states[user_id] = {"state": "waiting_payment_proof", "diamond_count": diamond_count}

    @bot.message_handler(content_types=['photo', 'document'],
                         func=lambda message: isinstance(user_states.get(message.from_user.id), dict) and
                                              user_states.get(message.from_user.id, {}).get(
                                                  "state") == "waiting_payment_proof")
    def process_payment_proof(message: Message):
        user_id = message.from_user.id
        lang = get_user_language(user_id)
        texts = get_texts(lang)
        diamond_count = user_states[user_id].get("diamond_count")

        full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
        username = f"@{message.from_user.username}" if message.from_user.username else "–"

        admin_message_text = texts.admin_buy_order_text.format(
            full_name=full_name,
            username=username,
            user_id=user_id,
            diamond_count=diamond_count
        )

        all_admins = get_all_admins()

        admin_messages = {}

        for admin_id in all_admins + [SUPER_ADMIN_ID]:
            try:
                sent_message = None
                if message.photo:
                    sent_message = bot.send_photo(chat_id=admin_id, photo=message.photo[-1].file_id,
                                                  caption=admin_message_text,
                                                  reply_markup=get_admin_action_buttons(order_id=user_id),
                                                  parse_mode="HTML")
                elif message.document:
                    sent_message = bot.send_document(chat_id=admin_id, document=message.document.file_id,
                                                     caption=admin_message_text,
                                                     reply_markup=get_admin_action_buttons(order_id=user_id),
                                                     parse_mode="HTML")

                if sent_message:
                    admin_messages[admin_id] = sent_message.message_id

            except Exception as e:
                print(f"Failed to send payment proof to admin {admin_id}: {e}")

        bot.send_message(
            chat_id=user_id,
            text=texts.buy_order_confirmation,
            reply_markup=get_back_to_main_menu_button(lang),
            parse_mode="HTML"
        )

        if user_id in user_states:
            user_states[user_id]["admin_messages"] = admin_messages
            user_states[user_id]["state"] = "waiting_for_admin_action"

    @bot.message_handler(content_types=['text'],
                         func=lambda message: isinstance(user_states.get(message.from_user.id), dict) and
                                              user_states.get(message.from_user.id, {}).get(
                                                  "state") == "waiting_payment_proof")
    def process_invalid_payment_proof(message: Message):
        user_id = message.from_user.id
        lang = get_user_language(user_id)
        texts = get_texts(lang)
        bot.send_message(message.chat.id, texts.invalid_payment_proof_text)
