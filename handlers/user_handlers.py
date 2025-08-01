from handlers.common import register_common_handlers
from handlers.buy import register_buy_handlers
from handlers.cabinet import register_cabinet_handlers
from handlers.prices import register_price_handlers
from handlers.acception_user_handler import register_acception_handlers


def register_user_handlers(bot):
    register_common_handlers(bot)
    register_buy_handlers(bot)
    register_cabinet_handlers(bot)
    register_price_handlers(bot)
    register_acception_handlers(bot)
