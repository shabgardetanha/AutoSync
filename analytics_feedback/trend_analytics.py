from db_handler import DBHandler
import sqlite3
import json

DB_PATH = "../core/autosync.db"

def analyze_trends():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("Analyzing trends...")
    # Placeholder: real analytics logic
    trends = {"test_pass_rate": 100, "patch_success_rate": 100}
    with open("lessons_learned.json", "w") as f:
        json.dump(trends, f)
    print("Trend analysis completed")

class TrendAnalytics:
    def __init__(self, db_path):
        self.db = DBHandler(db_path)

    def analyze(self):
        lessons = self.db.get_lessons_learned()
        trends = {}
        for item in lessons:
            key = item['type']
            trends[key] = trends.get(key, 0) + 1
        return trends

def analyze_trends():
    with open('analytics_feedback/lessons_learned.json') as f:
        data = json.load(f)
    trends = {k: "Improvement" for k in data.keys()}
    return trends

if __name__ == "__main__":
    analyze_trends()


    ta = TrendAnalytics('test_patch/snapshots/snapshot_v1.db')
    print(ta.analyze())
