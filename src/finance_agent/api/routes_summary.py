from fastapi import APIRouter, HTTPException

from finance_agent.services.account_insights import AccountInsightsService


router = APIRouter(prefix="/api/summary", tags=["summary"])


@router.get("/accounts")
def linked_account_insights() -> dict:
    try:
        service = AccountInsightsService()
        return service.generate()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to generate account insights: {exc}") from exc
