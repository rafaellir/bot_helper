import json
from pathlib import Path
import logging

TASKS_PATH = Path("data/tasks.json")
COMPLETED_PATH = Path("data/completed.json")
ACCOUNTS_PATH = Path("data/accounts.json")

class Repository:
    def __init__(self):
        for path in [TASKS_PATH, COMPLETED_PATH, ACCOUNTS_PATH]:
            path.parent.mkdir(exist_ok=True)
            if not path.exists():
                if path == COMPLETED_PATH:
                    path.write_text("{}", encoding="utf-8")
                else:
                    path.write_text("[]", encoding="utf-8")

    def load_tasks(self):
        try:
            content = TASKS_PATH.read_text(encoding="utf-8").strip()
            if not content:
                content = "[]"
            return json.loads(content)
        except json.JSONDecodeError as e:
            logging.error(f"❌ ERRO GRAVE: data/tasks.json está inválido!")
            logging.error(f"   Linha {e.lineno}, coluna {e.colno}")
            logging.error("   Abra o arquivo e corrija (provavelmente aspas erradas ou quebra de linha).")
            raise
        except Exception as e:
            logging.error(f"Erro ao ler tasks.json: {e}")
            raise

    def load_completed(self):
        try:
            return json.loads(COMPLETED_PATH.read_text(encoding="utf-8"))
        except:
            return {}

    def save_completed(self, data):
        COMPLETED_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def load_accounts(self):
        return json.loads(ACCOUNTS_PATH.read_text(encoding="utf-8"))

    def save_accounts(self, data):
        ACCOUNTS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")