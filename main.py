import time
from browser.session import BrowserSession
from browser.login import LoginManager
from browser.navigation import NavigationManager
from database.repository import Repository
from engine.matcher import Matcher
from engine.advisor import Advisor
from engine.tracker import Tracker
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    repo = Repository()
    matcher = Matcher()
    tracker = Tracker()

    accounts = repo.load_accounts()
    while accounts:
        account = accounts[0]
        email = account["email"]
        password = account["password"]

        browser = BrowserSession()
        page = browser.get_page()
        login_manager = LoginManager(page)

        try:
            login_manager.login_atlas(email, password)
        except Exception as e:
            logging.error(f"Falha login {email}: {e}")
            browser.close()
            accounts.pop(0)
            repo.save_accounts(accounts)
            continue

        # NAVEGAÇÃO
        nav_manager = NavigationManager(page)
        try:
            plurall_page = nav_manager.navigate_to_plurall_activities()
            logging.info("✅ Navegação concluída - iniciando processamento de tarefas...")
        except Exception as e:
            logging.error(f"Falha navegação {email}: {e}")
            browser.close()
            accounts.pop(0)
            repo.save_accounts(accounts)
            continue

        # === PROCESSAMENTO DAS TAREFAS ===
        advisor = Advisor(plurall_page)
        tasks = repo.load_tasks()
        completed = repo.load_completed().get(email, [])

        logging.info(f"Iniciando loop de tarefas - {len(tasks)} tarefas no total, {len(completed)} já feitas")

        for task in tasks:
            url = task["url"]
            if url in completed:
                logging.info(f"⏭️ Pulando (já feita): {url}")
                continue

            logging.info(f"🚀 Abrindo tarefa: {url}")
            plurall_page.goto(url, timeout=60000)
            plurall_page.wait_for_load_state("networkidle", timeout=60000)

            advisor.process_task(task)
            tracker.log_completed(email, url, task["type"], "completada")
            logging.info(f"✅ Tarefa concluída: {url}")

        browser.close()
        accounts.pop(0)
        repo.save_accounts(accounts)
        logging.info(f"✅ Conta {email} finalizada!")
        time.sleep(5)

    print("🎉 Missão cumprida: Todas contas e tarefas processadas!")

if __name__ == "__main__":
    main()