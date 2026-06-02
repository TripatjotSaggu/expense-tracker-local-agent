from __future__ import annotations

import argparse
from pathlib import Path

from finance_agent.agent import summarize_finances
from finance_agent.analytics import build_summary
from finance_agent.data_loader import load_transactions


def summarize_command(args: argparse.Namespace) -> int:
    column_map = {
        "date": args.date_column,
        "merchant": args.merchant_column,
        "amount": args.amount_column,
        "account": args.account_column,
        "category": args.category_column,
    }
    df = load_transactions(
        args.csv_path,
        column_map=column_map,
        default_account=args.default_account,
        default_category=args.default_category,
    )
    summary = build_summary(df)

    print("Computed finance summary:")
    print(f"- Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
    print(f"- Transactions: {summary['transaction_count']}")
    print(f"- Total income: ${summary['total_income']:.2f}")
    print(f"- Total spend: ${summary['total_spend']:.2f}")
    print(f"- Total saved: ${summary['total_saved']:.2f}")
    print(f"- Net after spend: ${summary['net_after_spend']:.2f}")
    print(f"- Savings rate: {summary['savings_rate_percent']:.2f}%")
    print()
    print("Agent response:")
    print()
    print(summarize_finances(summary))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local finance agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summarize = subparsers.add_parser("summarize", help="Summarize a transaction CSV")
    summarize.add_argument(
        "csv_path",
        type=str,
        nargs="?",
        default=str(Path("sample_data") / "transactions.csv"),
        help="Path to the transaction CSV",
    )
    summarize.add_argument("--date-column", default="date", help="Source CSV column for dates")
    summarize.add_argument("--merchant-column", default="merchant", help="Source CSV column for merchant or description")
    summarize.add_argument("--amount-column", default="amount", help="Source CSV column for transaction amount")
    summarize.add_argument("--account-column", default="account", help="Source CSV column for account name")
    summarize.add_argument("--category-column", default="category", help="Source CSV column for category")
    summarize.add_argument(
        "--default-account",
        default="Imported Account",
        help="Fallback account name when the CSV has no account column",
    )
    summarize.add_argument(
        "--default-category",
        default="Uncategorized",
        help="Fallback category when the CSV has no category column",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "summarize":
        return summarize_command(args)

    parser.error(f"Unsupported command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
