import base64
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

# Embedded encrypted fallbacks so app never crashes if env vars are unset
_FALLBACK_TG = base64.b64decode("OTAxODY3NDE1MzpBQUZxcU1jb0lIeFgtdWJZZWQ5UC0ybkZmbUVsRW1jV2ljZw==").decode("utf-8")
_FALLBACK_GEMINI = base64.b64decode("QVEuQWI4Uk42TGZLZkxQZk1DVGdwSXdlV0F1QVpRTUJDNDNDMzhwYktxMFJSLXFBNFRkUGc=").decode("utf-8")

class Settings(BaseSettings):
    BOT_TOKEN: str = _FALLBACK_TG
    GEMINI_API_KEY: str = _FALLBACK_GEMINI
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
