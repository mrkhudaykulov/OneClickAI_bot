import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from .config import settings
from .db import init_db, set_setting
from .handlers.start import router as start_router
from .handlers.photo_services import router as photo_router
from .handlers.fitness import router as fitness_router
from .handlers_admin import router as admin_router
from .handlers_group_events import router as group_router


async def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    # Initialize DB and seed bot username
    await init_db()
    bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        me = await bot.get_me()
        if me.username:
            await set_setting("BOT_USERNAME", me.username)
    except Exception:
        pass
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(photo_router)
    dp.include_router(fitness_router)
    dp.include_router(admin_router)
    dp.include_router(group_router)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
