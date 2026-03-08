import time
from playwright.sync_api import Page, TimeoutError
import yaml
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

config = yaml.safe_load(open("config.yaml"))

class NavigationManager:
    def __init__(self, page: Page):
        self.page = page
        self.context = page.context
        self.plurall_page = None

    def navigate_to_plurall_activities(self):
        try:
            # Plurall na home
            plurall_locator = self.page.get_by_text("Plurall").filter(visible=True).first
            plurall_locator.wait_for(state="visible", timeout=60000)
            plurall_locator.click(timeout=60000)
            logging.info("Clicado em 'Plurall'")

            time.sleep(3)

            # Acessar Plurall Web
            self.page.wait_for_selector("text=Acessar Plurall Web", state="visible", timeout=60000)
            with self.context.expect_page(timeout=120000) as page_info:
                self.page.click("text=Acessar Plurall Web", timeout=60000)
                logging.info("Clicado em 'Acessar Plurall Web' → nova aba")

            self.plurall_page = page_info.value
            self.plurall_page.bring_to_front()

            self.plurall_page.wait_for_load_state("domcontentloaded", timeout=90000)
            time.sleep(10)
            logging.info(f"✅ Plurall aberto: {self.plurall_page.url}")

            # Dentro do Plurall
            self.plurall_page.wait_for_selector("text=Atividades", state="visible", timeout=60000)
            self.plurall_page.click("text=Atividades", timeout=60000)
            logging.info("Clicado em 'Atividades'")

            time.sleep(3)

            self.plurall_page.wait_for_selector("text=Formação geral - Caderno 5", state="visible", timeout=60000)
            self.plurall_page.click("text=Formação geral - Caderno 5", timeout=60000)
            logging.info("Clicado em 'Formação geral - Caderno 5'")

            time.sleep(3)

            self.plurall_page.wait_for_selector("text=Acessar", state="visible", timeout=60000)
            self.plurall_page.click("text=Acessar", timeout=60000)
            logging.info("Clicado em 'Acessar' → lista de tarefas")

            self.plurall_page.wait_for_load_state("domcontentloaded", timeout=60000)
            time.sleep(10)
            logging.info("✅ Lista de atividades carregada! Iniciando tarefas...")

        except Exception as e:
            logging.error(f"Erro na navegação: {str(e)}")
            raise

        return self.plurall_page