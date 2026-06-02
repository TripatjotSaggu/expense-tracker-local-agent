from fastapi import APIRouter, HTTPException

from finance_agent.plaid.schemas import (
    ExchangePublicTokenRequest,
    ExchangePublicTokenResponse,
    LinkTokenCreateRequest,
    LinkTokenCreateResponse,
)
from finance_agent.plaid.service import PlaidService


router = APIRouter(prefix="/api/plaid", tags=["plaid"])


@router.post("/link-token/create", response_model=LinkTokenCreateResponse)
def create_link_token(payload: LinkTokenCreateRequest) -> LinkTokenCreateResponse:
    try:
        service = PlaidService()
        return service.create_link_token(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Plaid link token creation failed: {exc}") from exc


@router.post("/exchange-public-token", response_model=ExchangePublicTokenResponse)
def exchange_public_token(payload: ExchangePublicTokenRequest) -> ExchangePublicTokenResponse:
    try:
        service = PlaidService()
        return service.exchange_public_token(payload.public_token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Plaid public token exchange failed: {exc}") from exc
