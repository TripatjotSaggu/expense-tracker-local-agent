from __future__ import annotations

import sqlite3

from finance_agent.config import get_settings
from finance_agent.storage.keychain import TOKEN_PLACEHOLDER, store_access_token


def get_connection() -> sqlite3.Connection:
    settings = get_settings()
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS plaid_items (
                item_id TEXT PRIMARY KEY,
                access_token TEXT NOT NULL,
                token_storage_key TEXT,
                institution_id TEXT,
                institution_name TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                item_id TEXT NOT NULL,
                name TEXT NOT NULL,
                official_name TEXT,
                mask TEXT,
                type TEXT,
                subtype TEXT,
                current_balance REAL,
                available_balance REAL,
                iso_currency_code TEXT,
                credit_limit REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (item_id) REFERENCES plaid_items(item_id)
            );
            """
        )
        _migrate_plaid_items_table(connection)


def _migrate_plaid_items_table(connection: sqlite3.Connection) -> None:
    columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(plaid_items)").fetchall()
    }
    if "token_storage_key" not in columns:
        connection.execute("ALTER TABLE plaid_items ADD COLUMN token_storage_key TEXT")

    rows = connection.execute(
        """
        SELECT item_id, access_token, token_storage_key
        FROM plaid_items
        """
    ).fetchall()
    for row in rows:
        item_id = row["item_id"]
        access_token = row["access_token"]
        token_storage_key = row["token_storage_key"]
        if access_token and access_token != TOKEN_PLACEHOLDER and not token_storage_key:
            stored_key = store_access_token(item_id, access_token)
            connection.execute(
                """
                UPDATE plaid_items
                SET access_token = ?, token_storage_key = ?
                WHERE item_id = ?
                """,
                (TOKEN_PLACEHOLDER, stored_key, item_id),
            )
