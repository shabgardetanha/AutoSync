import psutil, time, json, logging

def monitor_system(interval=10, duration=300):
    """
    پایش منابع سیستم و جمع‌آوری داده‌های مصرف CPU، حافظه و I/O دیسک
    """
    start = time.time()
    data = []
    while time.time() - start < duration:
        snapshot = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "disk_io": psutil.disk_io_counters()._asdict()
        }
        data.append(snapshot)
        time.sleep(interval)
    with open("phase_9_monitoring/runtime_logs/system_health.json", "w") as f:
        json.dump(data, f, indent=2)
    logging.info("✅ Runtime monitoring completed.")
    return data
