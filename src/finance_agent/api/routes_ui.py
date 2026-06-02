from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["ui"])


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Expense Tracker Local Agent</title>
    <script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
    <style>
      :root {
        color-scheme: light;
        --bg: #f5f1e8;
        --panel: #fffdf8;
        --ink: #1c1b19;
        --muted: #6b655c;
        --accent: #0f766e;
        --accent-dark: #115e59;
        --border: #ded7cc;
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        min-height: 100vh;
        font-family: "Avenir Next", "Segoe UI", sans-serif;
        background:
          radial-gradient(circle at top left, #efe5cf, transparent 32%),
          radial-gradient(circle at bottom right, #d9efe9, transparent 30%),
          var(--bg);
        color: var(--ink);
      }

      main {
        max-width: 960px;
        margin: 0 auto;
        padding: 48px 20px 72px;
      }

      h1 {
        margin: 0 0 12px;
        font-size: clamp(2rem, 5vw, 4rem);
        line-height: 0.95;
      }

      p.lead {
        max-width: 700px;
        margin: 0 0 28px;
        font-size: 1.05rem;
        color: var(--muted);
      }

      .card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 10px 40px rgba(28, 27, 25, 0.06);
      }

      .grid {
        display: grid;
        gap: 20px;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        margin-top: 24px;
      }

      label {
        display: block;
        font-size: 0.92rem;
        font-weight: 600;
        margin-bottom: 8px;
      }

      input {
        width: 100%;
        padding: 12px 14px;
        border-radius: 12px;
        border: 1px solid var(--border);
        font: inherit;
        background: white;
      }

      button {
        margin-top: 16px;
        border: 0;
        border-radius: 999px;
        background: var(--accent);
        color: white;
        padding: 12px 18px;
        font: inherit;
        font-weight: 700;
        cursor: pointer;
      }

      button:hover {
        background: var(--accent-dark);
      }

      button.secondary {
        background: transparent;
        color: var(--ink);
        border: 1px solid var(--border);
      }

      pre {
        white-space: pre-wrap;
        word-break: break-word;
        background: #f7f4ee;
        border-radius: 16px;
        padding: 16px;
        border: 1px solid var(--border);
        min-height: 100px;
        margin: 0;
        font-size: 0.92rem;
      }

      .row {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
      }

      .muted {
        color: var(--muted);
        font-size: 0.92rem;
      }
    </style>
  </head>
  <body>
    <main>
      <h1>Connect your accounts locally</h1>
      <p class="lead">
        This page runs against your local FastAPI backend. Plaid handles the bank connection, your app stores metadata locally,
        and your LLM work stays on your Mac.
      </p>

      <section class="card">
        <label for="client-user-id">Client user ID</label>
        <input id="client-user-id" value="tripat-local-user" />
        <div class="row">
          <button id="connect-btn">Connect with Plaid</button>
          <button id="refresh-btn" class="secondary" type="button">Refresh linked accounts</button>
        </div>
        <p class="muted">
          After successful linking, this page will exchange the returned public token with your local backend automatically.
        </p>
      </section>

      <section class="grid">
        <article class="card">
          <h2>Latest action</h2>
          <pre id="action-output">No action yet.</pre>
        </article>
        <article class="card">
          <h2>Linked Plaid items</h2>
          <pre id="items-output">No items loaded yet.</pre>
        </article>
        <article class="card">
          <h2>Linked accounts</h2>
          <pre id="accounts-output">No accounts loaded yet.</pre>
        </article>
      </section>
    </main>

    <script>
      const actionOutput = document.getElementById("action-output");
      const itemsOutput = document.getElementById("items-output");
      const accountsOutput = document.getElementById("accounts-output");
      const connectBtn = document.getElementById("connect-btn");
      const refreshBtn = document.getElementById("refresh-btn");
      const clientUserIdInput = document.getElementById("client-user-id");

      function showJson(element, value) {
        element.textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
      }

      async function fetchJson(url, options = {}) {
        const response = await fetch(url, options);
        const data = await response.json();
        if (!response.ok) {
          throw new Error(typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail || data));
        }
        return data;
      }

      async function refreshLinkedData() {
        try {
          const [items, accounts] = await Promise.all([
            fetchJson("/api/plaid/items"),
            fetchJson("/api/plaid/accounts"),
          ]);
          showJson(itemsOutput, items.length ? items : "No linked items yet.");
          showJson(accountsOutput, accounts.length ? accounts : "No linked accounts yet.");
        } catch (error) {
          showJson(actionOutput, `Refresh failed: ${error.message}`);
        }
      }

      async function startPlaidLink() {
        connectBtn.disabled = true;
        showJson(actionOutput, "Requesting link token...");

        try {
          const tokenResponse = await fetchJson("/api/plaid/link-token/create", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
              client_user_id: clientUserIdInput.value.trim() || "tripat-local-user",
            }),
          });

          const handler = Plaid.create({
            token: tokenResponse.link_token,
            onSuccess: async function(public_token, metadata) {
              showJson(actionOutput, {
                message: "Plaid returned a public token. Exchanging with local backend...",
                metadata,
              });

              try {
                const exchangeResponse = await fetchJson("/api/plaid/exchange-public-token", {
                  method: "POST",
                  headers: {"Content-Type": "application/json"},
                  body: JSON.stringify({public_token}),
                });
                showJson(actionOutput, {
                  message: "Account link completed and stored locally.",
                  exchange: exchangeResponse,
                  metadata,
                });
                await refreshLinkedData();
              } catch (error) {
                showJson(actionOutput, `Public token exchange failed: ${error.message}`);
              }
            },
            onExit: function(err, metadata) {
              if (err) {
                showJson(actionOutput, {
                  message: "Plaid Link exited with an error.",
                  error: err,
                  metadata,
                });
              } else {
                showJson(actionOutput, {
                  message: "Plaid Link exited before completion.",
                  metadata,
                });
              }
              connectBtn.disabled = false;
            },
          });

          handler.open();
        } catch (error) {
          showJson(actionOutput, `Link token request failed: ${error.message}`);
          connectBtn.disabled = false;
        }
      }

      connectBtn.addEventListener("click", startPlaidLink);
      refreshBtn.addEventListener("click", refreshLinkedData);
      refreshLinkedData();
    </script>
  </body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
def root() -> str:
    return HTML_PAGE
