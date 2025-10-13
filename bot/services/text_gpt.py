from openai import OpenAI
from ..config import settings
from .openai_client import get_openai

SYSTEM_WORKOUT = (
    "Siz fitnes murabbiysiz. O'zbek tilida, sodda va aniq, xavfsiz tavsiyalar bering."
)

SYSTEM_PLAN = (
    "Siz reja tuzuvchi murabbiy. 1 haftalik fitnes rejasini kichik bloklarga bo'lib yozing."
)

SYSTEM_DIET = (
    "Siz parhez bo'yicha maslahatchisiz. Berilgan ma'lumotlarga ko'ra qisqa tavsiyalar yozing."
)


def generate_workout_tips(goal: str, place: str) -> str:
    client: OpenAI = get_openai()
    messages = [
        {"role": "system", "content": SYSTEM_WORKOUT},
        {"role": "user", "content": f"Maqsad: {goal}. Joy: {place}. Qisqa mashq ro'yxati va texnika eslatmalari yozing."},
    ]
    resp = client.chat.completions.create(model=settings.openai_model, messages=messages, temperature=0.3, max_tokens=600)
    return resp.choices[0].message.content or ""


def generate_week_plan(details: str) -> str:
    client: OpenAI = get_openai()
    messages = [
        {"role": "system", "content": SYSTEM_PLAN},
        {"role": "user", "content": f"1 haftalik reja tuzing. Kirish ma'lumotlari: {details}"},
    ]
    resp = client.chat.completions.create(model=settings.openai_model, messages=messages, temperature=0.3, max_tokens=900)
    return resp.choices[0].message.content or ""


def diet_from_photo_or_text(calorie_hint: str) -> str:
    client: OpenAI = get_openai()
    messages = [
        {"role": "system", "content": SYSTEM_DIET},
        {"role": "user", "content": f"Tavsiyalar bering. Ma'lumot: {calorie_hint}"},
    ]
    resp = client.chat.completions.create(model=settings.openai_model, messages=messages, temperature=0.3, max_tokens=600)
    return resp.choices[0].message.content or ""
