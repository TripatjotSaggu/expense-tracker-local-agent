from __future__ import annotations

from pathlib import Path
from typing import Mapping

import pandas as pd


REQUIRED_COLUMNS = {"date", "account", "merchant", "category", "amount"}


def load_transactions(
    csv_path: str | Path,
    column_map: Mapping[str, str] | None = None,
    default_account: str = "Imported Account",
    default_category: str = "Uncategorized",
) -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    df = pd.read_csv(path)
    if column_map:
        renamed = {}
        for canonical_name, source_name in column_map.items():
            if source_name and source_name in df.columns:
                renamed[source_name] = canonical_name
        df = df.rename(columns=renamed)

    if "account" not in df.columns:
        df["account"] = default_account
    if "category" not in df.columns:
        df["category"] = default_category

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df["amount"] = pd.to_numeric(df["amount"], errors="raise")
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df.sort_values("date").reset_index(drop=True)
