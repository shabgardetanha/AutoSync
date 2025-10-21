import json

def compare_manifests(current_path, previous_path):
    with open(current_path) as cur, open(previous_path) as prev:
        cur_data, prev_data = json.load(cur), json.load(prev)
    diff = [f for f in cur_data["file_tracking"] if f not in prev_data["file_tracking"]]
    return diff
