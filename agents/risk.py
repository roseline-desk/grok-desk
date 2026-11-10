# agents/risk.py
import asyncio
import logging
from datetime import datetime, timezone

from bus import bus
from db import connect
from links import coin_url
from config import settings

log = logging.getLogger("risk")
logging.basicConfig(filename="logs/risk.log", level=logging.INFO)

class Risk:
    async def run(self):
        while True:
            signal = await bus.executor_to_risk.get()
            await self.guard(signal)

    async def guard(self, signal):
        mint = signal["mint"]
        entry = signal["signalPrice"]
        size = signal["sizeUsd"]
        stop_pct = settings.get("risk.stop_pct", 6)
        # open position
        conn = connect()
        conn.execute(
            "INSERT INTO positions (mint, opened_at, entry_price, size_usd, peak_price, stop_price, trail_active, mode) VALUES (?,?,?,?,?,?,?,?)",
            (mint, datetime.now(timezone.utc).isoformat(), entry, size, entry, entry * (1 - stop_pct/100), 0, signal["mode"])
        )
        conn.commit()
        conn.close()
        # poll loop skeleton
        while True:
            await asyncio.sleep(settings.get("risk.poll_s", 15))
            # real: DexScreener poll, check stop/trail/timeout
            # for skeleton just log
            log.info(f"guarding {mint}")
            break  # remove in real
