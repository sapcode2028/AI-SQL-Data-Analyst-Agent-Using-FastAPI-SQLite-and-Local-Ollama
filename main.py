from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from agent import ask_agent, explain_sql
from db import SCHEMA, add_sample_sale, get_stats, reset_db

app = FastAPI(title="SQL Data Analyst Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent


class Question(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


class SqlPayload(BaseModel):
    sql: str = Field(..., min_length=1, max_length=4000)


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/schema")
def get_schema():
    return {"schema": SCHEMA}


@app.get("/stats")
def stats():
    try:
        return get_stats()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/ask")
def ask(q: Question):
    try:
        return ask_agent(q.text.strip())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/explain-sql")
def explain(payload: SqlPayload):
    try:
        return {"explanation": explain_sql(payload.sql.strip())}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/seed-sale")
def seed_sale():
    try:
        return add_sample_sale()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/reset-db")
def reset_database():
    try:
        return reset_db()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))