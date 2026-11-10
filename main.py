import asyncio
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from db import init, connect
from config import settings
from agents.scanner import Scanner
from agents.auditor import Auditor
from agents.analyst import Analyst
from agents.executor import Executor
from agents.risk import Risk
from telegram import poll_loop

app = FastAPI()

@app.get("/api/state")
async def api_state():
    conn = connect()
    act = conn.execute("SELECT COUNT(*) FROM activity").fetchone()[0]
    conn.close()
    return {
        "balance": 200.0,
        "today_pct": 0.0,
        "mode": "PAPER",
        "agents_running": 5,
        "activity_count": act,
    }

app.mount("/", StaticFiles(directory="web", html=True), name="web")

async def desk():
    init()
    print("=== Grok Bot Desk starting ===")
    scanner = Scanner()
    auditor = Auditor()
    analyst = Analyst()
    executor = Executor()
    risk = Risk()
    await asyncio.gather(
        scanner.run(),
        scanner.poll_loop(),
        auditor.run(),
        analyst.run(),
        executor.run(),
        risk.run(),
        poll_loop(),
    )

@app.on_event("startup")
async def startup():
    asyncio.create_task(desk())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
