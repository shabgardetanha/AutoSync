import time
from github_sync import GitHubSync
from core_config import CoreConfig
from db_handler import DBHandler

class AutoSyncCore:
    def __init__(self, config_file='core/core_config.json'):
        self.config = CoreConfig(config_file)
        self.db = DBHandler(self.config.db_path)
        self.github = GitHubSync(self.config.github_token, self.config.repo)

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

if __name__ == "__main__":
    core = AutoSyncCore()
    core.run_cycle()
