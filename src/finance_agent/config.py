from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("LOCAL_LLM_BASE_URL", "http://127.0.0.1:8080/v1")
    model: str = os.getenv("LOCAL_LLM_MODEL", "mlx-community/Qwen3.5-9B-OptiQ-4bit")
    api_key: str = os.getenv("LOCAL_LLM_API_KEY", "not-used")


def get_settings() -> Settings:
    return Settings()
