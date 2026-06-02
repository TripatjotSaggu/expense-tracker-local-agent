from __future__ import annotations

from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest as PlaidLinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products

from finance_agent.config import get_settings
from finance_agent.plaid.client import get_plaid_client
from finance_agent.plaid.schemas import (
    AccountRecord,
    ExchangePublicTokenResponse,
    ItemRecord,
    LinkTokenCreateRequest,
    LinkTokenCreateResponse,
)
from finance_agent.storage.db import initialize_database
from finance_agent.storage.models import Account, PlaidItem
from finance_agent.storage.repository import PlaidRepository


class PlaidService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = get_plaid_client()
        initialize_database()
        self.repository = PlaidRepository()

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
        accounts_response = self.client.accounts_get(AccountsGetRequest(access_token=data["access_token"]))
        accounts_payload = accounts_response.to_dict()

        item = PlaidItem(
            item_id=data["item_id"],
            access_token=data["access_token"],
            institution_id=accounts_payload.get("item", {}).get("institution_id"),
            institution_name=accounts_payload.get("item", {}).get("institution_name"),
        )
        accounts = [
            Account.from_plaid_dict(account=account, item_id=data["item_id"])
            for account in accounts_payload.get("accounts", [])
        ]
        self.repository.upsert_item(item)
        self.repository.upsert_accounts(accounts)

        return ExchangePublicTokenResponse(
            item_id=data["item_id"],
            request_id=data.get("request_id"),
            accounts_persisted=len(accounts),
        )

    def list_items(self) -> list[ItemRecord]:
        return [ItemRecord(**item.to_record()) for item in self.repository.list_items()]

    def list_accounts(self) -> list[AccountRecord]:
        return [AccountRecord(**account.to_record()) for account in self.repository.list_accounts()]
