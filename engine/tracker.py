import json
from pathlib import Path
from datetime import datetime
from database.repository import Repository

class Tracker:
    def __init__(self):
        self.repo = Repository()

    def log_completed(self, email, url, task_type, status):
        completed = self.repo.load_completed()
        if email not in completed:
            completed[email] = []
        if url not in completed[email]:
            completed[email].append(url)
        self.repo.save_completed(completed)

        # Log histórico adicional se quiser (expanda history.json se necessário)