import asyncio
import os
import httpx
from links import coin_url, SIGNUP_URL

TG_TOKEN = os.environ["TG_TOKEN"]
OWNER = int(os.environ["OWNER_CHAT_ID"])
BASE = f"https://api.telegram.org/bot{TG_TOKEN}"

async def send_push(text: str, mint: str = None, extra_buttons=None):
    buttons = []
    if mint:
        buttons.append([{"text": "Buy on FOMO", "url": coin_url(mint)}])
    if extra_buttons:
        buttons.extend(extra_buttons)
    payload = {"chat_id": OWNER, "text": text}
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE}/sendMessage", json=payload)

async def handle_command(text: str):
    t = text.strip()
    low = t.lower()
    if low in ("/start", "start"):
        return "Owner locked. Desk is live in PAPER mode.", None
    if low in ("/status", "status"):
        return "Mode: PAPER\nBalance: $200.00\nAgents: 5 running\nScanner listening", None
    if low in ("/invite", "invite"):
        return SIGNUP_URL, None
    if low.startswith("/buy") or low.startswith("buy"):
        parts = t.split()
        if len(parts) < 2:
            return "Usage: /buy <mint address>", None
        mint = parts[1]
        return f"Running Auditor on {mint[:8]}…\n(Full 8-layer check coming)\nOpen on FOMO:", mint
    if low in ("/help", "help"):
        return "Commands:\n/status\n/invite\n/buy <mint>\n/help", None
    return "Unknown. Try /help", None

async def poll_loop():
    print("Telegram poller started")
    offset = 0
    while True:
        try:
            async with httpx.AsyncClient(timeout=40) as client:
                r = await client.get(f"{BASE}/getUpdates", params={"offset": offset, "timeout": 30})
                for u in r.json().get("result", []):
                    offset = u["update_id"] + 1
                    msg = u.get("message", {})
                    if msg.get("chat", {}).get("id") != OWNER:
                        continue
                    reply, mint = await handle_command(msg.get("text", ""))
                    await send_push(reply, mint)
        except Exception as e:
            print("TG error:", e)
            await asyncio.sleep(5)
