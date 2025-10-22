import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path

DB_FILE = "autosync_db.db"
SNAPSHOT_JSON = "autosync_hybrid_snapshot.json"

def init_db(db_file=DB_FILE):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE,
            module TEXT,
            status TEXT,
            gaps TEXT,
            dependencies TEXT,
            last_inspected_utc TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_files INTEGER,
            total_gaps INTEGER,
            total_parse_errors INTEGER,
            total_read_errors INTEGER,
            last_updated_utc TEXT
        )
    """)
    conn.commit()
    conn.close()

def load_snapshot(snapshot_file=SNAPSHOT_JSON):
    with open(snapshot_file, "r", encoding="utf-8") as f:
        return json.load(f)

def upsert_file(conn, path, module, info, timestamp):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO files (path, module, status, gaps, dependencies, last_inspected_utc)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            module=excluded.module,
            status=excluded.status,
            gaps=excluded.gaps,
            dependencies=excluded.dependencies,
            last_inspected_utc=excluded.last_inspected_utc
    """, (
        path,
        module,
        info.get("status"),
        json.dumps(info.get("gaps", [])),
        json.dumps(info.get("dependencies", [])),
        timestamp
    ))
    conn.commit()

def update_summary(conn, summary):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO summary (total_files, total_gaps, total_parse_errors, total_read_errors, last_updated_utc)
        VALUES (?, ?, ?, ?, ?)
    """, (
        summary.get("total_files", 0),
        summary.get("total_gaps", 0),
        summary.get("total_parse_errors", 0),
        summary.get("total_read_errors", 0),
        datetime.now(timezone.utc).isoformat()
    ))
    conn.commit()

def sync_snapshot_to_db(snapshot):
    conn = sqlite3.connect(DB_FILE)
    timestamp = datetime.now(timezone.utc).isoformat()
    for module, module_data in snapshot["modules"].items():
        for path, info in module_data["files"].items():
            upsert_file(conn, path, module, info, timestamp)
    update_summary(conn, snapshot["overall_summary"])
    conn.close()
    print("Snapshot synced to database successfully.")

if __name__ == "__main__":
    init_db()
    snapshot = load_snapshot()
    sync_snapshot_to_db(snapshot)
