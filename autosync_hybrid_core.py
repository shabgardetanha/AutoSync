# autosync_hybrid_core.py
import os
import json
import sqlite3
import yaml
from pathlib import Path
import subprocess
import ast
from datetime import datetime, timezone

# ---------- CONFIG ----------
REPO_URL = "https://github.com/shabgardetanha/AutoSync.git"
CLONE_DIR = "autosync_repo"
BRANCH = "main"
OUTPUT_JSON = "autosync_hybrid_snapshot.json"
DB_EXTENSIONS = [".db", ".sqlite"]
CONFIG_EXTENSIONS = [".json", ".yaml", ".yml"]
MODULES = ["core", "tools", "test_patch"]
# ----------------------------

def clone_or_update_repo(url, path, branch="main"):
    if os.path.exists(path):
        subprocess.run(["git", "-C", path, "checkout", branch], check=True)
        subprocess.run(["git", "-C", path, "pull"], check=True)
    else:
        subprocess.run(["git", "clone", "-b", branch, url, path], check=True)
def extract_python_dependencies(file_path):
    """
    Safely parse a Python file and return a list of imported module names.
    Returns:
      - list of module names (strings) on success
      - ["parse_error"] on read/parse failure (UnicodeDecodeError, SyntaxError, etc.)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            src = f.read()
    except Exception as e:
        # Could be permission, encoding, or other I/O error
        return ["parse_error"]

    try:
        node = ast.parse(src, filename=file_path)
    except Exception:
        # SyntaxError or other AST parse issues
        return ["parse_error"]

    imports = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Import):
            for alias in n.names:
                if alias and getattr(alias, "name", None):
                    # top-level package name (e.g. "os.path" -> "os")
                    imports.add(alias.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom):
            # n.module might be None for relative imports (e.g. from . import something)
            mod = n.module
            if mod:
                imports.add(mod.split(".")[0])
            # also consider names in from ... import x as y
            for alias in n.names:
                if alias and getattr(alias, "name", None):
                    imports.add(alias.name.split(".")[0])
    return sorted(list(imports))

def extract_config_dependencies(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.endswith(".json"):
                data = json.load(f)
            else:
                data = yaml.safe_load(f)
        deps = []
        if isinstance(data, dict):
            for k,v in data.items():
                if isinstance(v, str) and any(ext in v for ext in DB_EXTENSIONS + CONFIG_EXTENSIONS):
                    deps.append(v)
        return deps
    except:
        return ["read_error"]

def extract_db_schema(db_path):
    schema = {}
    if not os.path.exists(db_path):
        return {"error": "db_missing"}
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for t in tables:
            table_name = t[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            cols = cursor.fetchall()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_rows = cursor.fetchall()
            schema[table_name] = {"columns": cols, "sample_rows": sample_rows}
        conn.close()
    except Exception as e:
        schema = {"error": str(e)}
    return schema

def get_file_info(file_path):
    p = Path(file_path)
    info = {
        "status": "exists" if p.exists() else "missing",
        "gaps": [],
        "dependencies": [],
        "content_summary": ""
    }
    if p.is_file():
        if p.suffix == ".py":
            info["dependencies"] = extract_python_dependencies(file_path)
            if "parse_error" in info["dependencies"]:
                info["gaps"].append("parse_error")
        elif p.suffix in CONFIG_EXTENSIONS:
            deps = extract_config_dependencies(file_path)
            info["dependencies"] = deps
            if "read_error" in deps:
                info["gaps"].append("read_error")
    return info

def scan_module(root_dir, module_name):
    module_path = os.path.join(root_dir, module_name)
    files_info = {}
    total_files = total_gaps = total_parse_errors = total_read_errors = 0
    if os.path.exists(module_path):
        for dirpath, dirnames, filenames in os.walk(module_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                fi = get_file_info(fp)
                files_info[fp] = fi
                total_files += 1
                total_gaps += len(fi["gaps"])
                total_parse_errors += fi["gaps"].count("parse_error")
                total_read_errors += fi["gaps"].count("read_error")
    else:
        files_info[module_path] = {"status": "missing", "gaps": ["folder_missing"]}
        total_gaps += 1
    summary = {
        "total_files": total_files,
        "total_gaps": total_gaps,
        "total_parse_errors": total_parse_errors,
        "total_read_errors": total_read_errors,
        "actions_needed": []
    }
    if total_gaps > 0:
        summary["actions_needed"].append("check_gaps")
    return files_info, summary

def main():
    clone_or_update_repo(REPO_URL, CLONE_DIR, BRANCH)
    modules_info = {}
    overall_files = overall_gaps = overall_parse_errors = overall_read_errors = 0

    for module in MODULES:
        files_info, summary = scan_module(CLONE_DIR, module)
        modules_info[module] = {"files": files_info, "summary": summary}
        overall_files += summary["total_files"]
        overall_gaps += summary["total_gaps"]
        overall_parse_errors += summary["total_parse_errors"]
        overall_read_errors += summary["total_read_errors"]

    overall_summary = {
        "total_files": overall_files,
        "total_gaps": overall_gaps,
        "total_parse_errors": overall_parse_errors,
        "total_read_errors": overall_read_errors,
        "status": "All files exist, no GAP detected." if overall_gaps==0 else "GAPs detected",
        "actions_needed": []
    }

    snapshot = {"modules": modules_info, "overall_summary": overall_summary,
                "inspected_at_utc": datetime.now(timezone.utc).isoformat()}

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    print(f"Hybrid snapshot saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
