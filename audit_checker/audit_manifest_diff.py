import json
import hashlib
import os
from datetime import datetime

def hash_file(path):
    """تولید هش برای تشخیص تغییر واقعی"""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def compare_manifests(current_manifest, previous_manifest):
    """مقایسه دو نسخه manifest"""
    with open(current_manifest) as cur, open(previous_manifest) as prev:
        cur_data, prev_data = json.load(cur), json.load(prev)

    diffs = []
    cur_files = {f["path"]: f["hash"] for f in cur_data["file_tracking"]}
    prev_files = {f["path"]: f["hash"] for f in prev_data["file_tracking"]}

    for path, hash_val in cur_files.items():
        if path not in prev_files:
            diffs.append({"file": path, "change": "🆕 Added"})
        elif hash_val != prev_files[path]:
            diffs.append({"file": path, "change": "✏️ Modified"})

    for path in prev_files:
        if path not in cur_files:
            diffs.append({"file": path, "change": "❌ Removed"})

    return diffs

def save_diffs_report(diffs):
    """ذخیره نتیجه در فایل و ثبت زمان"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "diffs": diffs
    }
    os.makedirs("analytics_feedback", exist_ok=True)
    path = "analytics_feedback/manifest_diffs.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"✅ Manifest diff report saved: {path}")

if __name__ == "__main__":
    diffs = compare_manifests("core/core_manifest.json", "snapshots/core_manifest_prev.json")
    if diffs:
        save_diffs_report(diffs)
        print(f"⚠️ Found {len(diffs)} differences in manifest files!")
    else:
        print("✅ No differences found in manifest comparison.")
