from telebot.types import CallbackQuery, Message
from database import get_user_language, get_all_prices
from texts import get_texts
from utils import get_back_to_main_menu_button
from .common import user_states


def register_price_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data == "main_menu:view_prices")
    def handle_view_prices(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id
        lang = get_user_language(user_id)
        texts = get_texts(lang)
        prices = get_all_prices()

        if not prices:
            price_text = f"⚠️ <b>{texts.no_price_found}</b>"
        else:
            price_text = f"💎 <b><u>{texts.view_prices}</u></b>\n\n"
            for name, price_uzs, price_rub in prices:
                if name == "100":
                    price_text += (
                        f"🇺🇿 <b>{texts.currency_uzs}:</b>\n"
                        f"├ 💎 100 ➤ <code>{1 * price_uzs:,} so'm</code>\n"
                        f"├ 💎 200 ➤ <code>{2 * price_uzs:,} so'm</code>\n"
                        f"├ 💎 300 ➤ <code>{3 * price_uzs:,} so'm</code>\n"
                        f"├ 💎 400 ➤ <code>{4 * price_uzs:,} so'm</code>\n"
                        f"└ 💎 500 ➤ <code>{5 * price_uzs:,} so'm</code>\n\n"
                        f"🇷🇺 <b>{texts.currency_rub}:</b>\n"
                        f"├ 💎 100 ➤ <code>{1 * price_rub:,} ₽</code>\n"
                        f"├ 💎 200 ➤ <code>{2 * price_rub:,} ₽</code>\n"
                        f"├ 💎 300 ➤ <code>{3 * price_rub:,} ₽</code>\n"
                        f"├ 💎 400 ➤ <code>{4 * price_rub:,} ₽</code>\n"
                        f"└ 💎 500 ➤ <code>{5 * price_rub:,} ₽</code>\n\n"
                    )

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=price_text,
                              reply_markup=get_back_to_main_menu_button(lang), parse_mode="HTML")

    @bot.callback_query_handler(func=lambda call: call.data == "main_menu:calculate")
    def handle_calculate(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id
        lang = get_user_language(user_id)
        texts = get_texts(lang)

        user_states[user_id] = "waiting_calculate_number"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=texts.enter_number_to_calculate, reply_markup=get_back_to_main_menu_button(lang),
                              parse_mode="HTML")

    @bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_calculate_number")
    def process_calculate_number(message: Message):
        user_id = message.from_user.id
        lang = get_user_language(user_id)
        texts = get_texts(lang)

        if not message.text or not message.text.isdigit():
            bot.send_message(message.chat.id, texts.invalid_number_for_calculation)
            return

        entered_number = int(message.text)
        prices = get_all_prices()
        base_price_uzs, base_price_rub = 0, 0
        if prices:
            for name, price_uzs, price_rub in prices:
                if name == "100":
                    base_price_uzs = price_uzs
                    base_price_rub = price_rub
                    break

        if not (base_price_uzs and base_price_rub):
            bot.send_message(message.chat.id, texts.no_price_found)
            return

        multiplier = entered_number / 100.0
        calculated_uzs = int(multiplier * base_price_uzs)
        calculated_rub = int(multiplier * base_price_rub)

        calculation_result_text = texts.calculation_result.format(
            entered_number=entered_number,
            calculated_uzs=calculated_uzs,
            calculated_rub=calculated_rub
        )

        bot.send_message(chat_id=message.chat.id, text=calculation_result_text,
                         reply_markup=get_back_to_main_menu_button(lang), parse_mode="HTML")

        if user_id in user_states:
            del user_states[user_id]
