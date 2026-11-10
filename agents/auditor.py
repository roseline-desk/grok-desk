# agents/auditor.py
import asyncio
import logging
from datetime import datetime, timezone

import httpx

from bus import bus
from db import connect
from fields import map_rugcheck_report

log = logging.getLogger("auditor")
logging.basicConfig(filename="logs/auditor.log", level=logging.INFO)

class Auditor:
    async def run(self):
        while True:
            scan = await bus.scanner_to_auditor.get()
            await self.audit(scan)

    async def audit(self, scan):
        mint = scan["mint"]
        layers = []
        passed = True
        reason = None
        # skeleton: real implementation calls RPC + RugCheck per layer
        # Layer 1-2: mint/freeze authority from getAccountInfo
        # Layer 3: dev balance
        # etc.
        # For proof we emit 8 layers
        for n, name in enumerate([
            "Mint authority", "Freeze authority", "Dev wallet", "Top 10 holders",
            "Liquidity", "Pool age", "Bundled wallets", "Delegations"
        ], 1):
            # placeholder values
            value = "Revoked" if n <= 2 else "ok"
            layer_pass = True
            layers.append({
                "n": n, "name": name, "pass": layer_pass,
                "value": value, "source": "rpc" if n <= 4 else "rugcheck"
            })
            # emit SSE-style (in real: api stream)
            if not layer_pass:
                passed = False
                reason = value
                break
        out = {
            "agent": "auditor",
            "mint": mint,
            "ts": datetime.now(timezone.utc).isoformat(),
            "passed": passed,
            "layersChecked": len(layers),
            "layers": layers,
            "holders": 100,
            "reason": reason,
        }
        # write audits
        conn = connect()
        for L in layers:
            conn.execute(
                "INSERT INTO audits (mint, ts, layer, name, value_text, pass, source) VALUES (?,?,?,?,?,?,?)",
                (mint, out["ts"], L["n"], L["name"], L["value"], int(L["pass"]), L["source"])
            )
        conn.commit()
        conn.close()
        log.info(f"{mint} passed={passed} reason={reason}")
        if passed:
            await bus.auditor_to_analyst.put(out)
        else:
            # activity reject
            pass
