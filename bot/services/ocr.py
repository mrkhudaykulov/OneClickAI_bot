from typing import Optional
from openai import OpenAI
from ..config import settings
from .openai_client import get_openai


SYSTEM_OCR = (
    "Siz OCR yordamchisiz. Rasm ichidagi matnni aniqlab, xatosiz va tartibli ko'rinishda qaytaring."
)


def ocr_image_to_text(image_data_url: str) -> str:
    client: OpenAI = get_openai()
    messages = [
        {"role": "system", "content": SYSTEM_OCR},
        {"role": "user", "content": [
            {"type": "text", "text": "Quyidagi rasm matnini aniq ko'chiring."},
            {"type": "image_url", "image_url": {"url": image_data_url}},
        ]},
    ]
    resp = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.0,
        max_tokens=1200,
    )
    return resp.choices[0].message.content or ""
