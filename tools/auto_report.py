#!/usr/bin/env python3
# tools/auto_report.py
"""
AutoSync Final Integrated - Report Generator
Generates docs/summary_final.md from core_manifest.json and kpi DB.
Designed to run in CI (GitHub Actions) or locally.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
import sys
import os

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "core_manifest.json"
DOCS_DIR = ROOT / "docs"
SUMMARY_FILE = DOCS_DIR / "summary_final.md"
CONFIG_PATH = ROOT / "config" / "ci_cd_config.json"

def read_config():
    cfg = {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        # fallback defaults
        cfg = {
            "report_path": "docs/summary_final.md",
            "manifest_path": "core_manifest.json",
            "kpi_db_path": "db/kpi_results.db"
        }
    return cfg

def read_manifest(path):
    if not path.exists():
        return {"current_core": "N/A", "files": [], "version": "0.0.0", "last_updated": None}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"current_core": "N/A", "files": [], "version": "0.0.0", "last_updated": None}

def get_kpi_rows(db_path):
    if not db_path.exists():
        return []
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT kpi, target, current, status, source FROM kpi_table")
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def generate_markdown(manifest, kpi_rows):
    date_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    md = []
    md.append(f"# 🚀 AutoSync Final Core – System Summary ({manifest.get('version','vX.X')})")
    md.append(f"**Generated:** {date_str}  ")
    md.append(f"**Core Reference:** `{manifest.get('current_core','N/A')}`  ")
    md.append("\n---\n")
    md.append("## ⚙️ Core Files")
    if not manifest.get("files"):
        md.append("_No core files listed in manifest._")
    else:
        for f in manifest.get("files", []):
            md.append(f"- `{f}`")
    md.append("\n---\n")
    md.append("## 📊 KPI Summary")
    if not kpi_rows:
        md.append("_No KPI data found or DB missing._")
    else:
        md.append("| KPI | Target | Current | Status | Source |")
        md.append("|------|---------|---------|----------|----------|")
        for kpi, target, current, status, source in kpi_rows:
            md.append(f"| {kpi} | {target} | {current} | {status} | {source} |")
    md.append("\n---\n")
    md.append("**AutoSync QA Signature:**  ")
    md.append(f"> Generated automatically via `tools/auto_report.py` on {date_str}  ")
    return "\n".join(md)

def save_report(content, out_path):
    out_dir = out_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[✅] Report saved to: {out_path}")

def main():
    cfg = read_config()
    manifest_path = ROOT / cfg.get("manifest_path", "core_manifest.json")
    kpi_db_path = ROOT / cfg.get("kpi_db_path", "db/kpi_results.db")
    manifest = read_manifest(manifest_path)
    kpi_rows = get_kpi_rows(Path(kpi_db_path))
    md = generate_markdown(manifest, kpi_rows)
    out_file = ROOT / cfg.get("report_path", "docs/summary_final.md")
    save_report(md, out_file)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[❌] auto_report failed: {e}", file=sys.stderr)
        sys.exit(1)
