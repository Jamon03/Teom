import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from user import user_login
from admin import admin_login

load_dotenv()
BOT_TOKEN = os.getenv("API")
if not BOT_TOKEN:
    raise ValueError("API token topilmadi! .env faylini tekshiring.")

logger = logging.getLogger(__name__)


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    user_login(dp)
    admin_login(dp)

    logger.info("🍽 MenuBot Restoran ishga tushmoqda...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("MenuBot to'xtatildi")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("bot_errors.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    asyncio.run(main())
