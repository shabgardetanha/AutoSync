
# مثال ساده استفاده از feature flag (کتابخانه فرضی)
import os

FEATURE_FLAG_SDK_KEY = os.getenv("FEATURE_FLAG_SDK_KEY", "local-mode")
# فرض: اگر از LaunchDarkly استفاده می‌کنید، از ldclient استفاده کنید
try:
    from ldclient import LDClient, Config
    client = LDClient(Config(FEATURE_FLAG_SDK_KEY))
    user = {"key":"autosync-runner"}
    autodeploy = client.variation("autodeploy_enabled", user, False)
    if autodeploy:
        print("Autodeploy فعال است — ادامه اتوماتیک")
    else:
        print("Autodeploy غیر فعال — نیاز به تایید انسانی")
except Exception:
    # fallback local config
    print("FeatureFlag client not available — fallback to env")
    if os.getenv("AUTODEPLOY", "false").lower()=="true":
        print("Autodeploy فعال (env)")
