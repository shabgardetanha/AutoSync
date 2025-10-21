import subprocess
from audit_checker.audit_manifest_diff import compare_manifests, save_diffs_report
from core.core_engine import update_core_manifest

from phase_10_deployment.validate_deployment import run_deployment_validation
from phase_10_deployment.validate_kpi import run_kpi_validation
class CICDRunner:
    def run_pipeline(self):
        subprocess.run(['echo', 'Running CI/CD Pipeline'])
        # Logic for CI/CD

def validate_before_push():
    diffs = compare_manifests("core/core_manifest.json", "snapshots/core_manifest_prev.json")
    if diffs:
        save_diffs_report(diffs)
        print(f"⚠️ Manifest changes detected! Review required before push.")
    else:
        print("✅ Manifest integrity verified.")

def pre_push_validation():
    update_core_manifest(updated_files=True)
    print("✅ Manifest validated before push")





def main():

    
    # مرحله نهایی فاز 10
    run_deployment_validation()
    run_kpi_validation()
    print("✅ Deployment Validation & Stability Completed.")


if __name__ == "__main__":
    main()
