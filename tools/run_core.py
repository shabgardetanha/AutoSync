import sqlite3
import json
import threading
import time
from pathlib import Path

DB_PATH = "autosync.db"
CONFIG_PATH = "core/core_config.json"
LOCK_FILE = "core/core.lock"

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def acquire_lock():
    while Path(LOCK_FILE).exists():
        print("Lock exists, waiting...")
        time.sleep(1)
    Path(LOCK_FILE).touch()

def release_lock():
    if Path(LOCK_FILE).exists():
        Path(LOCK_FILE).unlink()

def push_to_db(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO push_log (timestamp, data) VALUES (datetime('now'), ?)", (json.dumps(data),))
    conn.commit()
    conn.close()
    print("Push logged to DB.")

def core_cycle():
    config = load_config()
    acquire_lock()
    try:
        print("Running Core Push/Retry cycle...")
        push_to_db({"status": "success", "details": config})
    finally:
        release_lock()

if __name__ == "__main__":
    core_cycle()
