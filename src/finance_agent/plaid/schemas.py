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
    access_token: str
    item_id: str
    request_id: str | None = None
