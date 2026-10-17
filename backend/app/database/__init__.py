from __future__ import annotations
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Protocol

class Repository(Protocol):
    def save(self, investigation: dict) -> None: ...
    def get(self, identifier: str) -> dict | None: ...
    def list(self) -> list[dict]: ...
    def audit(self, identifier: str, action: str, detail: dict) -> None: ...
    def events(self, identifier: str) -> list[dict]: ...

class SQLiteRepository:
    def __init__(self, path=None):
        self.path = path or os.getenv('CORVQ_DB', 'corvq.db')
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS investigations (id TEXT PRIMARY KEY, body TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS audit (seq INTEGER PRIMARY KEY, investigation_id TEXT, at TEXT, action TEXT, detail TEXT)')
    def connect(self):
        return sqlite3.connect(self.path, timeout=15)
    def save(self, investigation):
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO investigations VALUES (?,?)', (investigation['id'], json.dumps(investigation)))
    def get(self, identifier):
        with self.connect() as db:
            row = db.execute('SELECT body FROM investigations WHERE id=?', (identifier,)).fetchone()
        return json.loads(row[0]) if row else None
    def list(self):
        with self.connect() as db:
            rows = db.execute('SELECT body FROM investigations ORDER BY rowid DESC LIMIT 100').fetchall()
        return [{k:v for k,v in json.loads(row[0]).items() if k not in ('records','graph','claims')} for row in rows]
    def audit(self, identifier, action, detail):
        with self.connect() as db:
            db.execute('INSERT INTO audit (investigation_id,at,action,detail) VALUES (?,?,?,?)',
                (identifier, datetime.now(timezone.utc).isoformat(), action, json.dumps(detail)))
    def events(self, identifier):
        with self.connect() as db:
            rows = db.execute('SELECT seq,at,action,detail FROM audit WHERE investigation_id=? ORDER BY seq', (identifier,)).fetchall()
        return [dict(seq=r[0], at=r[1], action=r[2], detail=json.loads(r[3])) for r in rows]

