from db_handler import DBHandler
from dashboard.dashboard_data_handler import get_latest_analysis

class Dashboard:
    def __init__(self, db_path):
        self.db = DBHandler(db_path)

    def display_kpis(self):
        kpis = self.db.get_kpis()
        for kpi in kpis:
            print(f"{kpi['name']}: {kpi['value']}")

def show_dashboard():
    print("🧭 AutoSync Dashboard – Version Stability")
    report = get_latest_analysis()
    if "summary" in report:
        print(report["summary"])
        return
    print(f"📅 Date: {report['timestamp']}")
    print(f"🆕 Added: {report['added']}")
    print(f"✏️ Modified: {report['modified']}")
    print(f"❌ Removed: {report['removed']}")
    print(f"📊 Stability Index: {report['stability_index']}%")
    print("--------------------------------------------------")

if __name__ == "__main__":
    with open("core/core_manifest.json") as f:
        version = json.load(f)["version"]
    print(f"🧩 AutoSync Core Version: {version}")
    print(json.dumps(test_results, indent=2))

    dash = Dashboard('test_patch/snapshots/snapshot_v1.db')
    dash.display_kpis()
    show_dashboard()
