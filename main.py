# main.py — full desk start (Plan B)
import asyncio
import json
from pathlib import Path

from db import init
from config import Settings
from agents.scanner import Scanner
from agents.auditor import Auditor
from agents.analyst import Analyst
from agents.executor import Executor
from agents.risk import Risk
from telegram import poll_loop

SECRETS = json.loads(Path("os.environ").read_text())
DATA_PATH = SECRETS["DATA_PATH"]

async def main():
    init()
    settings = Settings(None)
    print(f"=== Grok Bot Desk starting ===")
    print(f"Mode: {settings.get('desk.mode')}")
    print(f"FOMO handle: {settings.get('desk.fomo_handle')}")
    print(f"DATA_PATH: {DATA_PATH}")
    print(f"JSON: web/d/{DATA_PATH}/")
    print(f"Telegram owner locked")

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
        # json writer can be added back here
    )

if __name__ == "__main__":
    asyncio.run(main())
