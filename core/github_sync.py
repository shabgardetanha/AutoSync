import subprocess

class GitHubSync:
    def __init__(self, config):
        self.repo = config['repo']
        self.token = config['token']
        self.branch = config['branch']

    def push(self):
        # ذخیره داده‌ها در فایل temp و Push به GitHub
        with open('temp_push.json', 'w') as f:
            f.write(data)

        subprocess.run([
            "git", "add", "."
        ])
        subprocess.run([
            "git", "commit", "-m", "AutoSync Commit"
        ])
        subprocess.run([
            "git", "push", "origin", self.branch
        ])
