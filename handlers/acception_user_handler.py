import telebot
from telebot.types import CallbackQuery
from database import get_user_language, add_diamonds_to_user
from texts import get_texts
from .buy import user_states


def register_acception_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith(("accept_payment:", "decline_payment:")))
    def handle_payment_action(call: CallbackQuery):
        # 1. Callback ma'lumotlarini ajratib olish
        order_id = int(call.data.split(":")[1])
        action = call.data.split(":")[0]  # "accept_payment" yoki "decline_payment"
        admin_id = call.from_user.id
        admin_first_name = call.from_user.first_name

        # 2. Xabar ma'lumotlarini user_states'dan olish
        if order_id not in user_states:
            bot.answer_callback_query(call.id, text="Xato: Bu buyurtma allaqachon ko'rib chiqilgan.", show_alert=True)
            return

        order_info = user_states[order_id]
        admin_messages = order_info.get("admin_messages", {})
        diamond_count = order_info.get("diamond_count")

        # 3. Adminlarga javob qaytarish
        action_text = "Qabul qilindi" if action == "accept_payment" else "Bekor qilindi"
        bot.answer_callback_query(call.id, text=action_text)

        # 4. Buyurtma holatiga qarab amallarni bajarish
        status_text = ""
        if action == "accept_payment":
            status_text = f"\n\n✅ Buyurtma {admin_first_name} tomonidan qabul qilindi."
            # Olmoslarni foydalanuvchi hisobiga qo'shish
            add_diamonds_to_user(order_id, diamond_count)
        else:
            status_text = f"\n\n❌ Buyurtma {admin_first_name} tomonidan bekor qilindi."

        new_text = call.message.caption + status_text

        # 5. Barcha adminlar uchun xabarni tahrirlash
        for a_id, msg_id in admin_messages.items():
            try:
                bot.edit_message_caption(
                    chat_id=a_id,
                    message_id=msg_id,
                    caption=new_text,
                    reply_markup=None,  # Tugmalarni o'chirish
                    parse_mode="HTML"
                )
            except telebot.apihelper.ApiTelegramException as e:
                if "message to edit not found" in str(e) or "message is not modified" in str(e):
                    print(f"Failed to edit message for admin {a_id} (ID: {msg_id}): {e}")
                    continue
                else:
                    print(f"An unexpected error occurred while editing message for admin {a_id}: {e}")
                    raise

        # 6. Jarayon tugagach, user_states'dagi ma'lumotni tozalash
        del user_states[order_id]

        # 7. Foydalanuvchiga buyurtma holati haqida xabar yuborish
        lang = get_user_language(order_id)
        texts = get_texts(lang)
        final_user_text = texts.order_accepted_text if action == "accept_payment" else texts.order_declined_text

        try:
            bot.send_message(order_id, final_user_text, parse_mode="HTML")
            if action == "accept_payment":
                bot.send_message(order_id, texts.done_diamond, parse_mode="HTML")
                bot.send_message(order_id, "✅✅", parse_mode="HTML")
        except Exception as e:
            pass

