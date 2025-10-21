import json, logging

def validate_stability(metrics_file="phase_9_monitoring/runtime_logs/system_health.json", threshold=85):
    """
    ارزیابی پایداری سیستم بر اساس داده‌های Phase 9
    """
    with open(metrics_file) as f:
        data = json.load(f)
    cpu_avg = sum(d["cpu"] for d in data) / len(data)
    memory_avg = sum(d["memory"] for d in data) / len(data)
    stable = cpu_avg < threshold and memory_avg < threshold
    score = {"cpu_avg": cpu_avg, "memory_avg": memory_avg, "stable": stable}
    with open("phase_10_validation/validation_logs/stability_score.json", "w") as f:
        json.dump(score, f, indent=2)
    logging.info(f"✅ Stability validated: {stable}")
    return score
