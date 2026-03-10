# browser/session.py
from playwright.sync_api import sync_playwright
import yaml
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
config = yaml.safe_load(open("config.yaml"))

class BrowserSession:
    def __init__(self):
        self.playwright = sync_playwright().start()
        # Launch com anti-detecção
        self.browser = self.playwright.chromium.launch(
            channel="chrome",
            headless=config["browser"]["headless"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--start-maximized",
                "--disable-extensions",
            ],
            slow_mo=1000
        )
        # Context com fingerprint humano
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
            color_scheme="light",
            accept_downloads=True,
            ignore_https_errors=True
        )
        # Página principal (a que você já usa)
        self.page = self.context.new_page()
        logging.info("Nova sessão de browser iniciada com anti-detecção.")

    def get_page(self):
        return self.page

    # NOVO: cria uma nova aba (mesmo contexto, reaproveita sessão/cookies)
    def new_page(self):
        return self.context.new_page()

    # NOVO: fecha uma página criada dinamicamente
    def close_page(self, page):
        try:
            page.close()
        except Exception as e:
            logging.debug(f"Erro ao fechar page: {e}")

    def close(self):
        try:
            self.context.close()
            self.browser.close()
            self.playwright.stop()
            logging.info("Sessão de browser fechada com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao fechar sessão: {str(e)}")
