import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    local_llm_base_url: str = os.getenv("LOCAL_LLM_BASE_URL", "http://127.0.0.1:8080/v1")
    local_llm_model: str = os.getenv("LOCAL_LLM_MODEL", "mlx-community/Qwen3.5-9B-OptiQ-4bit")
    local_llm_api_key: str = os.getenv("LOCAL_LLM_API_KEY", "not-used")
    plaid_client_id: str = os.getenv("PLAID_CLIENT_ID", "")
    plaid_secret: str = os.getenv("PLAID_SECRET", "")
    plaid_env: str = os.getenv("PLAID_ENV", "sandbox").lower()
    plaid_products: tuple[str, ...] = tuple(
        item.strip() for item in os.getenv("PLAID_PRODUCTS", "transactions").split(",") if item.strip()
    )
    plaid_country_codes: tuple[str, ...] = tuple(
        item.strip() for item in os.getenv("PLAID_COUNTRY_CODES", "US").split(",") if item.strip()
    )
    plaid_redirect_uri: str | None = os.getenv("PLAID_REDIRECT_URI") or None
    database_path: str = os.getenv("DATABASE_PATH", "./finance_agent.db")

    def require_plaid_credentials(self) -> None:
        if not self.plaid_client_id or not self.plaid_secret:
            raise ValueError("PLAID_CLIENT_ID and PLAID_SECRET must be set in your environment.")


def get_settings() -> Settings:
    return Settings()
