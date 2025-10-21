import json
import os
from datetime import datetime

def load_manifest_diffs(path="audit_checker/manifest_diffs.json"):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def analyze_diff_trends(data):
    if not data:
        return {"summary": "No data available"}
    total = len(data["diffs"])
    added = sum(1 for d in data["diffs"] if "🆕" in d["change"])
    modified = sum(1 for d in data["diffs"] if "✏️" in d["change"])
    removed = sum(1 for d in data["diffs"] if "❌" in d["change"])
    
    stability_index = max(0, 100 - (modified * 3 + added * 5 + removed * 7))
    return {
        "timestamp": data["timestamp"],
        "total_changes": total,
        "added": added,
        "modified": modified,
        "removed": removed,
        "stability_index": stability_index,
    }

def get_latest_analysis():
    data = load_manifest_diffs()
    return analyze_diff_trends(data)
