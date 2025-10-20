import time
from threading import Lock

class RetryLockManager:
    def __init__(self):
        self.lock = Lock()
        self.retry_interval = 5

    def acquire_lock(self):
        return self.lock.acquire(blocking=False)

    def release_lock(self):
        self.lock.release()

    def retry_later(self, func):
        time.sleep(self.retry_interval)
        func()
