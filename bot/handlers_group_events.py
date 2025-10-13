from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.types import ChatMemberUpdated

from .db import upsert_group, set_group_active

router = Router()


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=True))
async def on_chat_member(update: ChatMemberUpdated):
    chat = update.chat
    if not chat.type.endswith("group"):
        return

    # Bot removed from group
    if KICKED.check(update):
        await set_group_active(chat.id, False)
        return

    # Bot became a member (added or returned)
    if MEMBER.check(update):
        await upsert_group(chat.id, chat.title or "", is_active=True)
        return
