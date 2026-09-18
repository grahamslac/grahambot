import asyncio
import logging
from bot_telegram.bot import get_application
from scanner import scanner_loop
from data.database import init_db, set_status
logging.basicConfig(level=logging.INFO)
async def main_async():
    await init_db()
    app = get_application()
    await app.initialize(); await app.start(); await app.updater.start_polling()
    stop_signal = asyncio.Event(); task = asyncio.create_task(scanner_loop(stop_signal))
    try: await stop_signal.wait()
    finally:
        stop_signal.set(); await task
        await app.updater.stop(); await app.stop(); await app.shutdown()
        await set_status(status="STOPPED", scanner_running=0)
def main():
    try: asyncio.run(main_async())
    except (KeyboardInterrupt, SystemExit): logging.info("Bot detenido")
if __name__ == "__main__": main()
