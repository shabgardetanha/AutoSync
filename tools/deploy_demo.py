import shutil
import os

DEMO_FOLDER = "demo_project"
TARGET_FOLDER = "demo_output"

def deploy_demo():
    if os.path.exists(TARGET_FOLDER):
        shutil.rmtree(TARGET_FOLDER)
    shutil.copytree(DEMO_FOLDER, TARGET_FOLDER)
    print(f"Demo project deployed to {TARGET_FOLDER}")

if __name__ == "__main__":
    deploy_demo()
