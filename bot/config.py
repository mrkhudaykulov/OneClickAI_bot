import json
import re
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    telegram_bot_token: str = Field(..., validation_alias="TELEGRAM_BOT_TOKEN")
    openai_api_key: str = Field(..., validation_alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", validation_alias="OPENAI_MODEL")
    admin_ids: List[int] = Field(default_factory=list, validation_alias="ADMIN_IDS")
    # If set, this code can toggle monetization via /monet on <code>
    monetization_activation_code: str = Field("", validation_alias="MONETIZATION_CODE")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, raw_value):
        if raw_value is None or raw_value == "":
            return []
        if isinstance(raw_value, (list, tuple)):
            return [int(element) for element in raw_value]
        if isinstance(raw_value, str):
            try:
                parsed = json.loads(raw_value)
                if isinstance(parsed, list):
                    return [int(element) for element in parsed]
            except Exception:
                pass
            parts = [part.strip() for part in re.split(r"[,\s]+", raw_value) if part.strip()]
            return [int(part) for part in parts]
        return raw_value

settings = Settings()
