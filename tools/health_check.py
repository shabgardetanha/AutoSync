import sqlite3
import json
import os

DB_PATH = "autosync.db"
CONFIG_PATH = "core/core_config.json"

def check_db():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.close()
    print("DB exists and is accessible.")

def check_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config not found at {CONFIG_PATH}")
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    print("Config loaded:", config)

def check_snapshots():
    snapshot_folder = "test_patch/snapshots"
    if not os.path.exists(snapshot_folder):
        raise FileNotFoundError(f"Snapshot folder missing: {snapshot_folder}")
    snapshots = os.listdir(snapshot_folder)
    print(f"Found {len(snapshots)} snapshots.")

if __name__ == "__main__":
    check_db()
    check_config()
    check_snapshots()
    print("Health check complete.")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
health_check.py
Pre-Pipeline Validation for AutoSync Final Core
Version: 1.0.0
Last Updated: 2025-10-19
"""

import os
import json
import datetime
from rich.console import Console
from rich.table import Table

console = Console()

# ------------------------------
# 1. مسیرها و فایل‌های کلیدی
# ------------------------------
CORE_PATHS = [
    "core/auto_sync_core.py",
    "core/github_sync.py",
    "core/retry_lock_manager.py",
    "core/core_config.json",
]
CONFIG_PATHS = [
    "config/ci_cd_config.json",
]
DOCS_PATHS = [
    "docs/summary_final.md",
]
TOOLS_PATHS = [
    "tools/auto_report.py",
    "tools/health_check.py"
]
MANIFEST_FILE = "core_manifest.json"
REQUIREMENTS_FILE = "requirements.txt"

# ------------------------------
# 2. تابع بررسی وجود فایل‌ها
# ------------------------------
def check_files(file_list, label):
    missing = []
    for f in file_list:
        if not os.path.exists(f):
            missing.append(f)
    if missing:
        console.print(f"[bold red]✗ Missing {label} files:[/bold red]")
        for f in missing:
            console.print(f"  └── {f}")
    else:
        console.print(f"[bold green]✓ {label} files OK[/bold green]")
    return missing


# ------------------------------
# 3. بررسی Manifest صحت و هم‌خوانی نسخه
# ------------------------------
def validate_manifest():
    if not os.path.exists(MANIFEST_FILE):
        console.print("[bold red]✗ core_manifest.json not found[/bold red]")
        return False
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    version = data.get("version")
    core = data.get("current_core")
    if not version or not core:
        console.print("[bold red]✗ manifest missing version or current_core[/bold red]")
        return False
    console.print(f"[bold cyan]✓ Manifest version:[/bold cyan] {version}")
    console.print(f"[bold cyan]✓ Current core:[/bold cyan] {core}")
    return True


# ------------------------------
# 4. بررسی نیازمندی‌ها
# ------------------------------
def check_requirements():
    if not os.path.exists(REQUIREMENTS_FILE):
        console.print("[bold yellow]⚠ requirements.txt not found[/bold yellow]")
        return
    with open(REQUIREMENTS_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    console.print(f"[bold green]✓ {len(lines)} dependencies listed[/bold green]")


# ------------------------------
# 5. جمع‌بندی خروجی
# ------------------------------
def main():
    console.print("\n[bold blue]=== AutoSync Final Core: Health-Check Phase ===[/bold blue]\n")

    missing_files = []
    missing_files += check_files(CORE_PATHS, "Core")
    missing_files += check_files(CONFIG_PATHS, "Config")
    missing_files += check_files(DOCS_PATHS, "Docs")
    missing_files += check_files(TOOLS_PATHS, "Tools")

    manifest_ok = validate_manifest()
    check_requirements()

    # جدول خلاصه
    table = Table(title="Health-Check Summary")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="white")

    table.add_row("Missing Files", "❌" if missing_files else "✅", str(len(missing_files)))
    table.add_row("Manifest Valid", "✅" if manifest_ok else "❌", MANIFEST_FILE)
    table.add_row("Last Checked", "🕒", datetime.datetime.now().isoformat())

    console.print("\n")
    console.print(table)

    # کد خروج بر اساس نتیجه
    if missing_files or not manifest_ok:
        console.print("\n[bold red]⛔ Health-Check failed — fix issues before running CI/CD pipeline.[/bold red]")
        exit(1)
    else:
        console.print("\n[bold green]✅ All checks passed — safe to run pipeline.[/bold green]")
        exit(0)


if __name__ == "__main__":
    main()
