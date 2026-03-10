import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from browser.session import BrowserSession
from engine.advisor import Advisor
from database.repository import Repository
from infra.tracker import Tracker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

BATCH_SIZE = 5


def run_leitura_task(browser, task):

    page = browser.new_page()

    try:

        advisor = Advisor(page)

        page.goto(task["url"], timeout=60000)
        page.wait_for_load_state("networkidle")

        advisor.process_task(task)

        return True

    except Exception as e:

        logging.error(f"Erro na leitura {task['url']}: {e}")

        return False

    finally:

        page.close()


def main():

    logging.info("Iniciando bot...")

    repo = Repository()
    tracker = Tracker()

    browser_session = BrowserSession()

    main_page = browser_session.get_page()

    advisor = Advisor(main_page)

    tasks = repo.load_tasks()
    completed = repo.load_completed()

    email = "default"

    done_for_account = completed.get(email, [])

    leitura_tasks = []
    outras_tasks = []

    for task in tasks:

        if task["url"] in done_for_account:
            continue

        if task["type"] == "leitura":
            leitura_tasks.append(task)
        else:
            outras_tasks.append(task)

    logging.info(f"{len(leitura_tasks)} leituras encontradas")
    logging.info(f"{len(outras_tasks)} outras tarefas encontradas")

    # -----------------------------
    # LEITURAS EM PARALELO
    # -----------------------------

    for i in range(0, len(leitura_tasks), BATCH_SIZE):

        batch = leitura_tasks[i:i + BATCH_SIZE]

        logging.info(f"Executando batch de leituras ({len(batch)})")

        with ThreadPoolExecutor(max_workers=len(batch)) as executor:

            futures = [
                executor.submit(run_leitura_task, browser_session, task)
                for task in batch
            ]

            for future, task in zip(as_completed(futures), batch):

                result = future.result()

                if result:

                    done_for_account.append(task["url"])

                    completed[email] = done_for_account

                    repo.save_completed(completed)

                    tracker.log_completed(
                        email,
                        task["url"],
                        task["type"],
                        "completada"
                    )

                    logging.info(f"Leitura concluída: {task['url']}")

                else:

                    logging.warning(f"Falha na leitura: {task['url']}")

    # -----------------------------
    # OBJETIVA + DISCURSIVA
    # -----------------------------

    logging.info("Iniciando tarefas objetivas e discursivas...")

    for task in outras_tasks:

        url = task["url"]

        try:

            logging.info(f"Abrindo tarefa: {url}")

            main_page.goto(url, timeout=60000)
            main_page.wait_for_load_state("networkidle")

            advisor.process_task(task)

            done_for_account.append(url)

            completed[email] = done_for_account

            repo.save_completed(completed)

            tracker.log_completed(
                email,
                url,
                task["type"],
                "completada"
            )

            logging.info(f"Tarefa concluída: {url}")

        except Exception as e:

            logging.error(f"Erro na tarefa {url}: {e}")

    logging.info("Todas tarefas finalizadas")

    browser_session.close()


if __name__ == "__main__":
    main()
