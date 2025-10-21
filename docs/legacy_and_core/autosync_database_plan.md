## 📒 4. `autosync_database_plan.md`

```markdown
# 🗃️ AutoSync Database & Storage Plan

## 🎯 هدف
مدیریت داده‌ها، snapshots و نتایج تست‌ها با ساختار DB/JSON Hybrid جهت سرعت و شفافیت.

---

## 🧩 ساختار داده‌ها

| نوع داده | قالب | مسیر ذخیره | توضیح |
|-----------|--------|--------------|--------|
| Configuration | JSON | ./core/core_config.json | تنظیمات مرکزی |
| Test Results | JSON | ./analytics_feedback/test_results.json | خروجی تست‌ها |
| Snapshots | JSON | ./test_patch/snapshots/ | بک‌آپ لحظه‌ای |
| Analytics | SQLite | ./analytics_feedback/auto_analytics.db | تحلیل‌های طولی |
| Feedback | JSON | ./analytics_feedback/feedback_loop.json | بازخوردها |
| Logs | Text | ./logs/autosync.log | رویدادها و خطاها |

---

## 🧱 طرح پایگاه‌داده SQLite

```sql
CREATE TABLE feedback (
  id TEXT PRIMARY KEY,
  source TEXT,
  recommendation TEXT,
  impact INTEGER,
  confidence INTEGER,
  effort INTEGER,
  risk INTEGER,
  created_at TEXT
);

CREATE TABLE trends (
  id TEXT PRIMARY KEY,
  metric_name TEXT,
  metric_value REAL,
  change_rate REAL,
  recorded_at TEXT
);
🧠 بهینه‌سازی‌ها
استفاده از Write-Ahead Logging (WAL) برای سرعت بیشتر

ایندکس بر اساس impact و risk برای تحلیل سریع‌تر

فشرده‌سازی JSON در snapshotها با gzip

yaml
Copy code

---