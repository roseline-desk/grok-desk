import asyncio
import json
import logging
import os
from datetime import datetime, timezone

import httpx

from links import coin_url, profile_url, SIGNUP_URL
from db import connect
from config import settings

log = logging.getLogger("telegram")
logging.basicConfig(filename="logs/telegram.log", level=logging.INFO)

TG_TOKEN = os.environ["TG_TOKEN"]
OWNER = int(os.environ["OWNER_CHAT_ID"])
BASE = f"https://api.telegram.org/bot{TG_TOKEN}"

async def send_push(text: str, mint: str = None, buttons=None):
    if not buttons and mint:
        buttons = [[{"text": "Buy on FOMO", "url": coin_url(mint)}]]
    payload = {
        "chat_id": OWNER,
        "text": text,
        "reply_markup": {"inline_keyboard": buttons} if buttons else None,
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE}/sendMessage", json=payload)
        log.info(f"push: {r.status_code} {text[:60]}")
        return r.json()

async def handle_command(text: str):
    text = text.strip().lower()
    if text.startswith("/start"):
        return "Owner locked. Desk ready."
    if text == "status":
        return f"Mode: PAPER · Balance: $200"
    if text == "invite":
        return SIGNUP_URL
    if text.startswith("buy "):
        mint = text.split()[-1]
        return f"Auditor run on {mint}\n{coin_url(mint)}"
    return "Commands: status, buy X, invite"

async def poll_loop():
    offset = 0
    while True:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{BASE}/getUpdates", params={"offset": offset, "timeout": 30})
                data = r.json()
                for u in data.get("result", []):
                    offset = u["update_id"] + 1
                    msg = u.get("message", {})
                    if msg.get("chat", {}).get("id") != OWNER:
                        continue
                    reply = await handle_command(msg.get("text", ""))
                    await send_push(reply)
        except Exception as e:
            log.error(f"poll error: {e}")
            await asyncio.sleep(5)
