from db_handler import DBHandler

class ContinuousImprovement:
    def __init__(self, db_path):
        self.db = DBHandler(db_path)

    def run(self):
        feedback = self.db.get_feedback()
        improvements = []
        for item in feedback:
            improvements.append({"id": item['id'], "suggestion": "Review required"})
        self.db.save_feedback_loop(improvements)
        return improvements

if __name__ == "__main__":
    ci = ContinuousImprovement('test_patch/snapshots/snapshot_v1.db')
    ci.run()
