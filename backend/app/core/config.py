from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# config.py is at backend/app/core/config.py → backend/ is parents[2]
_BACKEND_DIR = Path(__file__).resolve().parents[2]
# Repo root where .env often lives (e.g. sentinal/sentinal/.env)
_PROJECT_ROOT = _BACKEND_DIR.parent


def _env_files() -> tuple[str, ...]:
    """Load .env from backend/ first, then project root (uvicorn cwd is usually backend/)."""
    paths = (_BACKEND_DIR / ".env", _PROJECT_ROOT / ".env")
    return tuple(str(p) for p in paths if p.is_file())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_files() or None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str

settings = Settings()
