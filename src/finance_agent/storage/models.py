from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class PlaidItem:
    item_id: str
    access_token: str
    institution_id: str | None = None
    institution_name: str | None = None
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    def to_record(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "institution_id": self.institution_id,
            "institution_name": self.institution_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass(frozen=True)
class Account:
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
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    @classmethod
    def from_plaid_dict(cls, account: dict[str, Any], item_id: str) -> "Account":
        balances = account.get("balances", {}) or {}
        return cls(
            account_id=account["account_id"],
            item_id=item_id,
            name=account["name"],
            official_name=account.get("official_name"),
            mask=account.get("mask"),
            type=account.get("type"),
            subtype=account.get("subtype"),
            current_balance=balances.get("current"),
            available_balance=balances.get("available"),
            iso_currency_code=balances.get("iso_currency_code"),
            credit_limit=balances.get("limit"),
        )

    def to_record(self) -> dict[str, Any]:
        return {
            "account_id": self.account_id,
            "item_id": self.item_id,
            "name": self.name,
            "official_name": self.official_name,
            "mask": self.mask,
            "type": self.type,
            "subtype": self.subtype,
            "current_balance": self.current_balance,
            "available_balance": self.available_balance,
            "iso_currency_code": self.iso_currency_code,
            "credit_limit": self.credit_limit,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
