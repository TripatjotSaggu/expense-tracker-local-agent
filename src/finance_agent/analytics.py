from __future__ import annotations

from typing import Any

import pandas as pd


NON_SPEND_CATEGORIES = {"Savings", "Transfer", "Transfers"}


def build_summary(df: pd.DataFrame) -> dict[str, Any]:
    outflows = df[df["amount"] < 0].copy()
    income = df[df["amount"] > 0].copy()
    savings_transfers = outflows[outflows["category"].isin(NON_SPEND_CATEGORIES)].copy()
    expenses = outflows[~outflows["category"].isin(NON_SPEND_CATEGORIES)].copy()

    total_spend = round(float(expenses["amount"].sum() * -1), 2)
    total_income = round(float(income["amount"].sum()), 2)
    total_saved = round(float(savings_transfers["amount"].sum() * -1), 2)
    net_after_spend = round(total_income - total_spend, 2)
    savings_rate = round((total_saved / total_income) * 100, 2) if total_income else 0.0

    monthly_spend = (
        expenses.groupby("month")["amount"].sum().abs().round(2).sort_index().to_dict()
    )
    monthly_income = (
        income.groupby("month")["amount"].sum().round(2).sort_index().to_dict()
    )
    monthly_saved = (
        savings_transfers.groupby("month")["amount"].sum().abs().round(2).sort_index().to_dict()
    )
    category_spend = (
        expenses.groupby("category")["amount"].sum().abs().round(2).sort_values(ascending=False).to_dict()
    )
    top_merchants = (
        expenses.groupby("merchant")["amount"].sum().abs().round(2).sort_values(ascending=False).head(10).to_dict()
    )

    recent_transactions = (
        df.sort_values("date", ascending=False)
        .head(15)[["date", "account", "merchant", "category", "amount"]]
        .assign(date=lambda frame: frame["date"].dt.strftime("%Y-%m-%d"))
        .to_dict(orient="records")
    )

    return {
        "date_range": {
            "start": df["date"].min().strftime("%Y-%m-%d"),
            "end": df["date"].max().strftime("%Y-%m-%d"),
        },
        "transaction_count": int(len(df)),
        "total_income": total_income,
        "total_spend": total_spend,
        "total_saved": total_saved,
        "net_after_spend": net_after_spend,
        "savings_rate_percent": savings_rate,
        "monthly_spend": monthly_spend,
        "monthly_income": monthly_income,
        "monthly_saved": monthly_saved,
        "category_spend": category_spend,
        "top_merchants": top_merchants,
        "recent_transactions": recent_transactions,
    }
