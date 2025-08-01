from config import REQUIRED_CHANNELS
from telebot import TeleBot
import logging


def check_user_subscription(bot: TeleBot, user_id: int) -> bool:
    """
    Foydalanuvchi barcha kerakli kanallarga obuna bo'lganligini tekshiradi.
    :param bot: TeleBot obyekt
    :param user_id: foydalanuvchi IDsi
    :return: True (obuna bo'lgan) yoki False (yo'q)
    """
    valid_statuses = {"member", "creator", "administrator"}

    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel["username"], user_id)
            if member.status not in valid_statuses:
                return False
        except Exception as e:
            logging.warning(f"Error checking subscription for {channel['username']}: {e}")
            return False

    return True
