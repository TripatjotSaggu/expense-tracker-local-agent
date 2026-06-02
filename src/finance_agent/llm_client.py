from __future__ import annotations

from openai import OpenAI

from finance_agent.config import get_settings



def get_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(base_url=settings.local_llm_base_url, api_key=settings.local_llm_api_key)
