# agents/scanner.py
import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import httpx
import websockets

from bus import bus
from db import connect
from fields import map_pumpportal, map_dex
from config import settings

log = logging.getLogger("scanner")
logging.basicConfig(filename="logs/scanner.log", level=logging.INFO)

class Scanner:
    def __init__(self):
        self.waiting = {}  # mint -> data
        self.seen_today = set()

    async def run(self):
        while True:
            try:
                await self._listen()
            except Exception as e:
                log.error(f"ws error: {e}")
                await asyncio.sleep(5)

    async def _listen(self):
        uri = "wss://pumpportal.fun/api/data"
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({"method": "subscribeMigration"}))
            while True:
                msg = json.loads(await ws.recv())
                mapped = map_pumpportal(msg)
                mint = mapped.get("mint")
                if not mint or mint in self.seen_today:
                    continue
                self.waiting[mint] = {
                    "mint": mint,
                    "name": None,
                    "symbol": None,
                    "pool": mapped.get("pool"),
                    "migrated_at": datetime.now(timezone.utc).isoformat(),
                    "creator": mapped.get("creator"),
                }
                self.seen_today.add(mint)
                log.info(f"new migration {mint}")

    async def poll_loop(self):
        while True:
            await asyncio.sleep(settings.get("scanner.poll_s", 60))
            if not self.waiting:
                continue
            mints = list(self.waiting.keys())
            # batch DexScreener
            async with httpx.AsyncClient() as client:
                for i in range(0, len(mints), 30):
                    batch = mints[i:i+30]
                    url = "https://api.dexscreener.com/tokens/v1/solana/" + ",".join(batch)
                    try:
                        r = await client.get(url, timeout=10)
                        if r.status_code == 429:
                            await asyncio.sleep(30)
                            continue
                        pairs = r.json()
                        for p in pairs if isinstance(pairs, list) else []:
                            d = map_dex(p)
                            mint = d.get("pairAddress") and p.get("baseToken", {}).get("address")
                            if mint in self.waiting:
                                await self._evaluate(mint, d)
                    except Exception as e:
                        log.error(f"dex error: {e}")

    async def _evaluate(self, mint, dex):
        w = self.waiting[mint]
        liq = dex.get("liquidityUsd") or 0
        h1 = (dex.get("priceChange") or {}).get("h1") or 0
        # top10 would need RPC; simplified for skeleton
        top10 = 0
        age_min = 15  # placeholder
        reason = None
        verdict = "pass"
        if liq < settings.get("scanner.min_liquidity_usd", 40000):
            verdict, reason = "kill", f"liq ${liq/1000:.1f}K"
        elif top10 > settings.get("scanner.max_top10_pct", 25):
            verdict, reason = "kill", f"top 10 hold {top10}%"
        elif h1 > settings.get("scanner.max_h1_change_pct", 80):
            verdict, reason = "kill", f"+{h1}% in 1h"
        # copycat check omitted for skeleton
        out = {
            "agent": "scanner",
            "mint": mint,
            "name": dex.get("name") or w.get("name"),
            "symbol": dex.get("symbol"),
            "pool": dex.get("pairAddress") or w.get("pool"),
            "liquidityUsd": liq,
            "top10Pct": top10,
            "h1ChangePct": h1,
            "ageMin": age_min,
            "verdict": verdict,
            "reason": reason,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        # write db.scans
        conn = connect()
        conn.execute(
            "INSERT INTO scans (mint, ts, liquidity_usd, top10_pct, h1_change_pct, age_min, verdict, reason) VALUES (?,?,?,?,?,?,?,?)",
            (mint, out["ts"], liq, top10, h1, age_min, verdict, reason)
        )
        conn.commit()
        conn.close()
        log.info(f"{out['ts']} {mint} {verdict} {reason}")
        if verdict == "pass":
            await bus.scanner_to_auditor.put(out)
            del self.waiting[mint]
        # drop after max_wait handled elsewhere
