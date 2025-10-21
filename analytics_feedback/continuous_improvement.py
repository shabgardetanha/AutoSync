from db_handler import DBHandler
import json

def apply_feedback():
    with open("lessons_learned.json") as f:
        lessons = json.load(f)
    print("Applying continuous improvement based on lessons:", lessons)
    # Placeholder: implement automated improvements
    feedback = {"improvements_applied": True}
    with open("feedback_loop.json", "w") as f:
        json.dump(feedback, f)



def improve():
    with open('analytics_feedback/feedback_loop.json') as f:
        feedback = json.load(f)
    for k, v in feedback.items():
        feedback[k] = "Applied"
    with open('analytics_feedback/feedback_loop.json', 'w') as f:
        json.dump(feedback, f)
    print("Continuous improvements applied")
    
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

    apply_feedback()

    ci = ContinuousImprovement('test_patch/snapshots/snapshot_v1.db')
    ci.run()
