from typing import List, Dict, Any
import os
from openai import OpenAI
from ..config import settings

_client: OpenAI | None = None


def get_openai() -> OpenAI:
    global _client
    if _client is None:
        api_key = settings.openai_api_key or os.environ.get("OPENAI_API_KEY")
        _client = OpenAI(api_key=api_key)
    return _client


def vision_chat(messages: List[Dict[str, Any]], model: str | None = None, max_tokens: int = 500) -> str:
    client = get_openai()
    mdl = model or settings.openai_model
    resp = client.chat.completions.create(
        model=mdl,
        messages=messages,
        temperature=0.2,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content or ""
