# agents/analyst.py
import asyncio
import logging
from datetime import datetime, timezone

import httpx

from bus import bus
from db import connect
from config import settings

log = logging.getLogger("analyst")
logging.basicConfig(filename="logs/analyst.log", level=logging.INFO)

class Analyst:
    async def run(self):
        while True:
            audit = await bus.auditor_to_analyst.get()
            await self.score(audit)

    async def score(self, audit):
        mint = audit["mint"]
        mode = settings.get("analyst.mode", "jev")
        if mode == "jev":
            # real: POST to typesafe with state + 4 noul questions
            answers = {"alive_6h": 0.75, "organic": 0.70, "flush": 0.40, "chase": 0.25}
            model = "jev-latest"
            tokens = 400
        else:
            # rules mode
            answers = {"alive_6h": 0.8, "organic": 0.7, "flush": 0.5, "chase": 0.2}
            model = "rules"
            tokens = 0
        score = round(100 * (answers["alive_6h"] + answers["organic"] + answers["flush"] + (1 - answers["chase"])) / 4)
        passed = (
            answers["alive_6h"] >= settings.get("analyst.min_alive_6h", 0.70) and
            answers["organic"] >= settings.get("analyst.min_organic", 0.65) and
            answers["chase"] <= settings.get("analyst.max_chase", 0.30) and
            score >= settings.get("analyst.min_score", 70)
        )
        failed = []
        if not passed:
            failed.append("score")
        out = {
            "agent": "analyst",
            "mint": mint,
            "answers": answers,
            "score": score,
            "passed": passed,
            "failed": failed,
            "model": model,
            "inputTokens": tokens,
        }
        conn = connect()
        conn.execute(
            "INSERT INTO verdicts (mint, ts, alive_6h, organic, flush, chase, score, pass, reason, input_tokens) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (mint, datetime.now(timezone.utc).isoformat(), answers["alive_6h"], answers["organic"],
             answers["flush"], answers["chase"], score, int(passed), ",".join(failed), tokens)
        )
        conn.commit()
        conn.close()
        log.info(f"{mint} score={score} passed={passed}")
        if passed:
            await bus.analyst_to_executor.put(out)
