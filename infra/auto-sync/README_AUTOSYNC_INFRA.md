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
