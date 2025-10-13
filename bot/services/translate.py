from openai import OpenAI
from ..config import settings
from .openai_client import get_openai

SYSTEM_TRANSLATE = (
    "Siz tarjimon yordamchisiz. Berilgan matnni ko'rsatilgan tilga aniq, soddalashtirmay va izohsiz tarjima qiling."
    " Faqat tarjimani chiqaring, qo'shimcha matn yozmang."
)


def translate_text(text: str, target_lang: str) -> str:
    client: OpenAI = get_openai()
    messages = [
        {"role": "system", "content": SYSTEM_TRANSLATE},
        {"role": "user", "content": f"Til: {target_lang}. Matnni tarjima qiling:\n{text}"},
    ]
    resp = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.0,
        max_tokens=1200,
    )
    return resp.choices[0].message.content or ""
