# 🧩 AutoSync System Structure

## 🎯 هدف
تعریف ساختار معماری و وابستگی‌های ماژول‌های سیستم AutoSync برای حفظ انسجام بین کد، تست، تحلیل، و گزارش.

---

## 🔧 ساختار منطقی (Logical Architecture)

| لایه | وظیفه | ماژول‌ها | نوع ارتباط |
|------|--------|------------|-------------|
| Core | هماهنگی مرکزی و کنترل خطا | auto_sync_core.py, db_manager.py | داخلی (Sync Queue) |
| Connectors | ارتباط با پلتفرم‌های خارجی | github_sync.py, secrets_manager.py | API External |
| Testing | تست واحد و یکپارچه | test_suite.py, patch_batch_runner.py | Core → Test |
| Analytics | تحلیل داده و بازخورد | trend_analytics.py, continuous_improvement.py | Test → Analytics |
| Dashboard | نمایش KPI و وضعیت زنده | dashboard_main.py, kpi_graphs.js | Analytics → Dashboard |

---

## 🧱 وابستگی‌های ماژول‌ها

Core
├── Connectors
│ ├── GitHub Sync
│ ├── CI/CD Trigger
│ └── Secrets Manager
├── Testing
│ ├── Test Suite
│ └── Patch Runner
├── Analytics
│ ├── Trend Detection
│ └── Continuous Improvement
└── Dashboard
├── KPI Metrics
└── Feedback Viewer

yaml
Copy code

---

## 🧠 رفتار سیستمی (System Behavior)

| وضعیت | عمل | Trigger | نتیجه |
|--------|------|----------|--------|
| Commit جدید | `auto_sync_core` اجرا | GitHub Webhook | تست و تحلیل خودکار |
| Test Failure | ذخیره snapshot | Core Internal | بازگردانی وضعیت قبلی |
| KPI انحراف | گزارش در Dashboard | Analytics Event | ایجاد پیشنهاد بهبود |
| پایدار شدن سیستم | Push خودکار CI/CD | Feedback Validation | انتشار نسخه جدید |

---

## 🧩 نکات طراحی

- تمام داده‌ها باید از طریق `core_config.json` مدیریت شوند.
- Queue داخلی با Lock فایل انجام می‌شود (محدود به ۱ فرآیند همزمان).
- ماژول‌ها قابل افزوده‌شدن بدون تغییر در Core هستند (Plug-in Architecture).
- هر ماژول در اجرای `--verify` خود باید تست مستقل داشته باشد.