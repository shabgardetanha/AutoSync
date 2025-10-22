# autosync_analyzer_core.py
"""
AutoSync Analyzer Core
Reads a repo snapshot (inspector/hybrid snapshot) and decides the next phase and actions.
Produces autosync_analysis.json. If autosync_analysis_prev.json exists it will produce diffs.
Output is in Persian-friendly keys but machine-readable (UTF-8 JSON).
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone

# ------------ CONFIG ------------
# پذیرش چند نام فایل snapshot متداول:
SNAPSHOT_CANDIDATES = [
    "autosync_hybrid_snapshot.json",
    "autosync_inspector_full.json",
    "autosync_snapshot.json"
]
OUTPUT_JSON = "autosync_analysis.json"
PREV_JSON = "autosync_analysis_prev.json"
# ---------------------------------

def load_snapshot():
    for p in SNAPSHOT_CANDIDATES:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                try:
                    return json.load(f), p
                except Exception as e:
                    print(f"[warning] failed to parse {p}: {e}")
    raise FileNotFoundError("No snapshot JSON found. Place one of: " + ", ".join(SNAPSHOT_CANDIDATES))

def gather_metrics(snapshot):
    # Try multiple shapes
    metrics = {
        "total_files": 0,
        "total_gaps": 0,
        "total_parse_errors": 0,
        "total_read_errors": 0,
        "db_missing": 0,
        "db_errors": 0,
        "modules_present": []
    }

    # 1) If snapshot has overall_summary, use it (preferred)
    overall = snapshot.get("overall_summary") or snapshot.get("summary") or {}
    if overall:
        # safe copy with defaults
        metrics["total_files"] = int(overall.get("total_files", 0) or 0)
        metrics["total_gaps"] = int(overall.get("total_gaps", 0) or 0)
        metrics["total_parse_errors"] = int(overall.get("total_parse_errors", 0) or 0)
        metrics["total_read_errors"] = int(overall.get("total_read_errors", 0) or 0)
    # 2) If modules present, aggregate
    modules = snapshot.get("modules") or snapshot.get("modules_info") or snapshot.get("modules_info_by_folder") or {}
    if modules:
        metrics["modules_present"] = list(modules.keys())
        # aggregate if module summaries present
        for mname, mdata in modules.items():
            ms = mdata.get("summary") or {}
            metrics["total_files"] += int(ms.get("total_files", 0) or 0)
            metrics["total_gaps"] += int(ms.get("total_gaps", 0) or 0)
            metrics["total_parse_errors"] += int(ms.get("total_parse_errors", 0) or 0)
            metrics["total_read_errors"] += int(ms.get("total_read_errors", 0) or 0)
            # detect DB issues per module (if recorded)
            if isinstance(ms.get("actions_needed"), list) and "db_missing" in ms.get("actions_needed"):
                metrics["db_missing"] += 1
    # 3) fallback: try to parse modules/*/files entries for gaps
    if not modules:
        # some snapshots store modules at top-level e.g. core/tools/test_patch
        for key in ["core", "tools", "test_patch"]:
            m = snapshot.get(key, {})
            files_status = m.get("files_status") or (m.get("files") and {p:info.get("status","exists") for p,info in m.get("files",{}).items()})
            if files_status:
                metrics["modules_present"].append(key)
                metrics["total_files"] += len(files_status)
                # count parse/read keyed into dependencies or status
                for path, status in files_status.items():
                    # status might be "exists" or include strings like "parse_error"
                    if isinstance(status, str) and "parse_error" in status:
                        metrics["total_parse_errors"] += 1
                        metrics["total_gaps"] += 1
                    if isinstance(status, str) and "read_error" in status:
                        metrics["total_read_errors"] += 1
                        metrics["total_gaps"] += 1
    # 4) DB detection: look for explicit DB files
    # search snapshot entries for db_missing or db_summary errors
    if isinstance(snapshot, dict):
        # deep scan for db errors
        def deep_scan(obj):
            if isinstance(obj, dict):
                for k,v in obj.items():
                    if isinstance(k, str) and ("db" in k.lower() or "sqlite" in k.lower()):
                        if v is None:
                            metrics["db_missing"] += 1
                    deep_scan(v)
            elif isinstance(obj, list):
                for item in obj:
                    deep_scan(item)
        deep_scan(snapshot)
    return metrics

def decide_phase(metrics):
    """
    Returns detected_phase, explanation, and confidence [0..1]
    Phases: init_scan, fix_configs, patch_batch, db_migration, run_tests, stable_monitor
    """
    # heuristic rules
    if metrics["total_files"] == 0:
        return "init_scan", "اسکن اولیه یافت نشد یا فایل‌ها صفر است.", 0.95
    if metrics["db_missing"] > 0:
        return "db_migration", "پایگاه داده محلی موجود نیست یا گزارشی از خطای DB داریم.", 0.9
    if metrics["total_gaps"] > 0:
        # if gaps are parse/read heavy => fix configs, else patch
        if metrics["total_parse_errors"] + metrics["total_read_errors"] >= max(1, metrics["total_gaps"]/1.5):
            return "fix_configs", "خطاهای parse/read تشخیص داده شده‌اند؛ ابتدا پیکربندی/کد را اصلاح کنید.", 0.8
        else:
            return "patch_batch", "موارد گمشده یا GAP وجود دارد؛ اجرای دسته پچ‌ها پیشنهاد می‌شود.", 0.75
    # otherwise ready for tests or stable monitoring
    # prefer run_tests when there are modules present
    if metrics["modules_present"]:
        return "run_tests", "ساختار موجود است؛ اجرای تست‌ها و بررسی KPIها پیشنهاد می‌شود.", 0.85
    return "stable_monitor", "حالت پایدار؛ نظارت و جمع‌آوری KPI.", 0.7

def score_action(base):
    """
    base: dict with base Impact, Effort, Risk estimates (1-5)
    Add Confidence (derived) and compute weighted_score = (Impact*0.4 + Confidence*0.3) / (Effort*0.2 + Risk*0.1)
    Return numeric values and keep 1..5 ranges for ICER.
    """
    impact = base.get("Impact", 3)
    effort = base.get("Effort", 3)
    risk = base.get("Risk", 3)
    confidence = base.get("Confidence", 0.7)  # 0..1
    # scale confidence to 1..5 for display
    conf_scale = max(1, min(5, round(confidence*5)))
    weighted = (impact*0.4 + conf_scale*0.3) / (max(0.1, effort*0.2 + risk*0.1))
    return {
        "Impact": impact,
        "Confidence": round(confidence, 2),
        "Confidence_scale": conf_scale,
        "Effort": effort,
        "Risk": risk,
        "weighted_score": round(weighted, 3)
    }

def build_actions(detected_phase, metrics):
    actions = []
    # definitions of candidate actions with base heuristics
    # Impact, Effort, Risk baseline (1-5)
    catalog = {
        "init_scan": {
            "action": "init_scan_verify_paths",
            "title": "اجرای اسکن اولیه و تایید مسیرها",
            "desc": "ریپو و مسیرها را بررسی و snapshot اولیه تولید کنید.",
            "base": {"Impact":5, "Effort":1, "Risk":1, "Confidence":0.95}
        },
        "db_migration": {
            "action": "prepare_db_and_migrate_snapshots",
            "title": "ایجاد/برقراری پایگاه داده محلی و مهاجرت snapshots",
            "desc": "ایجاد autosync_db.sqlite و انتقال JSON snapshots به جدول 'snapshots'.",
            "base": {"Impact":5, "Effort":3, "Risk":2, "Confidence":0.8}
        },
        "fix_configs": {
            "action": "fix_parse_and_read_errors",
            "title": "رفع خطاهای parse/read در فایل‌های پیکربندی و کد",
            "desc": "اصلاح JSON/YAML یا کدهای دارای خطا و اجرای مجدد اسکن.",
            "base": {"Impact":5, "Effort":3, "Risk":2, "Confidence":0.7}
        },
        "patch_batch": {
            "action": "execute_patch_batch",
            "title": "اجرای Patch Batch و اعمال اصلاحات",
            "desc": "اعمال مجموعه پچ‌ها در sandbox یا staging و ثبت نتایج.",
            "base": {"Impact":4, "Effort":2, "Risk":3, "Confidence":0.75}
        },
        "run_tests": {
            "action": "execute_test_suite",
            "title": "اجرای Test Suite (واحد و integration)",
            "desc": "اجرای تست‌ها و ثبت نتایج در DB برای تحلیل KPI.",
            "base": {"Impact":5, "Effort":2, "Risk":2, "Confidence":0.85}
        },
        "stable_monitor": {
            "action": "start_monitoring_and_collect_kpis",
            "title": "شروع نظارت و جمع‌آوری KPI",
            "desc": "راه‌اندازی collection و داشبورد برای KPIها و اعلان‌ها.",
            "base": {"Impact":4, "Effort":1, "Risk":1, "Confidence":0.8}
        }
    }
    # Primary recommended action
    primary = catalog.get(detected_phase)
    if primary:
        primary_score = score_action({**primary["base"], "Confidence": primary["base"]["Confidence"]})
        actions.append({
            "module": "core" if detected_phase in ["init_scan","db_migration","fix_configs","patch_batch"] else "test_patch",
            "action": primary["action"],
            "title": primary["title"],
            "description": primary["desc"],
            "reason": f"Detected phase = {detected_phase}",
            "metrics": primary_score
        })
    # Add complementary actions
    if detected_phase == "run_tests":
        # also suggest creating DB backup and enabling CI if not present
        db_action = catalog["stable_monitor"]
        db_score = score_action({**db_action["base"], "Confidence":0.7})
        actions.append({
            "module": "tools",
            "action": db_action["action"],
            "title": db_action["title"],
            "description": "پیشنهاد: قبل از اجرای گسترده تست‌ها، پایگاه داده بکاپ گرفته شود و CI فعال شود.",
            "reason": "Pre-test safety and monitoring",
            "metrics": db_score
        })
    return actions

def compare_with_previous(prev_path, current):
    if not os.path.exists(prev_path):
        return {"found_previous": False}
    try:
        with open(prev_path, "r", encoding="utf-8") as f:
            prev = json.load(f)
    except Exception as e:
        return {"found_previous": True, "error": str(e)}
    diffs = {}
    # compare detected_phase and top-level numbers
    if prev.get("detected_phase") != current.get("detected_phase"):
        diffs["detected_phase_changed"] = {"from": prev.get("detected_phase"), "to": current.get("detected_phase")}
    # compare overall_summary numbers
    prev_sum = prev.get("metrics", {})
    curr_sum = current.get("metrics", {})
    for k in ["total_files","total_gaps","total_parse_errors","total_read_errors","db_missing"]:
        if prev_sum.get(k) != curr_sum.get(k):
            diffs.setdefault("metrics_changed", {})[k] = {"from": prev_sum.get(k), "to": curr_sum.get(k)}
    return {"found_previous": True, "diffs": diffs}

def main():
    snapshot, path = load_snapshot()
    metrics = gather_metrics(snapshot)
    detected_phase, explanation, phase_conf = decide_phase(metrics)
    # build recommended actions
    actions = build_actions(detected_phase, metrics)
    # compute overall confidence and risk heuristics
    confidence = phase_conf
    # risk level based on gaps and db issues
    risk_val = 0
    if metrics["total_gaps"] > 0:
        risk_val += min(5, int(metrics["total_gaps"] / max(1, metrics["total_files"]) * 10))
    if metrics["db_missing"] > 0:
        risk_val = max(risk_val, 4)
    risk_level = "low"
    if risk_val >= 4:
        risk_level = "high"
    elif risk_val >=2:
        risk_level = "medium"
    # compose analysis
    analysis = {
        "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        "snapshot_source": path,
        "metrics": metrics,
        "detected_phase": detected_phase,
        "phase_explanation": explanation,
        "confidence": round(confidence, 2),
        "risk_level": risk_level,
        "next_actions": actions
    }
    # compare with previous analysis if exists
    prev_compare = compare_with_previous(PREV_JSON, analysis)
    analysis["previous_analysis_comparison"] = prev_compare
    # write output and rotate prev
    if os.path.exists(OUTPUT_JSON):
        # move to prev
        os.replace(OUTPUT_JSON, PREV_JSON)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"Analysis saved to {OUTPUT_JSON}")
    # print compact summary to user
    print(json.dumps({
        "detected_phase": detected_phase,
        "reason": explanation,
        "next_action_titles": [a["title"] for a in actions],
        "confidence": analysis["confidence"],
        "risk_level": analysis["risk_level"]
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
