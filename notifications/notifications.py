import json
import requests
from connectors.secrets_manager import get_secret

class Notifications:
    def __init__(self, config_file='connectors/connectors_config.json'):
        with open(config_file) as f:
            self.config = json.load(f)


def send_slack_message(message):
    webhook = get_secret("SLACK_WEBHOOK")
    print(f"Sending Slack message: {message}")
    # requests.post(webhook, json={"text": message})  # Uncomment in real use