import asyncio
from typing import Iterable

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramForbiddenError, TelegramNotFound, TelegramRetryAfter, TelegramBadRequest

from .config import settings
from .db import (
    get_setting,
    set_setting,
    list_user_ids,
    list_active_group_ids,
    remove_user,
    remove_group,
)

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in set(settings.admin_ids or [])


@router.message(Command("monet"))
async def monet_toggle(message: Message):
    if not _is_admin(message.from_user.id):
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) == 2 and settings.monetization_activation_code and parts[1].strip() == settings.monetization_activation_code:
            await set_setting("MONETIZATION_ENABLED", "true")
            await message.answer("Монетизация фаоллаштирилди ✅")
            return
        await message.answer("Сизда бу буйруқ учун рухсат йўқ.")
        return

    parts = (message.text or "").split()
    arg = parts[1] if len(parts) > 1 else None
    current = (await get_setting("MONETIZATION_ENABLED")) or "false"
    if arg in ("on", "enable", "1", "true"):
        new_val = "true"
    elif arg in ("off", "disable", "0", "false"):
        new_val = "false"
    else:
        new_val = "false" if current.lower() == "true" else "true"

    await set_setting("MONETIZATION_ENABLED", new_val)
    status = "ёқиқ" if new_val == "true" else "ўчирилган"
    await message.answer(f"Монетизация {status}.")


async def _safe_send(to_send_coros: Iterable, delay_sec: float = 0.1):
    # Utility to run coroutines sequentially with delay to respect flood limits
    for send_coro in to_send_coros:
        try:
            await send_coro
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 0.5)
            try:
                await send_coro
            except Exception:
                pass
        await asyncio.sleep(delay_sec)


@router.message(Command("broadcast_users"))
async def broadcast_users(message: Message):
    if not _is_admin(message.from_user.id):
        await message.answer("Рухсат йўқ.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Фойдаланувчиларга юбориш учун матн киритинг: /broadcast_users <матн>", 
                             parse_mode=None)
        return
    text = parts[1]

    user_ids = await list_user_ids()

    async def gen():
        for uid in user_ids:
            async def send_one(uid=uid):
                try:
                    await message.bot.send_message(uid, text)
                except (TelegramForbiddenError, TelegramNotFound, TelegramBadRequest):
                    # Blocked or chat not found -> cleanup user
                    await remove_user(uid)
                except Exception:
                    # Keep going for other users
                    pass
            yield send_one()

    await _safe_send([c async for c in gen()], delay_sec=0.1)
    await message.answer(f"Юборилди. Аудитория: {len(user_ids)}")


@router.message(Command("broadcast_groups"))
async def broadcast_groups(message: Message):
    if not _is_admin(message.from_user.id):
        await message.answer("Рухсат йўқ.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Гуруҳларга юбориш учун матн киритинг: /broadcast_groups <матн>", 
                             parse_mode=None)
        return
    text = parts[1]

    group_ids = await list_active_group_ids()

    async def gen():
        for gid in group_ids:
            async def send_one(gid=gid):
                try:
                    await message.bot.send_message(gid, text)
                except (TelegramForbiddenError, TelegramNotFound, TelegramBadRequest):
                    # Bot removed or cannot post -> cleanup group
                    await remove_group(gid)
                except Exception:
                    pass
            yield send_one()

    await _safe_send([c async for c in gen()], delay_sec=0.1)
    await message.answer(f"Юборилди. Гуруҳлар: {len(group_ids)}")


@router.message(Command("credits"))
async def credits_info(message: Message):
    # Small helper for users to check credits
    from .db import get_user_credits, ensure_user
    user = message.from_user
    await ensure_user(user.id, user.username, user.first_name, user.last_name)
    credits = await get_user_credits(user.id)
    await message.answer(f"Сизда қолган сўровлар: {credits}")
