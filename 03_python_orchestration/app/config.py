import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT_ENV_FILE = Path(__file__).parents[2] / ".env"


def _default_service_url(offset: int) -> str:
    uid = os.getuid() if hasattr(os, "getuid") else 0
    port = 10000 + (uid % 6000) * 3 + offset
    return f"http://localhost:{port}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT_ENV_FILE, extra="ignore")

    openrouter_api_key: str = ""
    r_service_url: str = _default_service_url(0)
    py_data_url: str = _default_service_url(1)
    prompts_dir: Path = Path(__file__).parents[1] / "prompts"


settings = Settings()
