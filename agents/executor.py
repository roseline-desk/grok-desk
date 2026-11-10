# agents/executor.py
import asyncio
import logging
from datetime import datetime, timezone

from bus import bus
from db import connect
from links import coin_url
from config import settings
from fees import fomo_fee

log = logging.getLogger("executor")
logging.basicConfig(filename="logs/executor.log", level=logging.INFO)

class Executor:
    async def run(self):
        while True:
            analyst = await bus.analyst_to_executor.get()
            await self.size_and_push(analyst)

    async def size_and_push(self, analyst):
        mint = analyst["mint"]
        stack = settings.get("desk.paper_start_stack", 200)  # or live stack
        size = stack * (settings.get("executor.stack_pct", 8) / 100)
        # caps, below_min, recheck omitted in skeleton
        if size < settings.get("executor.min_ticket_usd", 47.50):
            if settings.get("executor.below_min") == "bump":
                size = 47.50
            else:
                return  # skip
        link = coin_url(mint, "solana")
        mode = settings.get("desk.mode", "PAPER")
        signal_price = 0.001  # from fresh dex
        out = {
            "agent": "executor",
            "mint": mint,
            "signalPrice": signal_price,
            "sizeUsd": size,
            "stackPct": settings.get("executor.stack_pct", 8),
            "link": link,
            "mode": mode,
            "status": "sent",
            "reason": None,
        }
        # PAPER fill immediately
        conn = connect()
        conn.execute(
            "INSERT INTO signals (mint, ts, price, size_usd, stack_pct, link, mode, status) VALUES (?,?,?,?,?,?,?,?)",
            (mint, datetime.now(timezone.utc).isoformat(), signal_price, size, out["stackPct"], link, mode, "sent")
        )
        # activity Bought
        conn.execute(
            "INSERT INTO activity (ts, kind, mint, agent, title, subtitle, value) VALUES (?,?,?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(), "bought", mint, "executor",
             f"Bought {mint[:6]}", "Executor · now", f"${size:.2f} · {out['stackPct']}%")
        )
        conn.commit()
        conn.close()
        log.info(f"{mint} size={size} link={link}")
        await bus.executor_to_risk.put(out)
        # real: send Telegram push with buttons
