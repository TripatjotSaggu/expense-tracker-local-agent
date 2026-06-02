from __future__ import annotations

from finance_agent.agent import summarize_linked_accounts
from finance_agent.analytics import build_account_summary
from finance_agent.storage.repository import PlaidRepository


class AccountInsightsService:
    def __init__(self) -> None:
        self.repository = PlaidRepository()

    def generate(self) -> dict:
        items = [item.to_record() for item in self.repository.list_items()]
        accounts = [account.to_record() for account in self.repository.list_accounts()]
        summary = build_account_summary(accounts=accounts, items=items)
        narrative = summarize_linked_accounts(summary)
        return {
            "summary": summary,
            "narrative": narrative,
        }
