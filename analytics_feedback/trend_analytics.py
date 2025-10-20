from db_handler import DBHandler

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

if __name__ == "__main__":
    ta = TrendAnalytics('test_patch/snapshots/snapshot_v1.db')
    print(ta.analyze())
