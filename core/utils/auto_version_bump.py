#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_version_bump.py
🔁 Auto Version Incrementer for AutoSync Final Core

وظیفه:
- خواندن نسخه فعلی از core_manifest.json
- افزایش نسخه به صورت خودکار (مثلاً 1.2.1 → 1.2.2)
- ثبت تغییر در manifest
- commit و push تغییر
"""

import json
import os
from datetime import datetime
from core.utils.github_auto_commit import auto_commit_manifest
from core.utils.manifest_handler import update_manifest_entry

MANIFEST_PATH = "core/core_manifest.json"
LOG_PATH = "core/logs/auto_version_bump.log"


def log(msg):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(msg)


def bump_version(version: str) -> str:
    """افزایش عدد نسخه به صورت خودکار"""
    parts = version.split(".")
    if len(parts) != 3:
        log(f"[⚠️] Invalid version format: {version}")
        return version
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def auto_bump_and_commit(core_name="autosync_final_core_v1"):
    log("🔹 Starting auto version bump...")

    if not os.path.exists(MANIFEST_PATH):
        log("[❌] core_manifest.json not found.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    current_version = data.get("version", "1.0.0")
    new_version = bump_version(current_version)

    update_manifest_entry(
        core_name=core_name,
        version=new_version,
        files=data.get("files", [])
    )

    log(f"[✅] Version bumped from {current_version} → {new_version}")

    # Commit & Push
    log("[🚀] Running auto_commit_manifest()...")
    auto_commit_manifest()

    log("[✅] Auto version bump completed.\n")


if __name__ == "__main__":
    auto_bump_and_commit()
