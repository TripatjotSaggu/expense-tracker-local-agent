from __future__ import annotations

from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest as PlaidLinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products

from finance_agent.config import get_settings
from finance_agent.plaid.client import get_plaid_client
from finance_agent.plaid.schemas import (
    ExchangePublicTokenResponse,
    LinkTokenCreateRequest,
    LinkTokenCreateResponse,
)


class PlaidService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = get_plaid_client()

    def create_link_token(self, payload: LinkTokenCreateRequest) -> LinkTokenCreateResponse:
        request = PlaidLinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=payload.client_user_id),
            client_name=payload.client_name,
            products=[Products(product) for product in self.settings.plaid_products],
            country_codes=[CountryCode(code) for code in self.settings.plaid_country_codes],
            language=payload.language,
            redirect_uri=self.settings.plaid_redirect_uri,
        )
        response = self.client.link_token_create(request)
        data = response.to_dict()
        return LinkTokenCreateResponse(
            link_token=data["link_token"],
            expiration=str(data.get("expiration")) if data.get("expiration") else None,
            request_id=data.get("request_id"),
        )

    def exchange_public_token(self, public_token: str) -> ExchangePublicTokenResponse:
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = self.client.item_public_token_exchange(request)
        data = response.to_dict()
        return ExchangePublicTokenResponse(
            access_token=data["access_token"],
            item_id=data["item_id"],
            request_id=data.get("request_id"),
        )
