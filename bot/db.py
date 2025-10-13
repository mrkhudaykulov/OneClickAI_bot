import asyncio
from typing import Any, Optional, Sequence, List

import aiosqlite

DB_PATH = "bot.sqlite3"

_init_sql = r"""
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  username TEXT,
  first_name TEXT,
  last_name TEXT,
  credits INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS groups (
  chat_id INTEGER PRIMARY KEY,
  title TEXT,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Each group can award bonus once; tracks who claimed
CREATE TABLE IF NOT EXISTS group_bonus_claims (
  group_id INTEGER PRIMARY KEY,
  claimed_by_user_id INTEGER NOT NULL,
  claimed_at TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  FOREIGN KEY (group_id) REFERENCES groups(chat_id) ON DELETE CASCADE,
  FOREIGN KEY (claimed_by_user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
"""

async def _execute(db: aiosqlite.Connection, sql: str, params: Sequence[Any] | None = None) -> None:
    await db.execute(sql, params or [])

async def _fetchone(db: aiosqlite.Connection, sql: str, params: Sequence[Any] | None = None) -> Optional[aiosqlite.Row]:
    cur = await db.execute(sql, params or [])
    row = await cur.fetchone()
    await cur.close()
    return row

async def _fetchall(db: aiosqlite.Connection, sql: str, params: Sequence[Any] | None = None) -> List[aiosqlite.Row]:
    cur = await db.execute(sql, params or [])
    rows = await cur.fetchall()
    await cur.close()
    return rows

async def init_db(path: str = DB_PATH) -> None:
    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row
        await db.executescript(_init_sql)
        # Seed default settings if not present
        defaults = {
            "MONETIZATION_ENABLED": "false",
            "DEFAULT_FREE_CREDITS": "20",
            "GROUP_BONUS_CREDITS": "5",
            "BOT_USERNAME": "",
        }
        for key, value in defaults.items():
            await _execute(
                db,
                "INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO NOTHING",
                (key, value),
            )
        await db.commit()

async def set_setting(key: str, value: str, path: str = DB_PATH) -> None:
    async with aiosqlite.connect(path) as db:
        await _execute(db, "INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
        await db.commit()

async def get_setting(key: str, path: str = DB_PATH) -> Optional[str]:
    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row
        row = await _fetchone(db, "SELECT value FROM settings WHERE key=?", (key,))
        return row["value"] if row else None

async def ensure_user(user_id: int, username: Optional[str], first_name: Optional[str], last_name: Optional[str], path: str = DB_PATH) -> None:
    async with aiosqlite.connect(path) as db:
        await _execute(
            db,
            (
                "INSERT INTO users(user_id, username, first_name, last_name, credits) "
                "VALUES(?,?,?,?, COALESCE((SELECT value FROM settings WHERE key='DEFAULT_FREE_CREDITS'), '20')) "
                "ON CONFLICT(user_id) DO UPDATE SET "
                "username=excluded.username, first_name=excluded.first_name, last_name=excluded.last_name, "
                "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now')"
            ),
            (user_id, username, first_name, last_name),
        )
        await db.commit()

async def get_user_credits(user_id: int, path: str = DB_PATH) -> int:
    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row
        row = await _fetchone(db, "SELECT credits FROM users WHERE user_id=?", (user_id,))
        return int(row["credits"]) if row else 0

async def increment_user_credits(user_id: int, delta: int, path: str = DB_PATH) -> None:
    if delta == 0:
        return
    async with aiosqlite.connect(path) as db:
        await _execute(db, "UPDATE users SET credits=credits+?, updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE user_id=?", (delta, user_id))
        await db.commit()

async def consume_user_credit(user_id: int, amount: int = 1, path: str = DB_PATH) -> bool:
    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row
        # optimistic check-decrement
        row = await _fetchone(db, "SELECT credits FROM users WHERE user_id=?", (user_id,))
        if not row:
            return False
        credits = int(row["credits"])
        if credits < amount:
            return False
        await _execute(db, "UPDATE users SET credits=credits-?, updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE user_id=?", (amount, user_id))
        await db.commit()
        return True

async def remove_user(user_id: int, path: str = DB_PATH) -> None:
    async with aiosqlite.connect(path) as db:
        await _execute(db, "DELETE FROM users WHERE user_id=?", (user_id,))
        await db.commit()

async def upsert_group(chat_id: int, title: Optional[str], is_active: bool = True, path: str = DB_PATH) -> None:
    async with aiosqlite.connect(path) as db:
        await _execute(
            db,
            "INSERT INTO groups(chat_id, title, is_active) VALUES(?,?,?) ON CONFLICT(chat_id) DO UPDATE SET title=excluded.title, is_active=excluded.is_active, updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now')",
            (chat_id, title or "", 1 if is_active else 0),
        )
        await db.commit()

async def set_group_active(chat_id: int, active: bool, path: str = DB_PATH) -> None:
    async with aiosqlite.connect(path) as db:
        await _execute(db, "UPDATE groups SET is_active=?, updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE chat_id=?", (1 if active else 0, chat_id))
        await db.commit()

async def remove_group(chat_id: int, path: str = DB_PATH) -> None:
    async with aiosqlite.connect(path) as db:
        await _execute(db, "DELETE FROM groups WHERE chat_id=?", (chat_id,))
        await db.commit()

async def claim_group_bonus(group_id: int, user_id: int, path: str = DB_PATH) -> bool:
    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row
        # Ensure group exists
        await _execute(db, "INSERT INTO groups(chat_id, title, is_active) VALUES(?, '', 1) ON CONFLICT(chat_id) DO NOTHING", (group_id,))
        # Insert claim if not exists
        try:
            await _execute(db, "INSERT INTO group_bonus_claims(group_id, claimed_by_user_id) VALUES(?,?)", (group_id, user_id))
        except Exception:
            # already claimed
            return False
        # Determine bonus amount
        row = await _fetchone(db, "SELECT value FROM settings WHERE key='GROUP_BONUS_CREDITS'", ())
        bonus = int(row["value"]) if row else 5
        await _execute(db, "UPDATE users SET credits=credits+?, updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE user_id=?", (bonus, user_id))
        await db.commit()
        return True

async def list_user_ids(path: str = DB_PATH) -> List[int]:
    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row
        rows = await _fetchall(db, "SELECT user_id FROM users", ())
        return [int(r["user_id"]) for r in rows]

async def list_active_group_ids(path: str = DB_PATH) -> List[int]:
    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row
        rows = await _fetchall(db, "SELECT chat_id FROM groups WHERE is_active=1", ())
        return [int(r["chat_id"]) for r in rows]
