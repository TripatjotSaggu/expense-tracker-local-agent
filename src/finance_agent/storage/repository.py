from __future__ import annotations

from datetime import UTC, datetime

from finance_agent.storage.db import get_connection
from finance_agent.storage.models import Account, PlaidItem


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


class PlaidRepository:
    def upsert_item(self, item: PlaidItem) -> None:
        now = _now_iso()
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO plaid_items (
                    item_id, access_token, institution_id, institution_name, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(item_id) DO UPDATE SET
                    access_token = excluded.access_token,
                    institution_id = excluded.institution_id,
                    institution_name = excluded.institution_name,
                    updated_at = excluded.updated_at
                """,
                (
                    item.item_id,
                    item.access_token,
                    item.institution_id,
                    item.institution_name,
                    item.created_at,
                    now,
                ),
            )

    def upsert_accounts(self, accounts: list[Account]) -> None:
        if not accounts:
            return

        with get_connection() as connection:
            connection.executemany(
                """
                INSERT INTO accounts (
                    account_id, item_id, name, official_name, mask, type, subtype,
                    current_balance, available_balance, iso_currency_code, credit_limit,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(account_id) DO UPDATE SET
                    item_id = excluded.item_id,
                    name = excluded.name,
                    official_name = excluded.official_name,
                    mask = excluded.mask,
                    type = excluded.type,
                    subtype = excluded.subtype,
                    current_balance = excluded.current_balance,
                    available_balance = excluded.available_balance,
                    iso_currency_code = excluded.iso_currency_code,
                    credit_limit = excluded.credit_limit,
                    updated_at = excluded.updated_at
                """,
                [
                    (
                        account.account_id,
                        account.item_id,
                        account.name,
                        account.official_name,
                        account.mask,
                        account.type,
                        account.subtype,
                        account.current_balance,
                        account.available_balance,
                        account.iso_currency_code,
                        account.credit_limit,
                        account.created_at,
                        _now_iso(),
                    )
                    for account in accounts
                ],
            )

    def list_items(self) -> list[PlaidItem]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT item_id, access_token, institution_id, institution_name, created_at, updated_at
                FROM plaid_items
                ORDER BY created_at DESC
                """
            ).fetchall()
        return [PlaidItem(**dict(row)) for row in rows]

    def list_accounts(self) -> list[Account]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT account_id, item_id, name, official_name, mask, type, subtype,
                       current_balance, available_balance, iso_currency_code, credit_limit,
                       created_at, updated_at
                FROM accounts
                ORDER BY created_at DESC, name ASC
                """
            ).fetchall()
        return [Account(**dict(row)) for row in rows]
