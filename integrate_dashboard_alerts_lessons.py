import os
import json
import sqlite3
from datetime import datetime, timezone
import smtplib
from email.message import EmailMessage

# ---------- CONFIG ----------
DB_FILE = "autosync_db.db"
DASHBOARD_CONFIG = "autosync_repo/dashboard/dashboard_config.json"
ALERTS_CONFIG = "autosync_repo/notifications/notifications_config.json"
LESSONS_LEARNED = "autosync_repo/analytics_feedback/lessons_learned.json"
ALERT_EMAIL = "user@example.com"  # ایمیل خود را قرار دهید
# ----------------------------

def fetch_db_data(db_file):
    if not os.path.exists(db_file):
        return {"error": "db_missing"}
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # خواندن Taskها
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    # خواندن نتایج تست‌ها
    cursor.execute("SELECT * FROM test_results")
    test_results = cursor.fetchall()

    # خواندن Patchها
    cursor.execute("SELECT * FROM patches_applied")
    patch_history = cursor.fetchall()

    conn.close()
    return {"tasks": tasks, "tests": test_results, "patches": patch_history}

# ---------------- Dashboard ----------------
def update_dashboard(data):
    if not os.path.exists(DASHBOARD_CONFIG):
        return
    with open(DASHBOARD_CONFIG, "r+", encoding="utf-8") as f:
        config = json.load(f)
        config["last_update"] = datetime.now(timezone.utc).isoformat()
        config["tasks_summary"] = {
            "total": len(data["tasks"]),
            "completed": len([t for t in data["tasks"] if t[2] == "done"])  # فرض ستون 3 وضعیت است
        }
        f.seek(0)
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.truncate()
    print("[Dashboard] Updated")

# ---------------- Alerts ----------------
def send_alerts(data):
    failed_tests = [t for t in data["tests"] if t[3] == "failed"]  # فرض ستون 4 وضعیت تست
    if not failed_tests:
        print("[Alerts] No failed tests")
        return

    msg = EmailMessage()
    msg.set_content(f"{len(failed_tests)} tests failed in AutoSync pipeline!")
    msg['Subject'] = "AutoSync Alert"
    msg['From'] = "autosync@system.local"
    msg['To'] = ALERT_EMAIL
    try:
        with smtplib.SMTP('localhost') as s:
            s.send_message(msg)
        print(f"[Alerts] Sent email to {ALERT_EMAIL}")
    except Exception as e:
        print(f"[Alerts] Failed to send email: {e}")

# ---------------- Lessons Learned ----------------
def update_lessons_learned(data):
    if not os.path.exists(LESSONS_LEARNED):
        return
    with open(LESSONS_LEARNED, "r+", encoding="utf-8") as f:
        lessons = json.load(f)
        lessons["last_update"] = datetime.now(timezone.utc).isoformat()
        lessons["test_summary"] = {
            "total_tests": len(data["tests"]),
            "failed_tests": len([t for t in data["tests"] if t[3] == "failed"])
        }
        lessons["patch_summary"] = {
            "total_patches": len(data["patches"])
        }
        f.seek(0)
        json.dump(lessons, f, indent=2, ensure_ascii=False)
        f.truncate()
    print("[Lessons Learned] Updated")

# ---------------- Main ----------------
def main():
    data = fetch_db_data(DB_FILE)
    if "error" in data:
        print("[Error] Database missing or not accessible")
        return

    update_dashboard(data)
    send_alerts(data)
    update_lessons_learned(data)
    print("[AutoSync Integration] Completed successfully")

if __name__ == "__main__":
    main()
