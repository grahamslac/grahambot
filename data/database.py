import logging
from pathlib import Path
import aiosqlite
from config import DB_PATH

logger = logging.getLogger(__name__)

async def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS tokens (id INTEGER PRIMARY KEY AUTOINCREMENT, token_address TEXT UNIQUE NOT NULL, symbol TEXT, name TEXT, chain TEXT NOT NULL, discovered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, creator_address TEXT, is_watched INTEGER NOT NULL DEFAULT 0, metadata_json TEXT);
        CREATE TABLE IF NOT EXISTS token_pairs (id INTEGER PRIMARY KEY AUTOINCREMENT, token_id INTEGER NOT NULL REFERENCES tokens(id), pair_address TEXT, dex_id TEXT, url TEXT, quote_symbol TEXT, UNIQUE(token_id, pair_address));
        CREATE TABLE IF NOT EXISTS market_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, token_id INTEGER NOT NULL REFERENCES tokens(id), captured_at TEXT NOT NULL, price_usd REAL, liquidity_usd REAL, volume_24h_usd REAL, market_cap_usd REAL, fdv_usd REAL, price_change_5m REAL, price_change_1h REAL, price_change_6h REAL, price_change_24h REAL, source TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS holder_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, token_id INTEGER NOT NULL REFERENCES tokens(id), captured_at TEXT NOT NULL, holder_count INTEGER, top_holder_percent REAL, top_10_percent REAL, creator_percent REAL, top_50_percent REAL, top_100_percent REAL, snipers_percent REAL, insiders_percent REAL, bundlers_percent REAL, dev_count INTEGER, sniper_count INTEGER, insider_count INTEGER, bundler_count INTEGER, active_wallets INTEGER, metadata_json TEXT, source TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS token_metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, token_id INTEGER NOT NULL REFERENCES tokens(id), calculated_at TEXT NOT NULL, metric_name TEXT NOT NULL, value REAL, methodology TEXT NOT NULL, confidence TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS risk_assessments (id INTEGER PRIMARY KEY AUTOINCREMENT, token_id INTEGER NOT NULL REFERENCES tokens(id), calculated_at TEXT NOT NULL, risk_score REAL, category TEXT NOT NULL, confidence TEXT NOT NULL, factors_json TEXT, missing_data_json TEXT);
        CREATE TABLE IF NOT EXISTS score_assessments (id INTEGER PRIMARY KEY AUTOINCREMENT, token_id INTEGER NOT NULL REFERENCES tokens(id), calculated_at TEXT NOT NULL, component TEXT NOT NULL, value REAL, weight REAL, contribution REAL, explanation TEXT, confidence TEXT);
        CREATE TABLE IF NOT EXISTS analysis_runs (id INTEGER PRIMARY KEY AUTOINCREMENT, token_id INTEGER NOT NULL REFERENCES tokens(id), analyzed_at TEXT NOT NULL, global_score REAL, confidence TEXT, report TEXT, ai_summary TEXT);
        CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY AUTOINCREMENT, token_id INTEGER NOT NULL REFERENCES tokens(id), created_at TEXT NOT NULL, alert_type TEXT NOT NULL, message TEXT NOT NULL, fingerprint TEXT UNIQUE);
        CREATE TABLE IF NOT EXISTS outcomes (id INTEGER PRIMARY KEY AUTOINCREMENT, token_id INTEGER NOT NULL REFERENCES tokens(id), analysis_run_id INTEGER REFERENCES analysis_runs(id), observed_at TEXT NOT NULL, horizon_hours INTEGER, return_percent REAL, max_drawdown_percent REAL);
        CREATE TABLE IF NOT EXISTS creator_profiles (id INTEGER PRIMARY KEY AUTOINCREMENT, token_id INTEGER NOT NULL REFERENCES tokens(id), creator_address TEXT, source TEXT, metadata_json TEXT, observed_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS wallet_events (id INTEGER PRIMARY KEY AUTOINCREMENT, token_id INTEGER NOT NULL REFERENCES tokens(id), wallet_address TEXT, event_type TEXT, amount REAL, observed_at TEXT NOT NULL, source TEXT);
        CREATE TABLE IF NOT EXISTS system_status (id INTEGER PRIMARY KEY CHECK (id = 1), status TEXT NOT NULL, last_scan TEXT, last_error TEXT, scanner_running INTEGER NOT NULL DEFAULT 0, ai_available INTEGER NOT NULL DEFAULT 0, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        INSERT OR IGNORE INTO system_status (id, status) VALUES (1, 'STARTING');
        CREATE INDEX IF NOT EXISTS idx_market_token_time ON market_snapshots(token_id, captured_at);
        CREATE INDEX IF NOT EXISTS idx_metrics_token_time ON token_metrics(token_id, calculated_at);
        """)
        cursor = await db.execute("PRAGMA table_info(tokens)")
        existing = {row[1] for row in await cursor.fetchall()}
        for column, statement in {"name":"ALTER TABLE tokens ADD COLUMN name TEXT", "creator_address":"ALTER TABLE tokens ADD COLUMN creator_address TEXT", "is_watched":"ALTER TABLE tokens ADD COLUMN is_watched INTEGER NOT NULL DEFAULT 0", "metadata_json":"ALTER TABLE tokens ADD COLUMN metadata_json TEXT"}.items():
            if column not in existing:
                await db.execute(statement)
        await db.commit()
    logger.info("Base de datos inicializada correctamente en %s", DB_PATH)

async def set_status(**fields):
    allowed = {"status", "last_scan", "last_error", "scanner_running", "ai_available"}
    fields = {k:v for k,v in fields.items() if k in allowed}
    if not fields:
        return
    assignments = ", ".join(f"{key} = ?" for key in fields)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE system_status SET {assignments}, updated_at = CURRENT_TIMESTAMP WHERE id = 1", list(fields.values()))
        await db.commit()
