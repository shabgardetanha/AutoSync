# AutoSync Infra — Quickstart

## پیش‌نیازها
- GitHub repo access
- Kubernetes cluster (for ArgoCD)
- Secrets configured in GitHub: KUBE_CONFIG, FLYWAY_URL, FLYWAY_USER, FLYWAY_PASSWORD, FEATURE_FLAG_SDK_KEY

## نصب ArgoCD (مثال)
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

## Deploy ArgoCD App
kubectl apply -f infra/auto-sync/argocd/app-autosync.yaml

## اجرای Flyway (local / CI)
docker run --rm -v ${PWD}/infra/auto-sync/flyway:/flyway/sql flyway/flyway:latest -url=${FLYWAY_URL} -user=${FLYWAY_USER} -password=${FLYWAY_PASSWORD} migrate

## GitHub Actions
- فایل `autosync_pipeline.yml` را در repo قرار بده. به ازای هر push به main snapshot → analysis اجرا خواهد شد.

## Feature Flags
- نمونه تنظیمات در `feature_flags/featureflags.sample.yml`.
- برای اجرای Autodeploy از طریق flag، `FEATURE_FLAG_SDK_KEY` را در secrets قرار ده.

## Monitoring
- Prometheus scrape config را به Prometheus اضافه کن.
- Grafana dashboard را import کن و metric names را طبق exporter تنظیم کن.





# AutoSync Canary Rollout / Feature Flag

## ساختار
- `features/` : تعریف Feature Flags
- `pipelines/` : GitHub Actions یا Argo workflows
- `scripts/` : تغییر درصد rollout و مانیتور Metrics
- `staging/` : تست Feature Flag
- `production/` : rollout واقعی

## نحوه اجرا
1. Feature Flag را در `features/autodeploy.json` بررسی کن.
2. Pipeline را با `workflow_dispatch` اجرا کن.
3. Scripts اتوماتیک rollout و مانیتور را اجرا می‌کنند.
4. Analyzer می‌تواند تصمیمات خودکار را بر اساس burn-rate و KPI بگیرد.

## Rollback
- هر زمان burn-rate > threshold یا خطای critical:
./flag_update.sh autodeploy 0 production

✅ نکات اجرایی
همه فایل‌ها نسخه‌بندی در Git → rollback سریع و trace کامل

Analyzer باید فایل‌های staging و production را بخواند و decision trigger کند

Scripts باید idempotent باشند → چند بار اجرا خرابکاری نکنند