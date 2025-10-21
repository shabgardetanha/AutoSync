import os

class LockManager:
    def __init__(self, lock_file):
        self.lock_file = lock_file

    def acquire_lock(self):
        if os.path.exists(self.lock_file):
            return False
        with open(self.lock_file, "w") as f:
            f.write("locked")
        return True

    def release_lock(self):
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)
