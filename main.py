import asyncio
import os
from db import init
from config import settings
from agents.scanner import Scanner
from agents.auditor import Auditor
from agents.analyst import Analyst
from agents.executor import Executor
from agents.risk import Risk
from telegram import poll_loop

async def main():
    init()
    print("=== Grok Bot Desk starting ===")
    print(f"Mode: {settings.get('desk.mode')}")
    print(f"FOMO handle: {os.environ.get('FOMO_HANDLE', 'skylinerya')}")
    print("Telegram owner locked")

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

if __name__ == "__main__":
    asyncio.run(main())
