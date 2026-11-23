import os
import re
from openai import OpenAI
from db import SCHEMA, init_db, run_query
from sql_guard import check_sql

client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1/"),
    api_key="ollama",
)
MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")


def _clean_sql(raw: str) -> str:
    text = (raw or "").strip()
    text = re.sub(r"^```(?:sql|sqlite)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\b(SELECT|WITH)\b[\s\S]*", text, flags=re.IGNORECASE)
    if match:
        text = match.group(0).strip()
    return text.rstrip(";").strip()


def _generate_sql(question: str, error_feedback: str | None = None) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a SQLite SQL generator. Write ONLY a single valid SQLite SELECT query "
                "for the schema below. Do not include markdown fences, comments, or explanations.\n"
                f"{SCHEMA}"
            ),
        },
        {"role": "user", "content": question},
    ]

    if error_feedback:
        messages.append(
            {
                "role": "user",
                "content": (
                    f"Your previous SQL failed with this error:\n{error_feedback}\n"
                    "Fix it and output ONLY the corrected SQLite SELECT query."
                ),
            }
        )

    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=messages,
    )
    return _clean_sql(resp.choices[0].message.content or "")


def ask_agent(question: str) -> dict:
    init_db()

    last_error: Exception | None = None
    safe_sql = ""
    rows: list[dict] = []

    for attempt in range(2):
        feedback = str(last_error) if attempt == 1 and last_error else None
        raw_sql = _generate_sql(question, error_feedback=feedback)
        try:
            safe_sql = check_sql(raw_sql)
            rows = run_query(safe_sql)
            last_error = None
            break
        except Exception as exc:
            last_error = exc

    if last_error is not None:
        raise RuntimeError(f"Could not run a valid SQL query: {last_error}")

    ans_resp = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer the user's question clearly and concisely using ONLY the provided "
                    "SQL query rows. Format currency values nicely when relevant."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {question}\nSQL: {safe_sql}\nRows: {rows}",
            },
        ],
    )

    return {
        "sql": safe_sql,
        "rows": rows,
        "answer": (ans_resp.choices[0].message.content or "").strip(),
    }


def explain_sql(sql: str) -> str:
    safe_sql = check_sql(sql)
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "Explain this SQLite SELECT query briefly in 2-3 clear bullet points "
                    "for a data analyst. Mention tables joined, filters, groupings, or ordering."
                ),
            },
            {"role": "user", "content": safe_sql},
        ],
    )
    return (resp.choices[0].message.content or "").strip()