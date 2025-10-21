import json, hashlib
from datetime import datetime
from pathlib import Path

def calculate_checksum(file_path):
    """Generate SHA256 checksum for version control"""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def update_core_manifest(updated_files=None, version=None):
    """
    Update core_manifest.json when files or version change
    """
    manifest_path = Path(__file__).parent / "core_manifest.json"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    if updated_files:
        new_tracking = []
        for item in manifest["file_tracking"]:
            path = Path(item["path"])
            if path.exists():
                item["checksum"] = calculate_checksum(path)
                item["status"] = "active"
            else:
                item["status"] = "missing"
            new_tracking.append(item)
        manifest["file_tracking"] = new_tracking

    if version:
        manifest["version"] = version

    manifest["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"✅ Manifest updated at {manifest_path}")

if __name__ == "__main__":
    update_core_manifest(updated_files=True)
