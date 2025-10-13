import base64
from io import BytesIO
from typing import Tuple
from aiogram import Bot
from aiogram.types import Message, PhotoSize

async def download_best_photo_bytes(bot: Bot, message: Message) -> bytes:
    if not message.photo:
        raise ValueError("No photo in message")
    photo: PhotoSize = message.photo[-1]
    buf = BytesIO()
    await bot.download(photo, destination=buf)
    return buf.getvalue()


def to_data_url(image_bytes: bytes, mime: str = "image/jpeg") -> str:
    b64 = base64.b64encode(image_bytes).decode()
    return f"data:{mime};base64,{b64}"


def chunk_text(text: str, limit: int = 3500) -> Tuple[str, str]:
    if len(text) <= limit:
        return text, ""
    return text[:limit], text[limit:]
