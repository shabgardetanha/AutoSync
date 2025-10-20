import sqlite3

DB_PATH = "autosync.db"

def send_notification(message):
    print(f"Notification: {message}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notifications (timestamp, message) VALUES (datetime('now'), ?)", (message,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    send_notification("Test alert: AutoSync pipeline executed.")
