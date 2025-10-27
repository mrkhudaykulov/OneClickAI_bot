from typing import Optional
from .openai_client import vision_chat

from openai import OpenAI
from ..config import settings # API kalitini olish uchun
import logging

SYSTEM_CALORIES = (
    "Siz ovqat rasmlaridan taom nomi va porsiya uchun taxminiy kaloriya chiqaring. "
    "Natijani qisqa, punktli va o'zbek tilida bering. Eng muhim: taom (taxminan), kaloriya (kcal, 1 porsiya), 2-3 maslahat."
)

SYSTEM_RECIPE = (
    "Siz oshpaz yordamchisiz. Rasm asosida taom nomini va 6-10 qadamli qisqa retseptni (o'zbek tilida) chiqaring."
)

SYSTEM_PRODUCT = (
    "Siz vizual obyektlarni aniqlovchi yordamchisiz. Rasm asosida obyekt/tovar nomini aniqroq taxmin qiling va qisqa javob qaytaring."
)

SYSTEM_GENERAL = (
    "Siz yordamchi AI. O'zbek tilida qisqa va tushunarli javob bering."
)


logger = logging.getLogger(__name__)
OPENAI_CLIENT = OpenAI(api_key=settings.openai_api_key) # settings.openai_api_key mavjud deb faraz qilamiz

async def get_image_analysis_response(image_url: str, prompt: str) -> str:
    """OpenAI Vision API orqali rasmni tahlil qilish (URL orqali)"""
    try:
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4-vision-preview", # Yoki boshqa vision-enabled model
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]}
            ],
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Vision API Error: {e}")
        return "Rasm tahlilida texnik xato yuz berdi."


def analyze_calories(image_data_url: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_CALORIES},
        {"role": "user", "content": [
            {"type": "text", "text": "Taom rasmini tahlil qiling va natija bering."},
            {"type": "image_url", "image_url": {"url": image_data_url}},
        ]},
    ]
    return vision_chat(messages, max_tokens=500)


def identify_recipe(image_data_url: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_RECIPE},
        {"role": "user", "content": [
            {"type": "text", "text": "Taomni nomlang va retsept yozing."},
            {"type": "image_url", "image_url": {"url": image_data_url}},
        ]},
    ]
    return vision_chat(messages, max_tokens=700)


def identify_product(image_data_url: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PRODUCT},
        {"role": "user", "content": [
            {"type": "text", "text": "Obyekt yoki tovarni nomlang va qisqa ma'lumot bering."},
            {"type": "image_url", "image_url": {"url": image_data_url}},
        ]},
    ]
    return vision_chat(messages, max_tokens=400)
