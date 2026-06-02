from __future__ import annotations

from datetime import UTC, datetime

from finance_agent.storage.db import get_connection
from finance_agent.storage.keychain import (
    TOKEN_PLACEHOLDER,
    get_access_token,
    store_access_token,
)
from finance_agent.storage.models import Account, PlaidItem


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


class PlaidRepository:
    def upsert_item(self, item: PlaidItem) -> None:
        now = _now_iso()
        token_storage_key = store_access_token(item.item_id, item.access_token)
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO plaid_items (
                    item_id, access_token, token_storage_key, institution_id, institution_name, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(item_id) DO UPDATE SET
                    access_token = excluded.access_token,
                    token_storage_key = excluded.token_storage_key,
                    institution_id = excluded.institution_id,
                    institution_name = excluded.institution_name,
                    updated_at = excluded.updated_at
                """,
                (
                    item.item_id,
                    TOKEN_PLACEHOLDER,
                    token_storage_key,
                    item.institution_id,
                    item.institution_name,
                    item.created_at,
                    now,
                ),
            )

    def get_access_token(self, item_id: str) -> str:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT token_storage_key
                FROM plaid_items
                WHERE item_id = ?
                """,
                (item_id,),
            ).fetchone()
        if row is None or not row["token_storage_key"]:
            raise KeyError(f"No stored Plaid token found for item_id={item_id}")
        return get_access_token(row["token_storage_key"])

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
                SELECT item_id, access_token, token_storage_key, institution_id, institution_name, created_at, updated_at
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
