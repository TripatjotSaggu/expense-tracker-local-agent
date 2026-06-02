from __future__ import annotations

import platform
import subprocess


KEYCHAIN_SERVICE_NAME = "expense-tracker-local-agent.plaid"
TOKEN_PLACEHOLDER = "__STORED_IN_KEYCHAIN__"


def _ensure_macos() -> None:
    if platform.system() != "Darwin":
        raise RuntimeError("macOS Keychain storage is only supported on macOS.")


def store_access_token(item_id: str, access_token: str) -> str:
    _ensure_macos()
    subprocess.run(
        [
            "security",
            "add-generic-password",
            "-a",
            item_id,
            "-s",
            KEYCHAIN_SERVICE_NAME,
            "-w",
            access_token,
            "-U",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return item_id


def get_access_token(token_storage_key: str) -> str:
    _ensure_macos()
    result = subprocess.run(
        [
            "security",
            "find-generic-password",
            "-a",
            token_storage_key,
            "-s",
            KEYCHAIN_SERVICE_NAME,
            "-w",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()

