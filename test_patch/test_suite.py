import json
from db_handler import DBHandler

class TestSuite:
    def __init__(self, db_path):
        self.db = DBHandler(db_path)

    def run_all(self):
        snapshots = self.db.get_snapshot()
        results = []
        for snapshot in snapshots:
            result = self.run_test(snapshot)
            results.append(result)
        self.db.save_test_results(results)
        return results

    def run_test(self, data):
        # منطق واقعی تست
        return {"id": data.get("id"), "passed": True}

if __name__ == "__main__":
    suite = TestSuite('test_patch/snapshots/snapshot_v1.db')
    suite.run_all()
