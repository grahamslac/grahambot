import asyncio
import logging
import aiohttp
import aiosqlite
from config import DB_PATH, BOT_TOKEN, ALLOWED_USER_ID, SCAN_INTERVAL_SECONDS
from data.database import set_status

logger = logging.getLogger(__name__)
LATEST_PROFILES_URL = "https://api.dexscreener.com/token-profiles/latest/v1"

async def send_telegram_alert(session, message):
    if not BOT_TOKEN or not ALLOWED_USER_ID: return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        await session.post(url, json={"chat_id": ALLOWED_USER_ID, "text": message}, timeout=10)
    except Exception as exc: logger.warning("Telegram alert failed: %s", exc)

async def evaluate_and_store_tokens():
    async with aiohttp.ClientSession() as session:
        async with session.get(LATEST_PROFILES_URL, timeout=15) as response:
            if response.status != 200: return 0
            profiles = await response.json()
        inserted = 0
        async with aiosqlite.connect(DB_PATH) as db:
            for item in profiles if isinstance(profiles, list) else []:
                address = item.get("tokenAddress"); chain = (item.get("chainId") or "").lower()
                if not address: continue
                exists = await (await db.execute("SELECT id FROM tokens WHERE token_address=?", (address,))).fetchone()
                if not exists:
                    await db.execute("INSERT INTO tokens(token_address, symbol, chain, discovered_at, metadata_json) VALUES(?,?,?,datetime('now'),?)", (address, None, chain, str(item)))
                    inserted += 1
            await db.commit()
        return inserted

async def scanner_loop(stop_signal):
    await set_status(status="RUNNING", scanner_running=1)
    while not stop_signal.is_set():
        try: await evaluate_and_store_tokens()
        except Exception as exc: logger.exception("Scanner error: %s", exc)
        try: await asyncio.wait_for(stop_signal.wait(), timeout=SCAN_INTERVAL_SECONDS)
        except asyncio.TimeoutError: pass
