from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from ..keyboards import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Салом! Мен ИИ ёрдамчиман. Қуйидаги менюлардан танланг:",
        reply_markup=main_menu,
    )
