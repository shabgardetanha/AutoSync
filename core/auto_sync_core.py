import time
from github_sync import GitHubSync
from core_config import CoreConfig
from db_handler import DBHandler
from utils.github_auto_commit import auto_commit_manifest
from utils.manifest_handler import update_manifest_entry, verify_integrity
# core/auto_sync_core.py
import sqlite3
import time
from github_sync import push_changes
from secrets_manager import get_secret

DB_PATH = "autosync.db"
RETRY_DELAY = 5  # seconds

class AutoSyncCore:
    def __init__(self, config_file='core/core_config.json'):
        self.config = CoreConfig(config_file)
        self.db = DBHandler(self.config.db_path)
        self.github = GitHubSync(self.config.github_token, self.config.repo)
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.locked = False

    def acquire_lock(self):
        if self.locked:
            print("Lock acquired by another process, retrying...")
            return False
        self.locked = True
        return True

    def release_lock(self):
        self.locked = False

    def push_with_retry(self, data):
        max_attempts = self.config.retry_limit
        attempt = 0
        while attempt < max_attempts:
            try:
                self.github.push(data)
                print(f"Push successful on attempt {attempt+1}")
                return True
            except Exception as e:
                print(f"Push failed on attempt {attempt+1}: {e}")
                attempt += 1
                time.sleep(self.config.retry_delay)
        return False

    def lock_resource(self):
        return self.db.acquire_lock('autosync_core_lock')

    def release_resource(self):
        self.db.release_lock('autosync_core_lock')

    def run_cycle(self):
        if not self.lock_resource():
            print("Another instance is running, exiting.")
            return
        try:
            snapshot = self.db.get_snapshot()
            if self.push_with_retry(snapshot):
                self.db.log_success()
        finally:
            self.release_resource()

    def finalize_sync():
        # ... existing manifest update ...
        update_manifest_entry(
            core_name="autosync_final_core",
            version="1.2.0",
            files=[
                "core/auto_sync_core.py",
                "core/github_sync.py",
                "core/core_config.json"
            ]
        )
    
    def check_integrity_before_run():
        verify_integrity()
        auto_commit_manifest()


if __name__ == "__main__":
    core = AutoSyncCore()
    core.run_cycle()
    core.auto_commit_manifest()
    core.verify_integrity()