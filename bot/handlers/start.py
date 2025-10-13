from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from ..db import ensure_user

from ..keyboards import main_menu
from ..monetization import handle_joined_group_credit

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    # Ensure user recorded and provision free credits
    await ensure_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await message.answer(
        "Салом! Мен ИИ ёрдамчиман. Қуйидаги менюлардан танланг:",
        reply_markup=main_menu,
    )
    # If /start used inside a group where the bot was just added, try grant bonus
    try:
        await handle_joined_group_credit(message)
    except Exception:
        pass
