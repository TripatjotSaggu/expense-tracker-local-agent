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


def build_account_summary(accounts: list[dict[str, Any]], items: list[dict[str, Any]]) -> dict[str, Any]:
    credit_accounts = []
    depository_accounts = []

    item_name_by_id = {
        item["item_id"]: item.get("institution_name") or item.get("institution_id") or "Linked institution"
        for item in items
    }

    for account in accounts:
        record = {
            "account_id": account["account_id"],
            "item_id": account["item_id"],
            "institution_name": item_name_by_id.get(account["item_id"], "Linked institution"),
            "name": account["name"],
            "official_name": account.get("official_name"),
            "type": account.get("type"),
            "subtype": account.get("subtype"),
            "current_balance": account.get("current_balance"),
            "available_balance": account.get("available_balance"),
            "credit_limit": account.get("credit_limit"),
            "iso_currency_code": account.get("iso_currency_code"),
        }
        if account.get("type") == "credit":
            limit = account.get("credit_limit")
            balance = account.get("current_balance")
            utilization = None
            if limit and balance is not None:
                utilization = round((balance / limit) * 100, 2)
            record["utilization_percent"] = utilization
            credit_accounts.append(record)
        else:
            depository_accounts.append(record)

    total_credit_balance = round(
        sum(account.get("current_balance") or 0.0 for account in credit_accounts), 2
    )
    total_credit_limit = round(
        sum(account.get("credit_limit") or 0.0 for account in credit_accounts), 2
    )
    overall_credit_utilization = (
        round((total_credit_balance / total_credit_limit) * 100, 2)
        if total_credit_limit
        else None
    )
    total_depository_balance = round(
        sum(account.get("current_balance") or 0.0 for account in depository_accounts), 2
    )

    return {
        "linked_items_count": len(items),
        "linked_accounts_count": len(accounts),
        "credit_accounts_count": len(credit_accounts),
        "depository_accounts_count": len(depository_accounts),
        "total_credit_balance": total_credit_balance,
        "total_credit_limit": total_credit_limit,
        "overall_credit_utilization_percent": overall_credit_utilization,
        "total_depository_balance": total_depository_balance,
        "credit_accounts": credit_accounts,
        "depository_accounts": depository_accounts,
    }
