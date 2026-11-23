# AI SQL Data Analyst Agent

A local, zero-cost full-stack **AI SQL Data Analyst Agent** that translates natural-language questions into validated read-only SQLite queries and plain-language summaries using **FastAPI**, **SQLite**, **`sqlglot`**, and a locally hosted **Ollama** model (`qwen2.5-coder:3b`).

## Features

- **100% Local & Free Inference:** Connects the OpenAI Python SDK to Ollama's local OpenAI-compatible server (`http://localhost:11434/v1/`)—no paid API keys or cloud billing required.
- **AST-Level SQL Guardrails (`sql_guard.py`):** Uses `sqlglot` to parse SQLite queries, enforce single-statement execution, allow only read-only `SELECT` / `UNION` / `WITH` queries, block mutating/DDL statements (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`), and restrict table access to `products` and `sales`.
- **Automatic SQL Retry & Self-Correction (`agent.py`):** Cleans markdown fences or extra prose from model output and automatically retries once with error feedback if SQL validation or SQLite execution fails.
- **Plain-Language SQL Explainer:** Includes a `POST /explain-sql` endpoint and **Explain SQL** button in the UI to break down generated queries.
- **Interactive Web Workbench (`index.html`):**
  - Natural-language query input with `Ctrl + Enter` / `Cmd + Enter` shortcut
  - One-click sample question chips and recent query history
  - Natural-language summary card, copyable SQL block, and formatted result table
  - Automatic horizontal bar chart for eligible two-column (label + non-negative numeric) result sets
  - One-click **Download CSV** export (`query_results.csv`)
  - Live database row counts (`GET /stats`), collapsible schema viewer (`GET /schema`), **+ Add Sample Sale** (`POST /seed-sale`), and **Reset Data** (`POST /reset-db`)

## Tech Stack

- **Backend:** FastAPI, Uvicorn, Pydantic, `python-dotenv`
- **Database:** SQLite (`agent.db`)
- **SQL Parsing & Validation:** `sqlglot`
- **LLM Runtime & Client:** Ollama (`qwen2.5-coder:3b`), `openai` Python SDK
- **Frontend:** Single-file HTML5, CSS3, and vanilla JavaScript (`index.html`)

## Project Structure

```text
sql-agent/
├── .env              # Local Ollama endpoint, model, and SQLite path config
├── requirements.txt  # Python dependencies
├── db.py             # SQLite schema, seeding, query execution, stats & reset helpers
├── sql_guard.py      # sqlglot read-only & table-allowlist validator
├── agent.py          # SQL generation, self-correction retry, summarization & SQL explainer
├── main.py           # FastAPI routes and static frontend entrypoint
└── index.html        # Web workbench UI
