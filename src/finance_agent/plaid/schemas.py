from pydantic import BaseModel, Field


class LinkTokenCreateRequest(BaseModel):
    client_user_id: str = Field(..., description="Stable user identifier for Plaid Link")
    client_name: str = Field(default="Expense Tracker Local Agent")
    language: str = Field(default="en")


class LinkTokenCreateResponse(BaseModel):
    link_token: str
    expiration: str | None = None
    request_id: str | None = None


class ExchangePublicTokenRequest(BaseModel):
    public_token: str


class ExchangePublicTokenResponse(BaseModel):
    item_id: str
    request_id: str | None = None
    accounts_persisted: int = 0


class ItemRecord(BaseModel):
    item_id: str
    institution_id: str | None = None
    institution_name: str | None = None
    created_at: str
    updated_at: str


class AccountRecord(BaseModel):
    account_id: str
    item_id: str
    name: str
    official_name: str | None = None
    mask: str | None = None
    type: str | None = None
    subtype: str | None = None
    current_balance: float | None = None
    available_balance: float | None = None
    iso_currency_code: str | None = None
    credit_limit: float | None = None
    created_at: str
    updated_at: str
