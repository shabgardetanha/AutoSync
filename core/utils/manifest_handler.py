#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
manifest_handler.py
🧠 AutoSync Final Core - Manifest Manager
- ثبت تغییرات نسخه و مسیر فایل‌های هسته
- بررسی صحت فایل‌ها (checksum)
- نگهداری نسخه جاری برای traceability کامل
"""

import os
import json
import hashlib
from datetime import datetime

MANIFEST_PATH = os.path.join("core", "core_manifest.json")

def calculate_checksum(file_path):
    """محاسبه هش SHA256 فایل برای کنترل صحت"""
    if not os.path.exists(file_path):
        return None
    hash_sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha.update(chunk)
    return hash_sha.hexdigest()

def load_manifest():
    """خواندن فایل manifest"""
    if not os.path.exists(MANIFEST_PATH):
        return {"current_core": None, "files": [], "version": "0.0.0", "last_updated": None}
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_manifest(manifest_data):
    """ذخیره فایل manifest"""
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

def update_manifest_entry(core_name, version, files):
    """به‌روزرسانی یا ایجاد manifest جدید"""
    manifest = load_manifest()
    manifest["current_core"] = core_name
    manifest["version"] = version
    manifest["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    manifest["files"] = []
    for file_path in files:
        manifest["files"].append({
            "path": file_path,
            "checksum": calculate_checksum(file_path)
        })

    save_manifest(manifest)
    print(f"[✅] Manifest updated successfully: {version}")

def verify_integrity():
    """بررسی صحت فایل‌ها بر اساس checksum"""
    manifest = load_manifest()
    mismatches = []

    for file_entry in manifest.get("files", []):
        path = file_entry["path"]
        expected = file_entry.get("checksum")
        actual = calculate_checksum(path)
        if actual != expected:
            mismatches.append(path)

    if mismatches:
        print(f"[⚠️] Integrity check failed for files: {mismatches}")
        return False
    print("[✅] All core files verified successfully.")
    return True
