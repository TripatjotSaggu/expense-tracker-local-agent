# Local Finance Agent

A local-only starter project for analyzing bank and credit card transactions with a locally hosted MLX model.

## What it does

- Loads transactions from a CSV file
- Computes monthly spend, income, savings, top merchants, and category totals in code
- Sends the computed summary to your local MLX model on `localhost`
- Prints a finance summary with recommendations
- Treats savings transfers separately from true spending

## Project layout

- `sample_data/transactions.csv`: sample input data
- `src/finance_agent/`: app source code

## Current architecture

- `CLI`: current local CSV workflow
- `FastAPI backend`: new local API layer for Plaid integration
- `Plaid routes`: starter endpoints for Link token creation and token exchange
- `Local MLX model`: stays on `localhost` for summaries and recommendations

## Prerequisites

- Python 3.14 installed
- Your local MLX server running with:

```bash
source ~/mlx314/bin/activate
python -m mlx_lm server --model "mlx-community/Qwen3.5-9B-OptiQ-4bit"
```

By default this project expects the server at `http://127.0.0.1:8080/v1`.

For Plaid-based development, copy `.env.example` to `.env` and fill in your credentials.

## Setup

```bash
cd "/Users/tripatjotsaggu/Documents/Codex/Expense Tracker/finance-agent-local"
/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

## Run with sample data

```bash
source .venv/bin/activate
python -m finance_agent.cli summarize sample_data/transactions.csv
```

You can also use the installed console command:

```bash
finance-agent summarize sample_data/transactions.csv
```

## Run the local API backend

```bash
source .venv/bin/activate
finance-agent-api
```

The API will start on `http://127.0.0.1:8000` with:

- `GET /health`
- `POST /api/plaid/link-token/create`
- `POST /api/plaid/exchange-public-token`

If your bank export uses different column names, map them at the CLI:

```bash
finance-agent summarize ~/Downloads/bank.csv \
  --date-column "Transaction Date" \
  --merchant-column "Description" \
  --amount-column "Amount" \
  --default-account "Chase Checking"
```

## Expected CSV columns

The importer expects these columns:

- `date`
- `account`
- `merchant`
- `category`
- `amount`

Conventions:

- Expenses should be negative numbers
- Income should be positive numbers
- Internal savings or transfer rows can stay negative, but should use categories like `Savings` or `Transfer`

If your export does not include `account` or `category`, the CLI can fill them with defaults.

## Notes

- All calculations are done in Python, not by the LLM
- The LLM is used for explanation, recommendations, and narrative summary
- Keep your CSV files local if you want a fully local workflow
- The sample analytics treats `Savings` transfers separately so they do not inflate spending
- Plaid data retrieval is handled by the local FastAPI backend, while LLM inference stays local
