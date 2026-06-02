from __future__ import annotations

import json

from finance_agent.config import get_settings
from finance_agent.llm_client import get_client


SYSTEM_PROMPT = """You are a careful personal finance assistant.
You help summarize spending, explain trends, point out risks, and suggest realistic savings ideas.
Use only the data provided.
Show your reasoning if it is available in your current response style, but do not invent transactions or numbers.
When giving savings advice, make it practical and specific.
Treat 'total_spend' as actual spending and 'total_saved' as money intentionally moved into savings."""



def summarize_finances(summary_payload: dict) -> str:
    settings = get_settings()
    client = get_client()

    user_prompt = f"""Here is a computed personal finance summary in JSON.

{json.dumps(summary_payload, indent=2)}

Please do all of the following:
1. Summarize the person's spending and income patterns.
2. Identify the biggest spending categories and merchants.
3. Comment on the savings rate and distinguish between spending and intentional savings transfers.
4. Provide 5 realistic recommendations to improve spending or savings.
5. Mention any unusual or notable patterns you see.
"""

    response = client.chat.completions.create(
        model=settings.model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""
