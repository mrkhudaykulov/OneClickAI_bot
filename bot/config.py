from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Environment configuration for pydantic-settings (pydantic v2)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    telegram_bot_token: str = Field(..., validation_alias="TELEGRAM_BOT_TOKEN")
    openai_api_key: str = Field(..., validation_alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", validation_alias="OPENAI_MODEL")
    admin_ids: List[int] = Field(default_factory=list, validation_alias="ADMIN_IDS")
    # If set, this code can toggle monetization via /monet on <code>
    monetization_activation_code: str = Field("", validation_alias="MONETIZATION_CODE")

settings = Settings()
