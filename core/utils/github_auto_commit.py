#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
github_auto_commit.py
🔄 AutoSync Final Core - GitHub Manifest Auto Commit
- commit و push خودکار تغییرات core_manifest.json
- ثبت metadata نسخه و زمان
"""

import os
import subprocess
import json
from datetime import datetime

MANIFEST_PATH = os.path.join("core", "core_manifest.json")

def run_command(cmd):
    """اجرای دستور Git و بازگرداندن خروجی"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[⚠️] Git command failed: {cmd}\n{e.stderr}")
        return None

def auto_commit_manifest():
    """commit و push خودکار manifest به GitHub"""
    if not os.path.exists(MANIFEST_PATH):
        print("[❌] Manifest file not found.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    version = data.get("version", "unknown")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    commit_msg = f'AutoSync: core manifest update (v{version}) @ {timestamp}'

    print("[🧩] Preparing to commit manifest...")
    run_command("git add core/core_manifest.json")
    run_command(f'git commit -m "{commit_msg}"')
    push_output = run_command("git push origin main")

    if push_output:
        print("[✅] Manifest committed and pushed successfully.")
    else:
        print("[⚠️] Push may have failed. Check connection or token.")

def check_git_status():
    """بررسی وضعیت فایل‌های staging"""
    status = run_command("git status --short")
    print("[📋] Current Git status:\n", status or "No changes.")
