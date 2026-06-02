from __future__ import annotations

import plaid
from plaid.api import plaid_api

from finance_agent.config import get_settings


ENVIRONMENT_MAP = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}


def get_plaid_client() -> plaid_api.PlaidApi:
    settings = get_settings()
    settings.require_plaid_credentials()

    try:
        host = ENVIRONMENT_MAP[settings.plaid_env]
    except KeyError as exc:
        raise ValueError(f"Unsupported Plaid environment: {settings.plaid_env}") from exc

    configuration = plaid.Configuration(
        host=host,
        api_key={
            "clientId": settings.plaid_client_id,
            "secret": settings.plaid_secret,
            "plaidVersion": "2020-09-14",
        },
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)
