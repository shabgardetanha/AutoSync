import os
import json
import sqlite3
import yaml
import hashlib
import ast
from pathlib import Path
from datetime import datetime, timezone
import subprocess

# ---------- CONFIG ----------
REPO_URL = "https://github.com/shabgardetanha/AutoSync.git"
CLONE_DIR = "autosync_repo"
BRANCH = "main"
OUTPUT_JSON = "autosync_graph_snapshot.json"
DB_EXTENSIONS = [".db", ".sqlite"]
CONFIG_EXTENSIONS = [".json", ".yaml", ".yml"]
CODE_EXTENSIONS = [".py", ".js", ".ts"]
# ----------------------------

def clone_or_update_repo(url, path, branch="main"):
    if os.path.exists(path):
        subprocess.run(["git", "-C", path, "checkout", branch], check=True)
        subprocess.run(["git", "-C", path, "pull"], check=True)
    else:
        subprocess.run(["git", "clone", "-b", branch, url, path], check=True)

def file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None

def extract_python_dependencies(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            src = f.read()
        node = ast.parse(src, filename=file_path)
    except:
        return ["parse_error"]

    imports = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Import):
            for alias in n.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom):
            if n.module:
                imports.add(n.module.split(".")[0])
            for alias in n.names:
                if alias and getattr(alias, "name", None):
                    imports.add(alias.name.split(".")[0])
    return sorted(list(imports))

def extract_js_dependencies(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            src = f.read()
        import_lines = [line for line in src.splitlines() if "import " in line or "require(" in line]
        deps = []
        for line in import_lines:
            parts = line.replace("import","").replace("from","").replace("require(","").replace(")","").replace("'","").replace('"','').split()
            if parts:
                deps.append(parts[-1].strip())
        return deps
    except:
        return ["parse_error"]

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

def get_file_node(file_path):
    p = Path(file_path)
    node = {
        "id": str(p),
        "type": None,
        "size_bytes": p.stat().st_size if p.exists() else None,
        "hash": file_hash(file_path) if p.exists() else None,
        "dependencies": [],
        "gaps": [],
    }
    if not p.exists():
        node["gaps"].append("missing_file")
        return node

    if p.suffix == ".py":
        node["dependencies"] = extract_python_dependencies(file_path)
        node["type"] = "python"
        if "parse_error" in node["dependencies"]:
            node["gaps"].append("parse_error")
    elif p.suffix in [".js", ".ts"]:
        node["dependencies"] = extract_js_dependencies(file_path)
        node["type"] = "js/ts"
        if "parse_error" in node["dependencies"]:
            node["gaps"].append("parse_error")
    elif p.suffix in CONFIG_EXTENSIONS:
        node["dependencies"] = extract_config_dependencies(file_path)
        node["type"] = "config"
        if "read_error" in node["dependencies"]:
            node["gaps"].append("read_error")
    elif p.suffix in DB_EXTENSIONS:
        node["dependencies"] = extract_db_schema(file_path)
        node["type"] = "database"
    else:
        node["type"] = "other"
    return node

def build_dependency_graph(root_dir):
    nodes = {}
    edges = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            node = get_file_node(fp)
            nodes[fp] = node
            for dep in node["dependencies"]:
                edges.append({"from": fp, "to": dep})
    return nodes, edges

def main():
    clone_or_update_repo(REPO_URL, CLONE_DIR, BRANCH)
    nodes, edges = build_dependency_graph(CLONE_DIR)
    summary = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "status": "All files scanned"
    }
    snapshot = {
        "repo": REPO_URL,
        "branch": BRANCH,
        "scanned_at_utc": datetime.now(timezone.utc).isoformat(),
        "nodes": nodes,
        "edges": edges,
        "summary": summary
    }
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    print(f"Dependency graph snapshot saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
