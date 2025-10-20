import sqlite3
import json

DB_PATH = "autosync.db"
FEEDBACK_FILE = "analytics_feedback/lessons_learned.json"

def analyze_feedback():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT result FROM test_results")
    results = cursor.fetchall()
    conn.close()
    analysis = {"total_tests": len(results), "passed": sum(1 for r in results if r[0]=="passed")}
    print("Analytics:", analysis)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(analysis, f)

if __name__ == "__main__":
    analyze_feedback()
