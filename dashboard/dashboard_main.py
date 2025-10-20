from db_handler import DBHandler

class Dashboard:
    def __init__(self, db_path):
        self.db = DBHandler(db_path)

    def display_kpis(self):
        kpis = self.db.get_kpis()
        for kpi in kpis:
            print(f"{kpi['name']}: {kpi['value']}")

if __name__ == "__main__":
    dash = Dashboard('test_patch/snapshots/snapshot_v1.db')
    dash.display_kpis()
