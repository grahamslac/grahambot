import aiosqlite
from analytics.metrics import calculate_metrics
from analytics.risk import assess_risk
from analytics.scoring import calculate_score
from reports import format_report
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import BOT_TOKEN, ALLOWED_USER_ID, DB_PATH, OPENAI_API_KEY, MOBULA_API_KEY


def restricted(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.effective_user or update.effective_user.id != ALLOWED_USER_ID:
            if update.message:
                await update.message.reply_text("⛔ Acceso denegado. Este bot es privado.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


@restricted
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 CryptoGraham activo. Usa /help para ver los comandos.")


@restricted
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📖 Comandos:
/start
/status
/watch TOKEN_ADDRESS
/unwatch TOKEN_ADDRESS
/analyze TOKEN_ADDRESS
/history TOKEN_ADDRESS")


@restricted
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            total = (await (await db.execute("SELECT COUNT(*) FROM tokens")).fetchone())[0]
            watched = (await (await db.execute("SELECT COUNT(*) FROM tokens WHERE is_watched=1")).fetchone())[0]
            rows = await (await db.execute("SELECT chain, COUNT(*) FROM tokens GROUP BY chain")).fetchall()
            system = await (await db.execute("SELECT last_scan, last_error FROM system_status WHERE id=1")).fetchone()
        chains = "\n".join(f"• {chain}: {count}" for chain, count in rows) or "• Ninguna"
        msg = f"🟢 Estado\n\nTokens: {total}\nWatchlist: {watched}\n\n{chains}\nÚltimo scan: {system[0] if system else 'UNKNOWN'}\nError: {system[1] if system and system[1] else 'Ninguno'}\nIA: {'disponible' if OPENAI_API_KEY else 'no configurada'}\nHolders: {'Mobula disponible' if MOBULA_API_KEY else 'no configurado'}"
        await update.message.reply_text(msg)
    except Exception as exc:
        await update.message.reply_text(f"⚠️ Error consultando estado: {exc}")


async def _set_watch(update, context, value):
    address = context.args[0] if context.args else None
    if not address:
        await update.message.reply_text("Uso: /watch TOKEN_ADDRESS")
        return
    async with aiosqlite.connect(DB_PATH) as db:
        result = await db.execute("UPDATE tokens SET is_watched=? WHERE token_address=?", (value, address))
        await db.commit()
    await update.message.reply_text("✅ Actualizado." if result.rowcount else "⚠️ Token no encontrado.")


@restricted
async def watch_cmd(update, context): await _set_watch(update, context, 1)
@restricted
async def unwatch_cmd(update, context): await _set_watch(update, context, 0)


@restricted
async def analyze_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = context.args[0] if context.args else None
    if not address:
        await update.message.reply_text("Uso: /analyze TOKEN_ADDRESS")
        return
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        token = await (await db.execute("SELECT * FROM tokens WHERE token_address=?", (address,))).fetchone()
        if not token:
            await update.message.reply_text("⚠️ Token no encontrado.")
            return
        snapshots = await (await db.execute("SELECT * FROM market_snapshots WHERE token_id=? ORDER BY captured_at", (token["id"],))).fetchall()
        holder = await (await db.execute("SELECT * FROM holder_snapshots WHERE token_id=? ORDER BY captured_at DESC LIMIT 1", (token["id"],))).fetchone()
    snap = {k: snapshots[-1][k] for k in snapshots[-1].keys()} if snapshots else {}
    holder_data = {k: holder[k] for k in holder.keys()} if holder else None
    if holder_data:
        snap.update({k: holder_data.get(k) for k in ("top_10_percent", "creator_percent")})
    metrics = calculate_metrics([r["price_usd"] for r in snapshots], [r["volume_24h_usd"] for r in snapshots], [r["liquidity_usd"] for r in snapshots])
    risk = assess_risk(snap, metrics)
    score = calculate_score(snap, metrics, risk)
    await update.message.reply_text(format_report(dict(token), snap, metrics, risk, score, holder=holder_data), parse_mode="Markdown")


@restricted
async def history_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = context.args[0] if context.args else None
    if not address:
        await update.message.reply_text("Uso: /history TOKEN_ADDRESS")
        return
    async with aiosqlite.connect(DB_PATH) as db:
        row = await (await db.execute("SELECT COUNT(*), MIN(captured_at), MAX(captured_at) FROM market_snapshots WHERE token_id=(SELECT id FROM tokens WHERE token_address=?)", (address,))).fetchone()
    await update.message.reply_text(f"📚 Snapshots: {row[0]}\nDesde: {row[1] or 'UNKNOWN'}\nHasta: {row[2] or 'UNKNOWN'}")


def get_application():
    app = Application.builder().token(BOT_TOKEN).build()
    for name, handler in (("start", start_cmd), ("help", help_cmd), ("status", status_cmd), ("watch", watch_cmd), ("unwatch", unwatch_cmd), ("analyze", analyze_cmd), ("report", analyze_cmd), ("risk", analyze_cmd), ("score", analyze_cmd), ("history", history_cmd)):
        app.add_handler(CommandHandler(name, handler))
    return app
