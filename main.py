import asyncio
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from db import init
from config import settings
from agents.scanner import Scanner
from agents.auditor import Auditor
from agents.analyst import Analyst
from agents.executor import Executor
from agents.risk import Risk
from telegram import poll_loop

app = FastAPI()
app.mount("/", StaticFiles(directory="web", html=True), name="web")

async def desk():
    init()
    print("=== Grok Bot Desk starting ===")
    print(f"Mode: {settings.get('desk.mode')}")
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
    uvicorn.run(app, host="0.0.0.0", port=port)
