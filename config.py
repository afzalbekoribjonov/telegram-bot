import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing in the .env file")

# Kerakli obuna kanallari
REQUIRED_CHANNELS = [
    {
        "name": "Likee Pay",
        "url": "https://t.me/likee_pay",
        "username": "@likee_pay"
    }
]

# Tillar
DEFAULT_LANGUAGE = 'uz'
SUPPORTED_LANGUAGES = ['uz', 'ru']

# Super admin ID
SUPER_ADMIN_ID = 5899057322
