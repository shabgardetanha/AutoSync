import json

class CoreConfig:
    @staticmethod
    def load(path="core/core_config.json"):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
