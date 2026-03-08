import time
import logging
from browser.actions import BrowserActions
from engine.ai_rewriter import AIRewriter

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Advisor:

    def __init__(self, page):
        self.page = page
        self.actions = BrowserActions(page)
        self.ai = AIRewriter()

    def process_task(self, task):

        task_type = task["type"]
        answer = task.get("answer")

        logging.info(f"📌 Processando tarefa {task_type} → {task['url']}")

        try:

            if task_type == "leitura":

                self.actions.handle_leitura()


            elif task_type == "objetiva":

                result = self.actions.handle_objetiva(answer)

                if not result:
                    logging.warning("⚠️ Falha ao marcar alternativa")


            elif task_type == "discursiva":

                if answer:

                    logging.info("🤖 Reescrevendo resposta com IA...")

                    answer = self.ai.rewrite(answer)

                self.actions.handle_discursiva(answer)


            else:

                logging.warning(f"⚠️ Tipo desconhecido: {task_type}")

        except Exception as e:

            logging.error(f"❌ Erro ao processar {task_type}: {str(e)}")

        # pausa mínima apenas para evitar travamento da interface
        time.sleep(1)