#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_autosync_final_core_v2.py
- نسخه ارتقا یافته AutoSync Final Core
- پشتیبانی هم‌زمان DB و JSON
- ساختار پوشه، DB، Snapshot اولیه و JSON ذخیره‌سازی همزمان
"""

import os
import subprocess
import sqlite3
import json
from pathlib import Path
from datetime import datetime

# -----------------------------
# 1. نصب پکیج‌ها
# -----------------------------
def install_requirements():
    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        print("[INFO] Installing required packages...")
        subprocess.run(["pip", "install", "-r", str(req_file)])
    else:
        print("[WARN] requirements.txt not found!")

# -----------------------------
# 2. ساختار پوشه‌ها
# -----------------------------
def create_folders(base_dir="AutoSync_Final_Core_v2"):
    print("[INFO] Creating project folder structure...")
    folders = [
        base_dir,
        f"{base_dir}/core",
        f"{base_dir}/test_patch/snapshots",
        f"{base_dir}/dashboard",
        f"{base_dir}/analytics_feedback",
        f"{base_dir}/connectors",
        f"{base_dir}/logs",
        f"{base_dir}/data"   # برای ذخیره JSONهای همزمان
    ]
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Folders created under {base_dir}/")

# -----------------------------
# 3. ایجاد DB اولیه
# -----------------------------
def initialize_db(db_path="AutoSync_Final_Core_v2/core/autosync.db"):
    print("[INFO] Initializing SQLite DB...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # جدول Patch/Test
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patch_test (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_name TEXT,
            patch_name TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # جدول Lessons Learned
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons_learned (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            severity TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # جدول Notifications/CI
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            message TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()
    print(f"[INFO] Database created at {db_path}")

# -----------------------------
# 4. ایجاد Snapshot اولیه و ذخیره JSON همزمان
# -----------------------------
def create_initial_snapshot(snapshot_file="AutoSync_Final_Core_v2/test_patch/snapshots/initial_snapshot.json",
                            json_file="AutoSync_Final_Core_v2/data/snapshot.json"):
    print("[INFO] Creating initial snapshot...")
    snapshot_data = {
        "version": "v2.0",
        "tasks": [],
        "patches": [],
        "kpi": {},
        "feedback": [],
        "timestamp": datetime.now().isoformat()
    }

    # ذخیره در پوشه Snapshots برای اجرای Patch/Test
    with open(snapshot_file, "w") as f:
        json.dump(snapshot_data, f, indent=4)

    # ذخیره همزمان در پوشه data/ برای مدیریت و بازیابی سریع
    with open(json_file, "w") as f:
        json.dump(snapshot_data, f, indent=4)

    print(f"[INFO] Initial snapshot created at {snapshot_file} and {json_file}")

# -----------------------------
# 5. همزمان‌سازی DB و JSON (Utility)
# -----------------------------
def sync_db_to_json(db_path="AutoSync_Final_Core_v2/core/autosync.db",
                    json_file="AutoSync_Final_Core_v2/data/full_data.json"):
    print("[INFO] Syncing DB to JSON...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    data = {}
    for table in ["patch_test", "lessons_learned", "notifications"]:
        cursor.execute(f"SELECT * FROM {table}")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        data[table] = [dict(zip(columns, row)) for row in rows]

    conn.close()

    with open(json_file, "w") as f:
        json.dump(data, f, indent=4)
    print(f"[INFO] DB synced to JSON at {json_file}")

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    install_requirements()
    create_folders()
    initialize_db()
    create_initial_snapshot()
    sync_db_to_json()
    print("[SUCCESS] AutoSync Final Core v2 setup complete. Ready for Patch/Test/Feedback cycle!")
