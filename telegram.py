import asyncio
import os
import httpx
from links import coin_url, SIGNUP_URL

TG_TOKEN = os.environ["TG_TOKEN"]
OWNER = int(os.environ["OWNER_CHAT_ID"])
BASE = f"https://api.telegram.org/bot{TG_TOKEN}"

async def send_push(text: str, mint: str = None):
    buttons = None
    if mint:
        buttons = [[{"text": "Buy on FOMO", "url": coin_url(mint)}]]
    payload = {"chat_id": OWNER, "text": text}
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE}/sendMessage", json=payload)
        print("TG send:", r.status_code, text[:40])
        return r.json()

async def handle_command(text: str):
    t = text.strip().lower()
    print("TG cmd:", t)
    if t in ("/start", "start"):
        return "Owner locked. Desk is live."
    if t in ("/status", "status"):
        return "Mode: PAPER\nBalance: $200.00\nAgents: running"
    if t in ("/invite", "invite"):
        return SIGNUP_URL
    if t.startswith("/buy") or t.startswith("buy"):
        return "Send a mint address after buy"
    return "Commands: /status /invite /buy"

async def poll_loop():
    print("Telegram poller started")
    offset = 0
    while True:
        try:
            async with httpx.AsyncClient(timeout=35) as client:
                r = await client.get(f"{BASE}/getUpdates", params={"offset": offset, "timeout": 30})
                data = r.json()
                for u in data.get("result", []):
                    offset = u["update_id"] + 1
                    msg = u.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    if chat_id != OWNER:
                        continue
                    reply = await handle_command(msg.get("text", ""))
                    await send_push(reply)
        except Exception as e:
            print("TG poll error:", e)
            await asyncio.sleep(5)

