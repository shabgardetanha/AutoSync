import sqlite3

DB_PATH = "autosync.db"

def display_kpi():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM push_log")
    pushes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM test_results")
    tests = cursor.fetchone()[0]
    conn.close()
    print(f"Dashboard KPI:")
    print(f"Total pushes: {pushes}")
    print(f"Total test executions: {tests}")

if __name__ == "__main__":
    display_kpi()
