from db_handler import DBHandler

class PatchBatchRunner:
    def __init__(self, db_path):
        self.db = DBHandler(db_path)

    def run_batch(self, batch_number):
        patches = self.db.get_pending_patches(batch_number)
        results = []
        for patch in patches:
            res = self.apply_patch(patch)
            results.append(res)
        self.db.save_patch_results(batch_number, results)
        return results

    def apply_patch(self, patch):
        # منطق اعمال Patch واقعی
        patch['applied'] = True
        return patch

if __name__ == "__main__":
    runner = PatchBatchRunner('test_patch/snapshots/snapshot_v1.db')
    runner.run_batch(1)
