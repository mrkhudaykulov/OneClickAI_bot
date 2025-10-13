from typing import Optional

from aiogram.types import Message
from aiogram import Bot

from .db import (
    get_setting,
    ensure_user,
    get_user_credits,
    consume_user_credit,
    claim_group_bonus,
)
from .keyboards import monet_cta_keyboard


async def is_monetization_enabled() -> bool:
    val = await get_setting("MONETIZATION_ENABLED")
    return (val or "false").lower() == "true"


async def ensure_user_and_gate(message: Message, *, consume: bool = True) -> bool:
    """
    Ensure user exists. If monetization enabled, consume a credit or show CTA.
    Returns True if allowed to proceed; False if blocked and CTA is shown.
    """
    user = message.from_user
    await ensure_user(user.id, user.username, user.first_name, user.last_name)

    if not await is_monetization_enabled():
        return True

    if not consume:
        return True

    credits = await get_user_credits(user.id)
    if credits <= 0:
        bot_username = await get_setting("BOT_USERNAME") or ""
        await message.answer(
            "Лимитингиз тугади. Premium обуна ёки ботни янги гуруҳга қўшиб 5 та қўшимча сўров олинг.",
            reply_markup=monet_cta_keyboard(bot_username=bot_username),
        )
        return False

    ok = await consume_user_credit(user.id, 1)
    if not ok:
        bot_username = await get_setting("BOT_USERNAME") or ""
        await message.answer(
            "Лимитингиз тугади. Premium обуна ёки ботни янги гуруҳга қўшиб 5 та қўшимча сўров олинг.",
            reply_markup=monet_cta_keyboard(bot_username=bot_username),
        )
        return False

    return True


async def handle_joined_group_credit(message: Message) -> None:
    """If user just added the bot to a new group, try award group bonus."""
    chat = message.chat
    if not chat.type.endswith("group"):
        return
    user = message.from_user
    if not user:
        return
    try:
        granted = await claim_group_bonus(chat.id, user.id)
        if granted:
            await message.answer("Раҳмат! Янги гуруҳга қўшганингиз учун 5 та қўшимча сўров берилди.")
    except Exception:
        # Silent; no disruption in groups
        pass
