#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_manifest_commit_integration.py
🧪 Integration Test - AutoSync Final Core
تست هماهنگی manifest_handler و github_auto_commit
"""

import os
import json
from datetime import datetime

from core.utils.manifest_handler import update_manifest_entry
from core.utils.github_auto_commit import auto_commit_manifest, check_git_status

LOG_PATH = "core/logs/test_manifest_commit.log"
MANIFEST_PATH = "core/core_manifest.json"

def log(msg):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(msg)

def test_manifest_update_and_commit():
    """تست به‌روزرسانی manifest و commit خودکار"""
    log("🔹 Starting integration test...")

    # 1️⃣ بروزرسانی manifest با ورژن تستی
    update_manifest_entry(
        core_name="autosync_final_core_test",
        version="1.2.1",
        files=[
            "core/auto_sync_core.py",
            "core/github_sync.py",
            "core/core_config.json"
        ]
    )

    # 2️⃣ بررسی تغییر در فایل manifest
    if not os.path.exists(MANIFEST_PATH):
        log("[❌] Manifest file not found.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    version = data.get("version", "unknown")
    if version != "1.2.1":
        log(f"[⚠️] Version mismatch in manifest: expected 1.2.1, got {version}")
    else:
        log(f"[✅] Manifest updated successfully to version {version}")

    # 3️⃣ اجرای commit و push خودکار
    log("[🚀] Running auto_commit_manifest()...")
    auto_commit_manifest()

    # 4️⃣ بررسی وضعیت git
    log("[🧩] Checking git status...")
    check_git_status()

    log("[✅] Integration test completed.\n")

if __name__ == "__main__":
    test_manifest_update_and_commit()
