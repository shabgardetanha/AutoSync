import json
import requests

class Notifications:
    def __init__(self, config_file='connectors/connectors_config.json'):
        with open(config_file) as f:
            self.config = json.load(f)

    def send_slack(self, message):
        requests.post(self.config['slack_webhook'], json={"text": message})
