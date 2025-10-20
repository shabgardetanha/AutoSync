import sqlite3
import json
import os

DB_PATH = "autosync.db"
CONFIG_PATH = "core/core_config.json"

def check_db():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.close()
    print("DB exists and is accessible.")

def check_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config not found at {CONFIG_PATH}")
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    print("Config loaded:", config)

def check_snapshots():
    snapshot_folder = "test_patch/snapshots"
    if not os.path.exists(snapshot_folder):
        raise FileNotFoundError(f"Snapshot folder missing: {snapshot_folder}")
    snapshots = os.listdir(snapshot_folder)
    print(f"Found {len(snapshots)} snapshots.")

if __name__ == "__main__":
    check_db()
    check_config()
    check_snapshots()
    print("Health check complete.")
