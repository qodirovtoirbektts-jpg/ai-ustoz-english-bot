"""Application configuration management via pydantic."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    BOT_TOKEN: str
    GEMINI_API_KEY: str
    DB_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'ai_ustoz.db'}"
    DEFAULT_LANG: str = "uz"
    TIMEZONE: str = "Asia/Tashkent"
    DEFAULT_VOICE: str = "en-US-AriaNeural"  # Microsoft Edge TTS voice
    TEMP_AUDIO_DIR: Path = BASE_DIR / "temp_audio"
    PORT: int | None = None

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
settings.TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
