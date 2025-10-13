from pydantic import BaseSettings, Field
from typing import List

class Settings(BaseSettings):
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", alias="OPENAI_MODEL")
    admin_ids: List[int] = Field(default_factory=list, alias="ADMIN_IDS")
    # If set, this code can toggle monetization via /monet on <code>
    monetization_activation_code: str = Field("", alias="MONETIZATION_CODE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
