# core/secrets_manager.py
import json

def get_secret(key, file_path="../connectors/connectors_config.json"):
    with open(file_path, "r") as f:
        secrets = json.load(f)
    return secrets.get(key)
